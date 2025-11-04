# SeoulMate - Korean Drama Recommendation System

A comprehensive K-Drama recommendation system that combines web scraping, semantic search, and machine learning to provide personalized drama recommendations.

## 🎯 Project Overview

SeoulMate is an intelligent recommendation engine that helps users discover Korean dramas based on their preferences. The system uses a hybrid search approach combining semantic understanding with traditional keyword matching to deliver highly relevant recommendations.

## 🏗️ Architecture

### 1. Data Collection 🔍

#### Wikipedia Scraper
- **File**: `data_scrapper/wiki_scrapper_playwright.py`
- **Purpose**: Scrapes K-Drama data from Wikipedia
- **Data Collected**:
  - Title
  - Cast
  - Director
  - Genre
  - Episodes
  - Release dates
  - Descriptions

#### MyDramaList Scrapers
- **Scraper**: `data_scrapper/DramaList_Scrapper/scrapper.py`
- **Capabilities**:
  - Collects 250 pages of popular dramas
  - Downloads individual drama pages (10,000+ HTML files)
  - Extracts detailed metadata using fast lxml parsing
  - Multithreaded processing for optimal performance

**Extracted Fields**:
- Basic Info: Title, alternate names, URL, description, image
- Metadata: Country, genres, keywords, publisher
- Ratings: Rating value, rating count, popularity ranking
- Production: Directors, screenwriters
- Details: Episodes, aired dates, duration, content rating
- Engagement: Watchers, ranked position
- Cast: Actors and their roles

#### Dataset
- **File**: `kdrama_dataset_detailed_v8_playwright.csv`
- **Content**: Comprehensive K-Drama information with all extracted fields
- **Size**: 10,000+ dramas

### 2. Recommendation Engine 🎯

#### Hybrid Search System
The recommendation engine combines multiple search techniques for optimal results:

1. **Semantic Search**
   - Technology: FAISS + Sentence Transformers
   - Purpose: Understands meaning and context
   - Model: `paraphrase-multilingual-mpnet-base-v2`
   - Features: Multilingual support (Korean & English)

2. **Lexical Search**
   - Technology: BM25 (Best Matching 25)
   - Purpose: Keyword matching and exact term retrieval
   - Use Case: Finding specific titles or terms

3. **Cross-Encoder Reranker**
   - Purpose: Improves relevance of final results
   - Function: Re-scores candidates for better ranking

4. **Fuzzy Matching**
   - Purpose: Handles typos and spelling variations
   - Benefit: More forgiving user input

#### Model Details
- **Primary Model**: `paraphrase-multilingual-mpnet-base-v2`
- **Vector Dimension**: 768
- **Language Support**: Multilingual (Korean, English, and more)
- **Index Type**: FAISS for efficient similarity search

### 3. Backend API 🚀

#### FastAPI Server
- **File**: `app.py`
- **Port**: 8001
- **Framework**: FastAPI

#### Endpoints

##### `/recommend` - Get Drama Recommendations
**Method**: POST

**Request Body**:
```json
{
  "query": "romantic comedy drama",
  "top_n": 10
}
```

**Response**:
```json
{
  "recommendations": [
    {
      "title": "Drama Title",
      "score": 0.95,
      "description": "Drama description...",
      "genres": "Romance, Comedy",
      "rating": 8.5,
      "episodes": 16,
      "year": 2023
    }
  ]
}
```

**Features**:
- CORS enabled for frontend integration
- Fast response times with FAISS indexing
- Configurable number of recommendations
- Detailed metadata in responses

## 📁 Project Structure

```
SeoulMate/
├── data_scrapper/
│   ├── wiki_scrapper_playwright.py          # Wikipedia scraper
│   ├── DramaList_Scrapper/
│   │   ├── scrapper.py                      # Main MyDramaList scraper
│   │   ├── dramas_html/                     # Downloaded HTML files
│   │   └── dramalist_all_dramas.csv         # Scraped data output
│   └── kdrama_dataset_detailed_v8_playwright.csv  # Final dataset
├── app.py                                    # FastAPI backend server
├── recommendation_engine/                    # ML models and search logic
└── README.md                                 # This file
```

## 🚀 Getting Started

### Prerequisites
```bash
pip install fastapi uvicorn
pip install sentence-transformers faiss-cpu
pip install beautifulsoup4 lxml
pip install playwright pandas tqdm
pip install rank-bm25 thefuzz
```

### Running the Scraper
```bash
# Scrape MyDramaList data
cd data_scrapper/DramaList_Scrapper
python scrapper.py
```

### Starting the API Server
```bash
# Run FastAPI server
python app.py

# Server will start at http://localhost:8001
```

### Making Recommendations
```bash
# Example API call
curl -X POST "http://localhost:8001/recommend" \
  -H "Content-Type: application/json" \
  -d '{"query": "romantic comedy", "top_n": 5}'
```

## 🔧 Configuration

### Scraper Settings
- **Max Workers**: Auto-detects CPU cores (configurable)
- **Skip Existing**: Avoids re-processing already scraped dramas
- **Output Format**: CSV with UTF-8 encoding

### Recommendation Engine
- **Top N Results**: Configurable (default: 10)
- **Reranking**: Enabled by default
- **Fuzzy Match Threshold**: Adjustable for typo tolerance

## 📊 Data Pipeline

```
Wikipedia + MyDramaList
        ↓
   HTML Scraping (Playwright/lxml)
        ↓
   Data Extraction & Cleaning
        ↓
   CSV Dataset (10,000+ dramas)
        ↓
   Embedding Generation (Sentence Transformers)
        ↓
   FAISS Index Creation
        ↓
   Hybrid Search Engine
        ↓
   FastAPI Recommendation Service
```

## 🎨 Features

### Data Collection
- ✅ Multi-source scraping (Wikipedia + MyDramaList)
- ✅ Multithreaded processing for speed
- ✅ Comprehensive metadata extraction
- ✅ Error handling and retry logic
- ✅ Progress tracking with tqdm

### Recommendation System
- ✅ Semantic understanding of queries
- ✅ Keyword-based search
- ✅ Intelligent reranking
- ✅ Typo tolerance
- ✅ Multilingual support
- ✅ Fast retrieval with FAISS

### API
- ✅ RESTful API design
- ✅ CORS support
- ✅ JSON responses
- ✅ Configurable parameters
- ✅ Production-ready with FastAPI

## 🔮 Future Enhancements

- [ ] User preference learning
- [ ] Collaborative filtering
- [ ] Real-time data updates
- [ ] Advanced filtering (by year, genre, rating)
- [ ] Similar drama discovery
- [ ] User ratings integration
- [ ] Frontend web application
- [ ] Mobile app support

## 📝 License

This project is for educational and personal use.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## 📧 Contact

For questions or suggestions, please open an issue in the repository.

---

**Built with ❤️ for K-Drama enthusiasts**
