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
- Client-side filtering of displayed products
- Dynamically generated from backend's `aggregated_characteristics`
- Filter by characteristics, materials, and price tier
- No backend API calls - instant filtering

### 3. Product Display
- Good/Better/Best tier organization
- Comprehensive product details (durability, materials, value metrics)
- Apple-style comparison view (up to 3 products)
- Kenny's Pick highlighting (best value in Better tier)

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

## Recent Changes (Nov 3, 2024)

### Filter System Refactor
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
