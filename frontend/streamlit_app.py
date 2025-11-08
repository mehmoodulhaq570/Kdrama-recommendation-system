"""
SeoulMate - K-Drama Recommendation System
Streamlit Frontend

Run with: streamlit run frontend/streamlit_app.py
"""

import streamlit as st
import requests
import pandas as pd
from typing import List, Dict

# ======================================================
# CONFIG
# ======================================================
API_URL = "http://127.0.0.1:8001"

# ======================================================
# PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title="SeoulMate - K-Drama Recommendations",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ======================================================
# CUSTOM CSS
# ======================================================
st.markdown(
    """
<style>
    /* Main Header Styling */
    .main-header {
        font-size: 3.5rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .sub-header {
        text-align: center;
        color: #6c757d;
        font-size: 1.3rem;
        margin-bottom: 3rem;
        font-weight: 300;
    }
    
    /* Drama Card Styling */
    .drama-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        color: white;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .drama-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.4);
    }
    
    .drama-title {
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .rank-badge {
        background: rgba(255, 255, 255, 0.2);
        padding: 0.3rem 0.8rem;
        border-radius: 50%;
        font-size: 1rem;
        font-weight: bold;
        backdrop-filter: blur(10px);
    }
    
    .drama-info {
        font-size: 1rem;
        line-height: 1.8;
        opacity: 0.95;
    }
    
    .drama-info strong {
        color: #FFD93D;
        font-weight: 600;
    }
    
    .score-badge {
        background: #FFD93D;
        color: #1A1A2E;
        padding: 0.4rem 1rem;
        border-radius: 25px;
        font-weight: 700;
        display: inline-block;
        margin-top: 1rem;
        font-size: 0.95rem;
        box-shadow: 0 4px 10px rgba(255, 217, 61, 0.3);
    }
    
    /* Filter Section Styling */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        padding: 0.75rem;
        transition: border-color 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    .stSelectbox > div > div {
        border-radius: 10px;
    }
    
    /* Button Styling */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s ease;
        border: none;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.75rem 2rem;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px 10px 0 0;
        padding: 1rem 2rem;
        font-weight: 600;
    }
    
    /* Search Box Enhancement */
    div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"] {
        gap: 1rem;
    }
    
    /* Metrics Styling */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
    }
</style>
""",
    unsafe_allow_html=True,
)


# ======================================================
# HELPER FUNCTIONS
# ======================================================
def check_api_health() -> bool:
    """Check if backend API is running"""
    try:
        response = requests.get(f"{API_URL}/", timeout=2)
        return response.status_code == 200
    except:
        return False


def get_recommendations(query: str, top_n: int = 5) -> Dict:
    """Get recommendations from backend API"""
    try:
        response = requests.get(
            f"{API_URL}/recommend", params={"title": query, "top_n": top_n}, timeout=10
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API error: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}


def format_drama_card(drama: Dict, rank: int) -> str:
    """Format drama data into HTML card"""
    title = drama.get("Title", "Unknown")
    genre = drama.get("Genre", drama.get("genres", "N/A"))
    description = drama.get(
        "Description", drama.get("description", "No description available")
    )

    # Truncate description
    if len(description) > 250:
        description = description[:250] + "..."

    cast = drama.get("Cast", drama.get("actors", "N/A"))
    rating = drama.get("rating_value", drama.get("score", "N/A"))
    episodes = drama.get("episodes", drama.get("Episodes", "N/A"))

    # Format cast
    if isinstance(cast, str) and len(cast) > 100:
        cast = cast[:100] + "..."

    return f"""
    <div class="drama-card">
        <div class="drama-title">
            <span class="rank-badge">#{rank}</span>
            <span>{title}</span>
        </div>
        <div class="drama-info">
            <strong>🎭 Genre:</strong> {genre}<br>
            <strong>⭐ Rating:</strong> {rating} | <strong>📺 Episodes:</strong> {episodes}<br>
            <strong>🎬 Cast:</strong> {cast}<br><br>
            <strong>📖 Synopsis:</strong><br>
            {description}
        </div>
        <span class="score-badge">⭐ {rating}</span>
    </div>
    """


