# Kenny Gem Finder

AI-powered kitchen product search that helps you find high-quality, long-lasting products organized by value tiers (Good/Better/Best).

## 🎯 Project Overview

Kenny Gem Finder uses Google's Agent Development Kit (ADK) with Gemini 2.5 Flash to conduct comprehensive product research across Reddit, expert reviews, and user reports. The system analyzes durability, value metrics, and real-world usage patterns to recommend kitchen products that are actually worth buying.

### Key Features

- **Multi-Agent Research Pipeline**: 3 specialized ADK agents work sequentially
  - Context Discovery Agent: Researches usage patterns and durability
  - Product Finder Agent: Finds specific products with reviews
  - Synthesis Agent: Organizes into Good/Better/Best tiers
- **Parallel Search Execution**: 4-8 Google searches simultaneously (3-7x faster)
- **Value Metrics**: Upfront price, expected lifespan, cost-per-year, cost-per-day
- **Database Caching**: Supabase PostgreSQL for fast repeated queries
- **Dynamic Characteristics**: Backend discovers what matters for each product type
- **Transparent Sources**: Shows all Google searches and sources analyzed

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                    │
│  • Search interface with Value Preference filter             │
│  • Product comparison (Apple-style)                          │
│  • Dynamic result filtering                                  │
│  • Real-time search metrics                                  │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP (Axios, 180s timeout)
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                    Backend (FastAPI + ADK)                   │
│  • Google ADK Sequential Agents                              │
│  • Google Custom Search API (100 free/day)                   │
│  • Supabase caching layer                                    │
│  • Gemini 2.5 Flash LLM                                      │
└─────────────────────┬───────────────────────────────────────┘
                      │
            ┌─────────┴──────────┐
            │                    │
    ┌───────▼────────┐   ┌──────▼────────┐
    │ Google Search  │   │   Supabase    │
    │      API       │   │   PostgreSQL  │
    └────────────────┘   └───────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+ with `uv` package manager
- Node.js 18+ with npm
- Google AI API key (Gemini)
- Google Custom Search API credentials
- Supabase account

### Backend Setup

```bash
cd backend
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt

# Create .env file
cat > .env << 'ENVEOF'
GOOGLE_API_KEY=your_gemini_api_key
GOOGLE_SEARCH_API_KEY=your_search_api_key
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
ENVEOF

# Run server
uv run python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Server: http://localhost:8000

### Frontend Setup

```bash
cd frontend
npm install

# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Run dev server
npm run dev
```

App: http://localhost:3000

## 📁 Project Structure

```
kenny-gem-finder/
├── backend/                 # FastAPI + Google ADK
│   ├── main.py             # FastAPI app
│   ├── adk_search.py       # Multi-agent search pipeline
│   ├── database_service.py # Supabase caching
│   ├── models.py           # Pydantic schemas
│   └── README.md           # Backend docs
├── frontend/               # Next.js 14 app
│   ├── app/                # App Router
│   ├── components/         # React components
│   ├── lib/api.ts          # Backend client
│   └── README.md           # Frontend docs
└── README.md               # This file
```

## 🔍 How It Works

### Search Flow

1. **User enters query** + optional Value Preference (Save Now / Best Value / Buy for Life)
2. **Backend checks cache** - If found, returns in <1s
3. **If not cached, ADK agent pipeline runs**:
   - **Context Discovery** (~17s): Parallel searches for usage patterns, durability issues
   - **Product Finder** (~82s): Multiple rounds of searches for specific products
   - **Synthesis** (~0.5s): Organizes products into Good/Better/Best tiers
4. **Results cached** to Supabase for future queries
5. **Frontend displays** products with full details, comparison options, and sources

### Typical Search Times

- **Fresh search**: 78-133 seconds (comprehensive research)
- **Cached search**: <1 second
- **Parallel searches**: 4-8 simultaneous Google searches per agent

## 🎨 UI/UX Design

### Filter Architecture

**Search Input Filters** (pre-search):
- Value Preference: Controls tier focus and recommendations
- Only applied when Search button clicked (no auto-triggering)

**Result Filters** (post-search):
- Dynamically generated from backend's `aggregated_characteristics`
- Client-side filtering only (instant, no API calls)
- Filter by characteristics, materials, price tier

### Product Display

- **Good Tier**: Budget-friendly, 2-5 year lifespan
- **Better Tier**: Sweet spot, 8-15 years (Kenny's Pick here)
- **Best Tier**: Buy for life, 15-30+ years

## 📊 Key Technologies

### Backend
- **FastAPI**: Modern async Python web framework
- **Google ADK**: Agent Development Kit for LangChain-style orchestration
- **Gemini 2.5 Flash**: Fast, capable LLM for product research
- **Google Custom Search API**: Reliable web search (100 free queries/day)
- **Supabase**: PostgreSQL database with automatic caching

### Frontend
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type safety across the app
- **Tailwind CSS**: Utility-first styling
- **React Query**: Server state management
- **Axios**: HTTP client with 3-minute timeout

## 📈 Performance Metrics

- **Search Speed**: 78-133s for comprehensive research
- **Cache Hit Rate**: <1s for repeated queries
- **Parallel Efficiency**: 3-7x faster with simultaneous searches
- **Sources Analyzed**: Typically 40-60 web sources per search
- **Products Found**: 6-10 products across 3 tiers

## 🐛 Known Issues

See [TODO](#-todo) section below for tracking.

## 📝 Recent Updates

### November 5, 2025 - Lifespan Parsing Fix & Comparison Reorganization ✅

**Completed:**
- ✅ **Fixed lifespan parsing bug** for heirloom products (`backend/main.py:603-653`)
  - Added special keyword detection for "Lifetime", "Generations", "Decades"
  - "Lifetime / Generations" → 75 years (multi-generational heirloom)
  - "Lifetime" → 50 years (buy-it-for-life quality)
  - "Generations" → 75 years (heirloom quality)
  - "Decades" → 30 years (multiple decades)
  - **Impact**: Le Creuset cost/year fixed from $380/year → $5.07/year ✅
  - **Impact**: Staub cost/year fixed from $320/year → $4.67/year ✅
- ✅ **Reorganized comparison component** to VALUE framework order (`frontend/app/HomePageContent.tsx:424-663`)
  - 🔨 **PRODUCT**: brand, materials, key_features, why_its_a_gem, quality metrics
  - 🛠️ **SERVICE**: learning_curve, maintenance, honest drawbacks
  - 💎 **EQUITY**: professional_reviews (now displayed!), best_for
  - 💰 **PRICE & ACTION**: value breakdown, purchase links
- ✅ Added **Professional Reviews** section (was missing in previous comparison view)
- ✅ Changed "Trade-offs" → "Honest Drawbacks" for transparency
- ✅ **Fixed parenthetical text edge case** in lifespan parsing (`backend/main.py:618-621`)
  - Added regex to strip parenthetical text before processing ranges
  - "5-10 years (or more with very careful handling)" → now correctly parses to 7.5 years ✅
  - "15-30 years (with proper care, enamel durability is key)" → now correctly parses to 22.5 years ✅

### November 4, 2025 - VALUE Framework Implementation ✅

**Completed:**
- ✅ Implemented VALUE framework across entire stack (backend, frontend, database)
- ✅ Changed "Quality" → "Value" terminology in all UI components
- ✅ Reorganized comparison cards and product detail modals by VALUE framework order:
  - 🔨 **PRODUCT** (Physical Quality): name, brand, materials, key_features, why_its_a_gem
  - 🛠️ **SERVICE** (Support & Usability): maintenance_tasks, learning_curve, drawbacks
  - 💎 **EQUITY** (Trust & Value Retention): professional_reviews, best_for
  - 💰 **PRICE & ACTION**: price, lifespan, cost/year, cost/day, purchase_links
- ✅ Updated ProductCard stars to align with value score (not just quality)
- ✅ Verified all 6 filters working: Value Tier, Price, Brand, Material, Features, "What to Look For"
- ✅ Renamed `trade_offs` → `drawbacks` for honest terminology
- ✅ Added VALUE_FRAMEWORK_ALIGNMENT.md documentation
- ✅ Created comprehensive verification scripts

**VALUE Score Calculation:**
```
VALUE Score (0-100) = PRODUCT (80 pts) + SERVICE (20 pts)

