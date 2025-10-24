# Kenny Gem Finder - Backend

AI-powered kitchen product search API using LangChain + Tavily for real-time web research.

## Features

- **AI Agent Search**: LangChain agent with Tavily tool for web research
- **Good/Better/Best Tiers**: Automatic product categorization
- **Value Calculations**: Cost-per-year and cost-per-day metrics
- **Real-time Research**: No static database - always fresh results from Reddit, review sites, forums
- **RESTful API**: FastAPI with automatic OpenAPI docs

## Setup

### 1. Install Python Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Get API Keys

**OpenAI API Key:**
1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Copy the key (starts with `sk-...`)

**Tavily API Key:**
1. Go to https://tavily.com
2. Sign up for free tier (10,000 searches/month for $50)
3. Get your API key from dashboard

### 3. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```
OPENAI_API_KEY=sk-your-openai-key-here
TAVILY_API_KEY=tvly-your-tavily-key-here
```

### 4. Run the Server

```bash
# Development mode (auto-reload)
uvicorn main:app --reload

# Or use Python directly
python main.py
```

Server will start at: **http://localhost:8000**

## API Documentation

Once running, visit:
- **Interactive docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### `GET /`
Health check endpoint

### `GET /api/categories`
Get list of kitchen product categories

**Response:**
```json
{
  "categories": [
    {"id": "knives", "name": "Knives & Cutting", "icon": "🔪"},
    ...
  ]
}
```

### `POST /api/search`
AI-powered product search

**Request:**
```json
{
  "query": "I need a chef's knife that stays sharp for beginners",
  "tier_preference": "better",  // optional
  "max_price": 150,  // optional
  "context": {
    "location": "Austin, TX",
    "experience_level": "beginner"
  }
}
```

**Response:**
```json
{
  "results": {
    "good": [...],
    "better": [...],
    "best": [...]
  },
  "search_metadata": {
    "sources_searched": [...],
    "search_queries_used": [...]
  },
  "processing_time_seconds": 12.5,
  "educational_insights": [
    "Hard water in Austin can cause knife rust - dry immediately after washing"
  ]
}
```

### `POST /api/calculate-value`
Calculate value metrics for a product

**Query Parameters:**
- `price` (float): Product price in USD
- `lifespan` (float): Expected lifespan in years

**Response:**
```json
{
  "upfront_price": 400.0,
  "expected_lifespan_years": 30.0,
  "cost_per_year": 13.33,
  "cost_per_day": 0.04
}
```

## Project Structure

```
backend/
├── main.py              # FastAPI application
├── models.py            # Pydantic data models
├── agent_service.py     # LangChain agent with Tavily
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## How the AI Agent Works

1. **User submits query** (e.g., "chef's knife for beginners")
2. **LangChain agent analyzes** query to extract:
   - Product type
   - User context (beginner = Better tier)
   - Key requirements
3. **Agent uses Tavily Search** to research:
   - Reddit discussions (r/BuyItForLife, r/Cooking)
   - Professional reviews (Serious Eats, America's Test Kitchen)
   - Specialty kitchen sites
4. **Agent synthesizes findings** into Good/Better/Best tiers
5. **Returns structured results** with value metrics and sources

## Tier System

- **GOOD**: $20-80, 2-5 years (students, renters)
- **BETTER**: $80-200, 8-15 years (homeowners, serious cooks)
- **BEST**: $200-600+, 15-30+ years (lifetime investment)

## Development

### Testing the Agent

```bash
# Start the server
uvicorn main:app --reload

# In another terminal, test the search endpoint
curl -X POST "http://localhost:8000/api/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "cast iron skillet that won't rust", "context": {}}'
```

### Debugging

Set `verbose=True` in `agent_service.py` to see agent's thinking process in console.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key for GPT-4 |
| `TAVILY_API_KEY` | Yes | Tavily API key for web search |
| `ENVIRONMENT` | No | `development` or `production` |
| `LOG_LEVEL` | No | Logging level (default: INFO) |

## Troubleshooting

**"OPENAI_API_KEY not found"**
- Make sure `.env` file exists and contains your API key
- Check that `python-dotenv` is installed
- Restart the server after adding keys

**"TAVILY_API_KEY not found"**
- Get API key from https://tavily.com
- Add to `.env` file
- Restart server

**Slow response times**
- Tavily searches take 10-30 seconds
- Consider caching results for repeated queries
- Agent makes multiple search queries per request

## Next Steps

1. Test basic product search queries
2. Refine agent prompts for better tier assignment
3. Add caching for faster repeat queries
4. Implement structured output parsing
5. Add error handling for failed searches

## License

MIT