# ======================================================
# SIDEBAR
# ======================================================
with st.sidebar:
    st.markdown("### 🎬 SeoulMate")
    st.markdown("*Your AI-Powered K-Drama Companion*")

    st.markdown("---")

    st.markdown("#### 🔍 About")
    st.markdown(
        """
    **SeoulMate** uses advanced AI to find your perfect K-drama match:
    
    - 🧠 **Fine-tuned SBERT** - Smart semantic understanding
    - 🔍 **Hybrid Search** - FAISS + BM25Plus for best results
    - 🎯 **Cross-Encoder** - Precision reranking
    - 📊 **1,922 Dramas** - Comprehensive database
    """
    )

    st.markdown("---")
    st.markdown("### ⚙️ Search Settings")
    top_n = st.slider(
        "📊 Number of Recommendations", 3, 15, 5, help="How many dramas to recommend"
    )

    st.markdown("---")
    st.markdown("### 🎯 Advanced Filters")

    with st.expander("🎭 Genre & People", expanded=False):
        genre = st.text_input(
            "🎭 Genre", "", placeholder="e.g., Romance, Action, Thriller"
        )
        director = st.text_input("🎬 Director", "", placeholder="e.g., Kim Eun-sook")
        screenwriters = st.text_input(
            "✍️ Screenwriter", "", placeholder="e.g., Park Ji-eun"
        )

    with st.expander("🏢 Production & Publisher", expanded=False):
        publisher = st.text_input(
            "📺 Publisher/Network", "", placeholder="e.g., tvN, Netflix"
        )
        keywords = st.text_input("🏷️ Keywords", "", placeholder="e.g., time travel, CEO")

    with st.expander("⭐ Ratings & Quality", expanded=False):
        rating_value = st.text_input("⭐ Min Rating", "", placeholder="e.g., 8.0")
        rating_count = st.text_input(
            "👥 Min Rating Count", "", placeholder="e.g., 1000"
        )

    with st.expander("🔄 Similar Drama Finder", expanded=False):
        similar_to = st.text_input(
            "🎯 Find Similar To", "", placeholder="Enter a drama title"
        )

    st.markdown("---")
    st.markdown("### 🔢 Sort Results")
    sort_by = st.selectbox(
        "Sort By",
        [
            "",
            "rating_value",
            "popularity",
            "date_published",
            "episodes",
            "duration",
            "ranked",
            "watchers",
        ],
        format_func=lambda x: {
            "": "Relevance (Default)",
            "rating_value": "⭐ Rating",
            "popularity": "🔥 Popularity",
            "date_published": "📅 Release Date",
            "episodes": "📺 Episode Count",
            "duration": "⏱️ Duration",
            "ranked": "🏆 Rank",
            "watchers": "👁️ Viewers",
        }.get(x, x),
    )
    sort_order = st.selectbox(
        "Sort Order",
        ["desc", "asc"],
        format_func=lambda x: "↓ Descending" if x == "desc" else "↑ Ascending",
    )

    st.markdown("---")
    st.markdown("### 📊 System Status")
    if check_api_health():
        st.success("✅ API Online")
    else:
        st.error("❌ API Offline")
        st.info("💡 Start backend: `python backend/app.py`")

# ======================================================
# MAIN CONTENT
# ======================================================
st.markdown('<div class="main-header">🎬 SeoulMate</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">✨ Discover Your Next Favorite K-Drama with AI-Powered Recommendations</div>',
    unsafe_allow_html=True,
)

# Search tabs
tab1, tab2, tab3 = st.tabs(["🔍 Smart Search", "📊 Statistics", "ℹ️ How It Works"])