PRODUCT (80 pts) = Longevity (30) + Failure Rate (30) + Materials (20)
SERVICE (20 pts) = Repairability/Maintenance (20)

Then compared against PRICE to determine tier:
- GOOD: Great value for the price
- BETTER: Excellent value with premium features
- BEST: Best-in-class, heirloom quality
```

## 📝 TODO

### High Priority

- [ ] **Add key_differentiator field**: What makes THIS product special vs competitors
  - Currently only in agent prompts, not returned in Product schema
  - Add to backend models.py, frontend types, and database schema
  - Display in PRODUCT section of comparison cards and modal

- [ ] **Product Images**: Extract image URLs from search results to display product photos
  - ADK agents should capture product image URLs during searches
  - Update Product schema to include `image_url` field
  - Display images in ProductCard component
  - Fallback to placeholder if no image available

- [ ] **Real-time Search Progress**: Setup WebSocket connection for live ADK event streaming
  - Backend: Add WebSocket endpoint to stream ADK agent events
  - Frontend: Connect to WebSocket and update "Kenny is thinking" section
  - Show progress: "Researching usage patterns...", "Finding products...", "Analyzing durability..."
  - Display current agent step and search queries being executed

- [ ] **Fix Search Transparency Metrics**: Section shows "0 sources from 0 searches" despite having results
  - ✅ Backend IS correctly capturing metrics (verified in logs: 11 searches, 160-188 sources)
  - ✅ `sources_by_phase_dict` populated correctly with all query details
  - ❌ Frontend display issue - metrics not rendering in SearchMetrics component
  - Need to verify `SearchResponse` fields are being passed to frontend correctly

### Medium Priority

- [x] ~~Lifespan parsing: "Lifetime" and "Decades" incorrectly parsed as 1 year~~ ✅ **FIXED (Nov 5)**
- [x] ~~Lifespan parsing edge case: Parenthetical text breaks range parsing~~ ✅ **FIXED (Nov 5)**
- [ ] Handle products with missing price data (null price causes parse failure)
- [ ] Mobile responsive design improvements
- [ ] Add loading skeleton states
- [ ] Implement search history / saved searches
- [ ] Add "Compare" button on product cards for easier selection

### Low Priority

- [ ] User accounts and preferences persistence
- [ ] Export comparison as PDF
- [ ] Share search results via URL
- [ ] Dark mode support
- [ ] Keyboard navigation improvements

## 🧪 Testing

### Backend Tests
```bash
cd backend
uv run python test_adk.py                    # Unit tests
uv run python test_api_adk.py                # Integration tests
uv run python test_cache_complete.py         # Cache tests
```

### Frontend Tests
```bash
cd frontend
npm run test                                  # Unit tests (when added)
npm run build                                 # Type checking
```

## 📚 Documentation

- [Backend README](./backend/README.md) - ADK architecture, API endpoints, setup
- [Frontend README](./frontend/README.md) - Component architecture, filter system
- [VALUE Framework Alignment](./VALUE_FRAMEWORK_ALIGNMENT.md) - Complete system alignment report
- [Cache Setup](./backend/CACHE_SETUP.md) - Caching implementation guide
- [Migration to Gemini](./backend/MIGRATION_TO_GEMINI.md) - LangChain → ADK migration

## 🤝 Contributing

This is a personal project, but suggestions are welcome! File an issue if you spot bugs or have ideas.

## 📄 License

MIT

---

**Built with** ❤️ **using Google ADK + Gemini 2.5 Flash**
