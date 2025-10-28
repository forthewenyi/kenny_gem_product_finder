# Database Migration Instructions

## Status
The popular search dropdown feature is **fully implemented** in code but requires a **one-time database migration** to create the `popular_search_terms` table.

## What's Been Implemented

### Backend (✅ Complete)
- Created `popular_search_service.py` with caching and tracking logic
- Added `/api/popular-searches/{category}` endpoint
- Added `/api/track-search` endpoint
- Both endpoints are live and working (waiting for the table to exist)

### Frontend (✅ Complete)
- Created `NavigationDropdown.tsx` component with hover-activated dropdowns
- Updated `Header.tsx` to use dropdown menus
- Integrated with React Query for efficient data fetching
- Added API client functions in `lib/api.ts`
- Connected to search functionality in `page.tsx`

## Manual Migration Required

### Step 1: Access Supabase SQL Editor
Navigate to: https://supabase.com/dashboard/project/nuzndrucvjyvezgafgcd/sql

### Step 2: Run the Migration SQL
Copy and paste the following SQL into the editor and click "Run":

```sql
-- Migration: Create popular_search_terms table for dynamic navigation
-- This table tracks search term frequency to power the dropdown menus

CREATE TABLE IF NOT EXISTS popular_search_terms (
  id BIGSERIAL PRIMARY KEY,
  query_term TEXT NOT NULL,
  category TEXT NOT NULL CHECK (category IN ('cookware', 'knives', 'bakeware')),
  search_count INTEGER DEFAULT 1,
  last_searched TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  CONSTRAINT unique_term_category UNIQUE(query_term, category)
);

-- Index for fast queries by category and count
CREATE INDEX IF NOT EXISTS idx_popular_search_terms_category_count
ON popular_search_terms(category, search_count DESC);

-- Seed data for cold start
INSERT INTO popular_search_terms (query_term, category, search_count) VALUES
-- Cookware
('Cast Iron Skillet', 'cookware', 50),
('Stainless Steel Pan', 'cookware', 45),
('Dutch Oven', 'cookware', 40),
('Non-Stick Pan', 'cookware', 35),
('Wok', 'cookware', 30),
('Saucepan Set', 'cookware', 25),
('Roasting Pan', 'cookware', 20),
('Grill Pan', 'cookware', 15),

-- Knives
('Chef''s Knife', 'knives', 60),
('Paring Knife', 'knives', 40),
('Bread Knife', 'knives', 35),
('Knife Sharpener', 'knives', 30),
('Cutting Board', 'knives', 25),
('Knife Set', 'knives', 20),
('Santoku Knife', 'knives', 15),
('Utility Knife', 'knives', 10),

-- Bakeware
('Sheet Pan', 'bakeware', 55),
('Mixing Bowls', 'bakeware', 45),
('Measuring Cups', 'bakeware', 40),
('Stand Mixer', 'bakeware', 35),
('Loaf Pan', 'bakeware', 30),
('Muffin Tin', 'bakeware', 25),
('Baking Sheet', 'bakeware', 20),
('Cake Pan', 'bakeware', 15)
ON CONFLICT (query_term, category) DO NOTHING;
```

### Step 3: Verify
After running the SQL, the dropdowns will immediately start working. You can verify by:

1. Hovering over COOKWARE, KNIVES, or BAKEWARE in the navigation
2. The dropdown should appear with 8 popular search terms
3. Clicking a term should trigger a search
4. The backend will track each search and update the counts

## Current Error (Before Migration)
If you check the backend logs, you'll see:
```
Error fetching popular searches: {'message': "Could not find the table 'public.popular_search_terms' in the schema cache"
```

This error will disappear once the migration is run.

## Files Modified
- `/backend/migrations/001_create_popular_search_terms.sql` - Migration SQL
- `/backend/popular_search_service.py` - Service layer (NEW)
- `/backend/main.py` - Added 2 new endpoints
- `/frontend/lib/api.ts` - API client functions
- `/frontend/components/NavigationDropdown.tsx` - Dropdown component (NEW)
- `/frontend/components/Header.tsx` - Updated navigation
- `/frontend/app/page.tsx` - Connected search handler

## What Happens After Migration
- Dropdowns will display the seeded popular searches
- As users search, the counts will update automatically
- The most searched terms will bubble to the top
- Cache refreshes every hour to reflect new data