with tab1:
    st.markdown("### 🎯 Find Your Perfect Drama")
    st.markdown(
        "Enter a drama title, describe what you're looking for, or use our advanced filters!"
    )

    col1, col2 = st.columns([5, 1])
    with col1:
        query = st.text_input(
            "Search for K-Dramas:",
            placeholder="Try: 'Crash Landing on You', 'romantic comedy', 'time travel thriller'...",
            label_visibility="collapsed",
            key="search_input",
        )
    with col2:
        search_button = st.button("🔍 Search", use_container_width=True, type="primary")

    # Example queries with better styling
    st.markdown("##### 💡 Quick Searches")
    example_col1, example_col2, example_col3, example_col4 = st.columns(4)
    with example_col1:
        if st.button("💕 Crash Landing on You", use_container_width=True):
            query = "Crash Landing on You"
            search_button = True
    with example_col2:
        if st.button("🍜 Itaewon Class", use_container_width=True):
            query = "Itaewon Class"
            search_button = True
    with example_col3:
        if st.button("😂 Romantic Comedy", use_container_width=True):
            query = "romantic comedy"
            search_button = True
    with example_col4:
        if st.button("🕰️ Historical Drama", use_container_width=True):
            query = "historical drama"
            search_button = True

    # Search results
    if query and search_button:
        # Collect all filter params from sidebar
        filter_params = {
            "genre": genre,
            "director": director,
            "publisher": publisher,
            "rating_value": rating_value,
            "rating_count": rating_count,
            "keywords": keywords,
            "screenwriters": screenwriters,
            "sort_by": sort_by,
            "sort_order": sort_order,
            "similar_to": similar_to,
        }
        # Remove empty values
        filter_params = {k: v for k, v in filter_params.items() if v not in [None, ""]}
        params = {"title": query, "top_n": top_n}
        params.update(filter_params)

        with st.spinner(
            "🔮 AI is analyzing thousands of dramas to find your perfect matches..."
        ):
            try:
                response = requests.get(
                    f"{API_URL}/recommend", params=params, timeout=10
                )
                if response.status_code == 200:
                    results = response.json()
                else:
                    results = {"error": f"API error: {response.status_code}"}
            except Exception as e:
                results = {"error": str(e)}

            if "error" in results:
                st.error(f"❌ **Error:** {results['error']}")
                st.info(
                    "💡 **Tip:** Make sure the backend is running with `python backend/app.py`"
                )
            else:
                recommendations = results.get("recommendations", [])

                if recommendations:
                    st.success(
                        f"✨ **Found {len(recommendations)} amazing recommendations for you!**"
                    )

                    # Display active filters
                    active_filters = [
                        f"**{k.replace('_', ' ').title()}:** {v}"
                        for k, v in filter_params.items()
                        if v
                    ]
                    if active_filters:
                        st.info("🎯 **Active Filters:** " + " | ".join(active_filters))

                    st.markdown("---")

                    # Display results
                    for idx, drama in enumerate(recommendations, 1):
                        st.markdown(
                            format_drama_card(drama, idx), unsafe_allow_html=True
                        )
                else:
                    st.warning(
                        "😔 No recommendations found. Try adjusting your search or filters!"
                    )
                    st.info(
                        "💡 **Tips:**\n- Try a broader search term\n- Remove some filters\n- Check spelling of drama titles"
                    )

