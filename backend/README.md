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

- ✅ **Parallel Search Execution**: Agents make 13-19 Google searches per query (5-7 for context, 8-12 for products)
- ✅ **Google Custom Search API**: Reliable, production-ready search (100 free queries/day, ~5-7 unique searches)
- ✅ **Database Caching**: Supabase PostgreSQL for cached results
- ✅ **Personalized Search**: User characteristics passed to agents for tailored recommendations
- ✅ **Dynamic Characteristics**: Backend discovers what matters for each product (no hard-coding)
- ✅ **Comprehensive Product Data**: Materials, durability, practical metrics, trade-offs, sources

### Recent Improvements

**Session Nov 4, 2024:**
- Removed testing mode from ADK agents for production-ready search
- Context Discovery Agent: 1 → 5-7 focused searches (usage, durability, materials)
- Product Finder Agent: 1 → 8-12 targeted searches (budget/mid/premium tiers)
- Total search capacity: 13-19 Google searches per query
- Implemented comprehensive cache clearing utilities
- Added parallel search execution across all research phases

**Session Nov 3, 2024:**
- Migrated from coordinator agent to SequentialAgent with state management (`output_key`)
- Added async Google Custom Search API support via `httpx`
- Implemented parallel search hints in agent prompts
- Added timing profiling for performance monitoring
- All product fields now returned: materials, characteristics, key_features, why_its_a_gem, best_for, trade_offs, web_sources, purchase_links, professional_reviews
- Frontend: Removed 100+ lines of hard-coded product-specific filter logic
- Simplified client-side filtering and made productConfig optional

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
- **Search count**: 5-7 focused searches executed in parallel
- **Topics**: Real user experiences (Reddit), usage patterns, durability/longevity, common problems/failures, material science insights, living constraints, compatibility
- **Examples**:
  - "frying pan reddit honest review"
  - "frying pan how long does it last lifespan"
  - "frying pan material quality durability comparison"
- **Focus**: Real user experiences, material properties, common problems
- **Output**: `context_research` state passed to next agent

### 2. Product Finder Agent
Finds specific products based on context:
- **Search count**: 8-12 targeted searches executed in parallel
- **Topics**: Budget-tier products, mid-tier quality, premium buy-it-for-life, professional recommendations, Reddit BIFL favorites, expert reviews, brand comparisons, pricing, durability reports, long-term reviews
- **Examples**:
  - "best budget frying pan under $50 reddit"
  - "best frying pan $50-150 wirecutter serious eats"
  - "best premium frying pan buy for life reddit"
  - "Lodge vs Field Company frying pan comparison"
- **Reads**: `context_research` from previous agent
- **Extracts**: Full product data with all fields
- **Output**: `product_findings` state with 6-9 products across all tiers

### 3. Synthesis Agent
Organizes products into tiers:
- **Reads**: Both `context_research` and `product_findings`
- **Analyzes**: Price, durability, features
- **Output**: Final Good/Better/Best tier structure with insights

### Parallel Execution

Agents execute multiple searches concurrently for maximum speed:
- **Context Agent**: 5-7 searches run in parallel (~8-15 seconds)
- **Product Finder**: 8-12 searches run in parallel (~20-40 seconds)
- **Total**: 13-19 searches executed per query

Each agent receives explicit search strategy instructions:
```python
instruction="""
SEARCH STRATEGY: Execute 5-7 focused searches to build comprehensive understanding.
Make parallel searches for different aspects - the tool supports concurrent execution.
"""
```

Result: **Comprehensive product research in 30-60 seconds** with parallel execution!

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

- **Context Discovery**: ~8-15s (5-7 parallel searches for usage patterns, durability, materials)
- **Product Finder**: ~20-40s (8-12 parallel searches across all price tiers)
- **Synthesis**: ~0.5s (no searches, just analysis and tier organization)
- **Total**: ~30-60s for comprehensive research with 13-19 searches
- **With Cache**: <1s for repeated queries (cache hit rate improves over time)
- **API Usage**: 13-19 searches per unique query = ~5-7 unique searches per day with free tier (100/day limit)

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
- First search: ~30-60s (comprehensive research with 13-19 Google searches)
- Cached search: <1s
- ADK agents are thorough - Context Agent (5-7 searches) + Product Finder (8-12 searches)
- This is normal for production-quality research across all price tiers

**Network errors or search failures**
- Ensure backend is running: `python -m uvicorn main:app --reload`
- Check API keys are set in `.env` file
- Verify Google Custom Search API has remaining quota (100 free/day)
- Clear cache if needed: `python clear_all_cache.py`

**No products returned**
- Check that agents have access to google_search tool
- Verify Google Search API is working (check logs for search results)
- Testing mode has been removed - agents should make 13-19 searches per query

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
