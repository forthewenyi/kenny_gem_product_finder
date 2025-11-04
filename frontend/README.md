# Kenny Gem Finder - Frontend

Next.js application for discovering high-quality kitchen products with AI-powered recommendations.

## Architecture Overview

### Technology Stack
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React Query (TanStack Query)
- **HTTP Client**: Axios

## Project Structure

```
frontend/
├── app/                      # Next.js App Router
│   ├── page.tsx             # Home page entry point
│   ├── HomePageContent.tsx  # Main application logic
│   ├── globals.css          # Global styles and animations
│   └── layout.tsx           # Root layout
├── components/              # React components
│   ├── Header.tsx           # Navigation header
│   ├── SearchInterface.tsx  # Search bar with filters
│   ├── FilterBar.tsx        # Result filtering UI
│   ├── ProductCard.tsx      # Product display card
│   ├── ProductDetailModal.tsx  # Full product detail modal
│   ├── CharacteristicsSection.tsx  # AI buying guidance display
│   └── ValuePreferenceDropdown.tsx
├── lib/
│   └── api.ts              # Backend API client
└── types/
    └── index.ts            # TypeScript type definitions
```

## Key Features

### 1. Search & Discovery
- AI-powered product search via backend Google ADK agents
- 3-minute timeout for comprehensive research
- Real-time search metrics and source transparency

### 2. Filter System

**Two Types of Filters:**

#### Search Input Filters (Pre-Search)
- **Value Preference**: User's value approach (Save Now, Best Value, Buy for Life)
- Only passed to backend when Search button is clicked
- No auto-triggering - simple state management

#### Result Filters (Post-Search)
FilterBar component with 6 filter types:
- **Value**: Good/Better/Best tier filtering
- **Price**: Range slider for maximum upfront price
- **Brand**: Toggle buttons for all brands in results
- **Material**: Toggle buttons for product materials
- **Features**: Toggle buttons for characteristics (dynamically generated from backend)
- **Cost/Year**: Range slider for maximum annual ownership cost

Features:
- Client-side filtering - no backend API calls (instant)
- Always visible with expandable sections
- Active filters displayed as removable pills
- Clear all functionality

### 3. AI Buying Guidance
- **Characteristics Section**: AI-generated buying guidance for each product category
- **Multi-select Filtering**: Select multiple characteristics to filter products
- **Fuzzy Matching**: Smart matching between AI characteristics and product features
- **Visual Feedback**: Selected characteristics highlighted with checkmark badges

### 4. Product Display
- **Product Cards**: Click to view details, "Select to Compare" button for comparisons
- **Product Detail Modal**: Comprehensive view with value breakdown, quality data, practical metrics, sources
- Good/Better/Best tier organization
- Kenny's Pick highlighting (best value in Better tier)

### 5. Comparison View
- **Streamlined Layout**: 7 consolidated sections (down from 12)
- **No Duplicates**: Single source of truth for price, lifespan, recommendations
- Apple-style side-by-side comparison (up to 3 products)
- Sections:
  1. Value at a Glance (price, lifespan, why it's recommended)
  2. Quality & Durability (scores, repairability, failure points)
  3. Key Features (characteristics + materials combined)
  4. Practical Use (cleaning, setup, learning curve, maintenance)
  5. Considerations (best for + trade-offs)
  6. User Reviews Summary (key insights + sources)
  7. Where to Buy (purchase links with hover tooltips)

## Development

### Setup
```bash
npm install
```

### Run Dev Server
```bash
npm run dev
```
Server starts at http://localhost:3000

### Build
```bash
npm run build
```

### Environment Variables
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Recent Changes

### Nov 4, 2024 - Product Detail Modal & Comparison Reorganization
**Added:**
- ✅ **ProductDetailModal**: Comprehensive product view with all backend data
  - Value breakdown (price, cost/year, cost/day, lifespan)
  - Quality & durability metrics (score, repairability, failure points)
  - Practical day-to-day use details (cleaning, setup, maintenance)
  - Materials, characteristics, best for, trade-offs
  - Source transparency with clickable research links
- ✅ **AI Buying Characteristics**: Backend integration via `characteristic_generator`
  - Multi-select filtering (select multiple characteristics simultaneously)
  - Fuzzy matching between AI labels and product features
  - Visual feedback with selected badges and product counts
- ✅ **Comparison Section Reorganization**: Streamlined from 12 to 7 sections
  - Eliminated duplicate information (lifespan, price, why_its_a_gem, best_for)
  - Consolidated related data into logical groupings
  - Improved scanability and decision-making flow
- ✅ **ProductCard Design Update**: Native design system consistency
  - Added explicit borders and ring-2 selection pattern
  - Separated onClick (comparison) vs onViewDetails (modal) handlers
  - Updated instruction text for clarity

**Code Changes:**
- 11 files changed, 743 insertions(+), 336 deletions(-)

### Nov 3, 2024 - Filter System Refactor
**Problem:**
- Hard-coded SIZE, SURFACE, FEATURES filters from `/config/productCharacteristics.ts`
- Auto-triggering searches on filter changes (frustrating 93s waits)
- Confusing mix of search input filters and result filters

**Solution:**
- ✅ Removed all hard-coded product characteristics
- ✅ Simplified to single input filter: Value Preference (lazy - no auto-trigger)
- ✅ Result filters dynamically generated from backend `aggregated_characteristics`
- ✅ Clear visual separation between filter types
- ✅ Simple `useState` for all filter state
- ✅ Removed focus ring artifacts (green rectangles)

**Code Reduction:**
- Total: ~1,058 lines removed, 487 lines added

## License

MIT