with tab2:
    st.markdown("### 📊 SeoulMate Statistics")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📚 Total Dramas", "1,922", help="Complete database of K-dramas")
    with col2:
        st.metric("🤖 AI Model", "v3.1", help="Latest recommendation engine version")
    with col3:
        st.metric("🎯 Accuracy", "Fine-tuned", help="Trained on 1,922 dramas")
    with col4:
        st.metric("⚡ Speed", "< 1s", help="Average response time")

    st.markdown("---")

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("#### 🧠 AI Technology Stack")
        st.markdown(
            """
        - **SBERT Model:** `sbert-finetuned-full`
          - 3 epochs training
          - Multilingual support
          - Semantic understanding
        
        - **Retrieval System:** Hybrid approach
          - FAISS IndexFlatIP for vector search
          - BM25Plus for lexical matching
          - Combined scoring (α=0.7)
        
        - **Reranker:** Cross-encoder
          - 3 epochs training
          - 25,000+ training pairs
          - Precision refinement
        """
        )

    with col_right:
        st.markdown("#### 🎯 Features")
        st.markdown(
            """
        ✅ **Smart Semantic Search**
        - Understands context and meaning
        - Works with descriptions
        
        ✅ **Fuzzy Matching**
        - Handles typos gracefully
        - Finds close matches
        
        ✅ **Advanced Filters**
        - Genre, director, network
        - Ratings and popularity
        - Custom keywords
        
        ✅ **Similar Drama Finder**
        - Discover shows like your favorites
        - AI-powered similarity
        
        ✅ **Flexible Sorting**
        - By rating, popularity, date
        - Ascending or descending
        """
        )

    st.markdown("---")
    st.markdown("#### 🔧 Backend Technology")
    st.code(
        """
    Backend: FastAPI v3.1
    Models: Sentence-Transformers (SBERT)
    Vector DB: FAISS
    Lexical: BM25Plus
    Reranker: Cross-Encoder
    """,
        language="text",
    )

with tab3:
    st.markdown("### ℹ️ How SeoulMate Works")

    st.markdown("#### 🔍 The Recommendation Process")

    st.markdown(
        """
    **Step 1: Understanding Your Query** 🧠
    - SeoulMate uses AI to understand what you're looking for
    - Works with drama titles, genres, or descriptions
    - Handles typos and fuzzy matches
    
    **Step 2: Smart Search** 🔎
    - **Semantic Search (FAISS):** Finds dramas with similar meanings
    - **Lexical Search (BM25Plus):** Matches keywords and terms
    - Combines both for best results
    
    **Step 3: Filtering** 🎯
    - Applies your selected filters (genre, director, rating, etc.)
    - Sorts by your preferred criteria
    
    **Step 4: Precision Reranking** ⚡
    - Cross-encoder analyzes each match
    - Reorders results for maximum relevance
    
    **Step 5: Results!** 🎉
    - Top recommendations delivered to you
    - Complete with ratings, cast, and synopsis
    """
    )

    st.markdown("---")

    st.markdown("#### 🚀 Getting Started")
    st.markdown(
        """
    1. **Simple Search:** Just type a drama title or genre
    2. **Use Filters:** Refine by genre, director, ratings, etc.
    3. **Find Similar:** Enter a drama you love in "Similar To"
    4. **Sort Results:** Order by rating, popularity, or date
    """
    )

    st.markdown("---")

    st.markdown("#### 💡 Pro Tips")
    st.info(
        """
    - 🎭 **For Genre Searches:** Try "romantic comedy", "thriller", "historical"
    - 🎬 **For Director/Cast:** Use the advanced filters in the sidebar
    - ⭐ **For Top Rated:** Set minimum rating to 8.0 or higher
    - 🔄 **For Similar Dramas:** Use the "Similar To" filter
    - 📊 **For Sorting:** Choose "rating_value" to see highest rated first
    """
    )

    st.markdown("---")

    with st.expander("❓ Need Help?"):
        st.markdown(
            """
        **Common Questions:**
        
        - **Q: How accurate are the recommendations?**
          - A: Our AI is trained on 1,922 dramas with 3 epochs of fine-tuning for high accuracy.
        
        - **Q: Can I search in other languages?**
          - A: Our model supports multilingual queries!
        
        - **Q: How do I find dramas like my favorite?**
          - A: Use the "Similar To" filter and enter your favorite drama's title.
        
        - **Q: What if I get no results?**
          - A: Try broader search terms or remove some filters.
        """
        )

# ======================================================
# FOOTER
# ======================================================
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; padding: 2rem; color: #6c757d;">
        <p style="font-size: 0.9rem; margin-bottom: 0.5rem;">
            Made with ❤️ by the SeoulMate Team | Powered by AI & Advanced Machine Learning
        </p>
        <p style="font-size: 0.8rem; opacity: 0.7;">
            © 2025 SeoulMate - Your K-Drama Companion | v3.1
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)
