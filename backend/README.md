# Kenny Gem Finder - Backend

AI-powered kitchen product search API using **Google Agent Development Kit (ADK)** + **Gemini 2.5 Flash** for intelligent multi-agent product research.

## Current Architecture (December 2024)

### Multi-Agent Search Pipeline

We use Google ADK's **SequentialAgent** pattern with 3 specialized agents:

```
Context Discovery Agent → Product Finder Agent → Synthesis Agent
```

1. **Context Discovery Agent**: Researches real-world usage patterns, materials science, durability insights
2. **Product Finder Agent**: Finds specific products with reviews, prices, and characteristics
3. **Synthesis Agent**: Organizes products into Good/Better/Best tiers with insights

### Key Features

- ✅ **Parallel Search Execution**: Agents make 4-8 Google searches simultaneously (3-7x faster)
- ✅ **Google Custom Search API**: Reliable, production-ready search (100 free queries/day)
- ✅ **Database Caching**: Supabase PostgreSQL for cached results
- ✅ **Personalized Search**: User characteristics passed to agents for tailored recommendations
- ✅ **Dynamic Characteristics**: Backend discovers what matters for each product (no hard-coding)
- ✅ **Comprehensive Product Data**: Materials, durability, practical metrics, trade-offs, sources

### Recent Improvements (Session Nov 3, 2024)

**Backend:**
- Migrated from coordinator agent to SequentialAgent with state management (`output_key`)
- Added async Google Custom Search API support via `httpx`
- Implemented parallel search hints in agent prompts (4 searches in 0.6s!)
- Added timing profiling for performance monitoring
- All product fields now returned: materials, characteristics, key_features, why_its_a_gem, best_for, trade_offs, web_sources, purchase_links, professional_reviews

**Frontend:**
- Removed 100+ lines of hard-coded product-specific filter logic
- Simplified client-side filtering (removed household_size → skillet size mapping)
- Now trusts backend personalization instead of duplicate filtering
- Made productConfig optional (backend dynamically discovers characteristics)
- Fixed TypeScript errors and aligned with backend data structure

## Setup

### 1. Install Python Dependencies

```bash
cd backend
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

### 2. Get API Keys

**Google AI API Key (for Gemini):**
1. Go to https://aistudio.google.com/app/apikey
2. Create a new API key
3. Copy the key

**Google Custom Search API:**
1. **API Key**: https://console.cloud.google.com/apis/credentials
   - Create project → Enable Custom Search API → Create API Key
2. **Search Engine ID**: https://programmablesearchengine.google.com/
   - Create new search engine → Search entire web: Yes
   - Copy Search Engine ID (cx parameter)

**Supabase (Database):**
1. Go to https://supabase.com
2. Create a new project
3. Copy the URL and anon key from Settings → API

### 3. Configure Environment Variables

Create `.env` file:

```bash
# Google AI (Gemini)
GOOGLE_API_KEY=your_gemini_api_key_here

