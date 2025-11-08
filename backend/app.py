from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import os
import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer, CrossEncoder
from rapidfuzz import process, fuzz
from functools import lru_cache
from rank_bm25 import BM25Plus

# ======================================================
# CONFIGURATION
# ======================================================
MODEL_NAME = "paraphrase-multilingual-mpnet-base-v2"
# Using fine-tuned cross-encoder trained on K-drama data
CROSS_ENCODER_MODEL = r"D:\Projects\SeoulMate\model_traning\models\cross-enc-excellent"
MODEL_DIR = r"D:\Projects\SeoulMate\model_traning\models"
INDEX_DIR = r"D:\Projects\SeoulMate\model_traning\faiss_index"

# ======================================================
# FASTAPI SETUP
# ======================================================
app = FastAPI(title="Kdrama Hybrid Recommendation API", version="3.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======================================================
# STAGE 1 — LOAD MODELS & INDEXES
# ======================================================
print("Stage 1: Loading models and FAISS index...")

# Try to load fine-tuned SBERT first, fallback to pretrained
finetuned_models = (
    [
        d
        for d in os.listdir(MODEL_DIR)
        if os.path.isdir(os.path.join(MODEL_DIR, d)) and d.startswith("sbert-finetuned")
    ]
    if os.path.exists(MODEL_DIR)
    else []
)

if finetuned_models:
    model_path = os.path.join(MODEL_DIR, finetuned_models[0])
    print(f"Loading fine-tuned SBERT from: {model_path}")
    model = SentenceTransformer(model_path)
else:
    print(f"No fine-tuned model found, using pretrained: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME, cache_folder=MODEL_DIR)

index = faiss.read_index(os.path.join(INDEX_DIR, "index.faiss"))

with open(os.path.join(INDEX_DIR, "meta.pkl"), "rb") as f:
    metadata = pickle.load(f)

titles = [m["Title"] for m in metadata]
corpus = [
    f"{m.get('Title', '')} {m.get('Genre', '')} {m.get('Description', '')} {m.get('Cast', '')}"
    for m in metadata
]
# Using BM25Plus for better performance (improved IDF handling)
bm25 = BM25Plus([doc.split() for doc in corpus])

print(f"Loaded {len(metadata)} dramas successfully.")

# ======================================================
# STAGE 2 — LOAD OPTIONAL RERANKER
# ======================================================
try:
    print("Stage 2: Loading cross-encoder reranker...")
    reranker = CrossEncoder(CROSS_ENCODER_MODEL)
    use_reranker = True
    print("Cross-encoder reranker loaded successfully.")
except Exception as e:
    reranker = None
    use_reranker = False
    print(f"Warning: Could not load reranker ({e}). Continuing without it.")


# ======================================================
# STAGE 3 — HELPER FUNCTIONS
# ======================================================
def fuzzy_match_title(user_input: str, threshold=70):
    """Handle typos and near matches using fuzzy logic."""
    match, score, _ = process.extractOne(user_input, titles, scorer=fuzz.WRatio)
    if score >= threshold:
        return match, score
    return None, score


@lru_cache(maxsize=128)
def cached_encode(text: str):
    """Cached embedding generation for speed."""
    emb = model.encode([text], convert_to_numpy=True)
    faiss.normalize_L2(emb)
    return emb


# ======================================================
# STAGE 4 — HYBRID RECOMMENDATION PIPELINE
# ======================================================
def recommend(
    title: str,
    top_n=5,
    alpha=0.7,
    genre=None,
    director=None,
    publisher=None,
    top_rated=False,
    description=None,
    rating_value=None,
    rating_count=None,
    keywords=None,
    screenwriters=None,
    sort_by=None,
    sort_order="desc",
    similar_to=None,
):
    """
    Stage-based pipeline:
    0. Apply filters to create filtered corpus (PRE-FILTERING)
    1. Resolve user input (fuzzy match or free-text)
    2. Semantic search (FAISS) on filtered corpus
    3. Lexical search (BM25) on filtered corpus
    4. Hybrid combination
    5. Optional reranking (Cross-Encoder)
    """

    # ---- Stage 4.0: PRE-FILTER the dataset ----
    filtered_metadata = metadata.copy()

    # Apply all filters to create a subset
    if genre:
        filtered_metadata = [
            r
            for r in filtered_metadata
            if genre.lower() in str(r.get("Genre", "")).lower()
            or genre.lower() in str(r.get("genres", "")).lower()
        ]
    if director:
        filtered_metadata = [
            r
            for r in filtered_metadata
            if director.lower() in str(r.get("Director", "")).lower()
            or director.lower() in str(r.get("directors", "")).lower()
        ]
    if publisher:
        filtered_metadata = [
            r
            for r in filtered_metadata
            if publisher.lower() in str(r.get("publisher", "")).lower()
        ]
    if description:
        filtered_metadata = [
            r
            for r in filtered_metadata
            if description.lower() in str(r.get("Description", "")).lower()
            or description.lower() in str(r.get("description", "")).lower()
        ]
    if rating_value:
        try:
            rating_value_val = float(rating_value)
            filtered_metadata = [
                r
                for r in filtered_metadata
                if float(r.get("rating_value", r.get("score", 0))) >= rating_value_val
            ]
        except Exception:
            pass
    if rating_count:
        try:
            rating_count_val = float(rating_count)
            filtered_metadata = [
                r
                for r in filtered_metadata
                if float(r.get("rating_count", 0)) >= rating_count_val
            ]
        except Exception:
            pass
    if keywords:
        filtered_metadata = [
            r
            for r in filtered_metadata
            if keywords.lower() in str(r.get("keywords", "")).lower()
        ]
    if screenwriters:
        filtered_metadata = [
            r
            for r in filtered_metadata
            if screenwriters.lower() in str(r.get("screenwriters", "")).lower()
        ]

    # If no results after filtering, return empty
    if not filtered_metadata:
        return {
            "query": {"Title": title},
            "filters": {
                "genre": genre,
                "director": director,
                "publisher": publisher,
                "top_rated": top_rated,
                "description": description,
                "rating_value": rating_value,
                "rating_count": rating_count,
                "keywords": keywords,
                "screenwriters": screenwriters,
                "sort_by": sort_by,
                "sort_order": sort_order,
                "similar_to": similar_to,
            },
            "recommendations": [],
            "message": "No dramas match your filters. Try broadening your search criteria.",
        }

    print(
        f"Filtered corpus: {len(filtered_metadata)} dramas (from {len(metadata)} total)"
    )

    # Create indices mapping for the filtered corpus
    title_to_original_idx = {m["Title"]: i for i, m in enumerate(metadata)}
    filtered_indices = [title_to_original_idx[m["Title"]] for m in filtered_metadata]

    # ---- Stage 4.1: Title resolution ----
    drama = next(
        (m for m in filtered_metadata if m["Title"].lower() == title.lower()), None
    )

    if not drama:
        # Try fuzzy match only within filtered corpus
        filtered_titles = [m["Title"] for m in filtered_metadata]
        if filtered_titles:
            match, score, _ = process.extractOne(
                title, filtered_titles, scorer=fuzz.WRatio
            )
            if match and score >= 70:
                drama = next(
                    (m for m in filtered_metadata if m["Title"] == match), None
                )
                print(
                    f"Fuzzy match: '{title}' -> '{match}' (confidence: {score:.1f}%)".encode(
                        "utf-8", errors="replace"
                    ).decode(
                        "utf-8"
                    )
                )
                query_text = f"{drama['Title']} {drama.get('Genre', '')} {drama.get('Description', '')} {drama.get('Cast', '')}"
            else:
                print(
                    f"No close match found for '{title}', treating as free-text query."
                )
                query_text = title
        else:
            query_text = title
    else:
        query_text = f"{drama['Title']} {drama.get('Genre', '')} {drama.get('Description', '')} {drama.get('Cast', '')}"

    # ---- Stage 4.2: FAISS Semantic Search on filtered corpus ----
    query_emb = cached_encode(query_text)
    # Search more broadly to ensure we get enough results
    search_k = min(len(filtered_metadata) + 50, len(metadata))
    D_all, I_all = index.search(query_emb, search_k)

    # Filter FAISS results to only include filtered_metadata indices
    faiss_results = [
        (metadata[idx], float(score))
        for idx, score in zip(I_all[0], D_all[0])
        if idx < len(metadata) and idx in filtered_indices
    ][
        : top_n + 20
    ]  # Take top results from filtered set

    # ---- Stage 4.3: BM25 Lexical Search on filtered corpus ----
    # Get BM25 scores for all dramas, then filter
    bm25_scores_all = bm25.get_scores(query_text.split())
    bm25_results = [
        (metadata[idx], float(bm25_scores_all[idx])) for idx in filtered_indices
    ]
    bm25_results = sorted(bm25_results, key=lambda x: x[1], reverse=True)[: top_n + 20]

    # ---- Stage 4.4: Combine Results ----
    combined_scores = {}
    max_bm25 = max([score for _, score in bm25_results]) if bm25_results else 1
    if max_bm25 == 0:
        max_bm25 = 1

    for rec, score in faiss_results:
        combined_scores[rec["Title"]] = alpha * score
    for rec, score in bm25_results:
        combined_scores[rec["Title"]] = combined_scores.get(rec["Title"], 0) + (
            1 - alpha
        ) * (score / max_bm25)

    # Sort by combined score (filters already applied in Stage 4.0)
    filtered = [
        next(m for m in filtered_metadata if m["Title"] == t)
        for t, _ in sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
    ]

    # Handle similar_to filter (requires FAISS search)
    if similar_to:
        # Find dramas similar to a given title within filtered metadata
        sim_drama = next(
            (m for m in filtered_metadata if m["Title"].lower() == similar_to.lower()),
            None,
        )
        if sim_drama:
            sim_query = f"{sim_drama['Title']} {sim_drama.get('Genre', '')} {sim_drama.get('Description', '')} {sim_drama.get('Cast', '')}"
            sim_emb = cached_encode(sim_query)
            D_sim, I_sim = index.search(sim_emb, len(filtered_metadata) + 20)
            # Only keep results that are in our filtered set
            sim_titles = [
                metadata[idx]["Title"]
                for idx in I_sim[0]
                if idx < len(metadata) and idx in filtered_indices
            ]
            filtered = [r for r in filtered if r["Title"] in sim_titles]

    # Sorting
    if sort_by:
        reverse = sort_order == "desc"
        filtered = sorted(
            filtered,
            key=lambda r: (
                float(r.get(sort_by, 0))
                if isinstance(r.get(sort_by, 0), (int, float, str))
                and str(r.get(sort_by, 0)).replace(".", "", 1).isdigit()
                else str(r.get(sort_by, ""))
            ),
            reverse=reverse,
        )
    elif top_rated:
        filtered = sorted(
            filtered,
            key=lambda r: float(r.get("rating_value", r.get("score", 0))),
            reverse=True,
        )
    top_results = filtered[:top_n]
    # ---- Stage 4.5: Optional Reranking ----
    if use_reranker and reranker:
        try:
            pairs = [[query_text, r["Description"]] for r in top_results]
            rerank_scores = reranker.predict(pairs)
            top_results = [
                r
                for _, r in sorted(
                    zip(rerank_scores, top_results), key=lambda x: x[0], reverse=True
                )
            ]
        except Exception as e:
            print(f"Reranking failed: {e}")

    return {
        "query": {"Title": title},
        "filters": {
            "genre": genre,
            "director": director,
            "publisher": publisher,
            "top_rated": top_rated,
            "description": description,
            "rating_value": rating_value,
            "rating_count": rating_count,
            "keywords": keywords,
            "screenwriters": screenwriters,
            "sort_by": sort_by,
            "sort_order": sort_order,
            "similar_to": similar_to,
        },
        "recommendations": top_results,
    }


# ======================================================
# STAGE 5 — API ROUTES
# ======================================================
@app.get("/")
def root():
    return {"message": "Hybrid Kdrama Recommendation API v3.1 is running"}


@app.get("/recommend")
def get_recommendations(
    title: str = Query(..., description="Kdrama title or user query"),
    top_n: int = Query(5, description="Number of recommendations"),
    genre: str = Query(None, description="Genre filter"),
    director: str = Query(None, description="Director filter"),
    publisher: str = Query(None, description="Publisher filter"),
    top_rated: bool = Query(False, description="Sort by top rating"),
    description: str = Query(None, description="Description keyword filter"),
    rating_value: float = Query(None, description="Minimum rating value"),
    rating_count: float = Query(None, description="Minimum rating count"),
    keywords: str = Query(None, description="Keywords filter"),
    screenwriters: str = Query(None, description="Screenwriters filter"),
    sort_by: str = Query(
        None,
        description="Sort by field (e.g., rating_value, popularity, date_published, episodes, duration)",
    ),
    sort_order: str = Query("desc", description="Sort order: asc or desc"),
    similar_to: str = Query(None, description="Find dramas similar to this title"),
):
    """Main recommendation endpoint with advanced filters and sorting."""
    return recommend(
        title,
        top_n,
        alpha=0.7,
        genre=genre,
        director=director,
        publisher=publisher,
        top_rated=top_rated,
        description=description,
        rating_value=rating_value,
        rating_count=rating_count,
        keywords=keywords,
        screenwriters=screenwriters,
        sort_by=sort_by,
        sort_order=sort_order,
        similar_to=similar_to,
    )


# ======================================================
# STAGE 6 — RUN LOCALLY
# ======================================================
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="127.0.0.1", port=8001, reload=True)