# Google Custom Search
GOOGLE_SEARCH_API_KEY=your_search_api_key_here
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here
```

### 4. Run the Server

```bash
# Development mode (auto-reload)
uv run python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Or production
uv run python main.py
```

Server will start at: **http://localhost:8000**

## API Documentation

Once running, visit:
- **Interactive docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### `POST /api/search`
AI-powered product search with personalization

**Request:**
```json
{
  "query": "frying pan",
  "max_price": 150,
  "context": {
    "location": "United States"
  },
  "characteristics": {
    "household_size": "2-4",
    "cooking_frequency": "daily",
    "surface": "pre_seasoned"
  }
}
```

**Response:**
```json
{
  "results": {
    "good": [...products...],
    "better": [...products...],
    "best": [...products...]
  },
  "aggregated_characteristics": [
    {"label": "Pre-seasoned", "count": 4, "product_names": [...]},
    {"label": "Helper handle", "count": 3, "product_names": [...]}
  ],
  "search_queries": [...],
  "total_sources_analyzed": 48,
  "processing_time_seconds": 99.27,
  "from_cache": false
}
```

### Product Schema

Each product includes:
- `name`, `brand`, `tier` (good/better/best)
- `value_metrics`: upfront_price, expected_lifespan_years, cost_per_year, cost_per_day
- `characteristics`: Array of searchable characteristics (e.g., "Pre-seasoned", "Helper handle")
- `key_features`: Array of key features
- `materials`: Array of materials (e.g., ["cast iron"])
- `why_its_a_gem`: 2-3 sentence explanation
- `best_for`: Specific use case
- `trade_offs`: Array of cons/limitations
- `web_sources`: Array of source URLs
- `purchase_links`: Array of {name, url} buy links
- `professional_reviews`: Array of review site names
- `durability_data`: Durability score, lifespan, failure points, repairability
- `practical_metrics`: Cleaning time, setup, learning curve, maintenance

## Project Structure

```
backend/
├── main.py                  # FastAPI application
├── adk_search.py            # Google ADK multi-agent search (NEW)
├── google_search_service.py # Google Custom Search API wrapper (NEW)
├── database_service.py      # Supabase caching layer (NEW)
├── models.py                # Pydantic data models
├── contextual_search.py     # Old Gemini search (deprecated)
├── test_adk.py              # Unit tests for ADK search
├── test_api_adk.py          # Integration tests
├── pyproject.toml           # UV package manager config
├── .env                     # Environment variables (git-ignored)
└── README.md                # This file
```

## How the ADK Agent Pipeline Works

### 1. Context Discovery Agent
Researches how people actually use the product:
- **Parallel searches**: "product reddit usage patterns", "product durability issues", "product material science"
- **Focus**: Real user experiences, material properties, common problems
- **Output**: `context_research` state passed to next agent

### 2. Product Finder Agent
Finds specific products based on context:
- **Reads**: `context_research` from previous agent
- **Parallel searches**: "best product reddit 2024", "product wirecutter review", "brand model durability"
- **Extracts**: Full product data with all fields
- **Output**: `product_findings` state with 6-10 products

### 3. Synthesis Agent
Organizes products into tiers:
- **Reads**: Both `context_research` and `product_findings`
- **Analyzes**: Price, durability, features
- **Output**: Final Good/Better/Best tier structure with insights

### Parallel Execution

Agents explicitly hint to make parallel tool calls:
```python
instruction="""
IMPORTANT - PARALLEL EXECUTION: Call google_search multiple times IN PARALLEL.
Make 4-6 search calls simultaneously, not one-by-one.
ALL AT ONCE in the same response.
"""
```

Result: **4 searches in 0.6s** (vs 2.0s sequential) = 3x faster!

## Testing

### Unit Test
```bash
uv run python test_adk.py
```

### API Integration Test
```bash
# Start server
uv run python -m uvicorn main:app --reload

# In another terminal
uv run python test_api_adk.py
```

### Manual Test via Frontend
The frontend at http://localhost:3000 will automatically use the backend API.

## Performance

- **Context Discovery**: ~17s (4 parallel searches)
- **Product Finder**: ~82s (multiple search rounds with 5-8 searches each)
- **Synthesis**: ~0.5s (no searches, just analysis)
- **Total**: ~99s for comprehensive research
- **With Cache**: <1s for repeated queries

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_API_KEY` | Yes | Google AI (Gemini) API key |
| `GOOGLE_SEARCH_API_KEY` | Yes | Google Custom Search API key |
| `GOOGLE_SEARCH_ENGINE_ID` | Yes | Programmable Search Engine ID |
| `SUPABASE_URL` | Yes | Supabase project URL |
| `SUPABASE_KEY` | Yes | Supabase anon/service key |

## Troubleshooting

**"Google Custom Search API not configured"**
- Will fallback to free `googlesearch-python` library (may be rate-limited)
- For production, set up Google Custom Search API (100 free queries/day)

**"App name mismatch detected"**
- Warning from Google ADK, doesn't affect functionality
- Can be safely ignored

**Slow response times**
- First search: ~99s (comprehensive research with 10+ Google searches)
- Cached search: <1s
- ADK agents are thorough - they research multiple aspects in parallel

**No products returned**
- Check that agents have access to google_search tool
- Verify Google Search API is working (check logs for search results)
- Try increasing num_results in google_search calls

## Migration Notes

### From LangChain/Tavily to Google ADK/Gemini

**Why we migrated:**
- ✅ Better control over agent flow with SequentialAgent
- ✅ State management between agents via output_key
- ✅ Native async support with Google APIs
- ✅ Faster response with parallel searches
- ✅ Google Custom Search API more reliable than Tavily

**Breaking changes:**
- Search function signature: Now async `await google_search(query, num_results)`
- Agent output: Uses output_key for state passing instead of tool results
- Event handling: Must check `event.is_final_response()` and `event.author`

## License

MIT
