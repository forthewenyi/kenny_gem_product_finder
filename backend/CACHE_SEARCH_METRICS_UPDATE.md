# Cache Search Metrics Update

## Problem
When users got cached search results, the search transparency metrics showed **zeros** instead of the actual research work done:
- AI Search Queries: 0 (should show actual number like 2)
- Reviews Analyzed: 0 (should show actual number like 40)
- Products Evaluated: 0 (should show actual number like 6)

This made cached results appear less trustworthy and created confusion about whether the AI actually did research.

## Solution
Store and retrieve `real_search_metrics` from the Supabase cache so users see the original research work even on cache hits.

## Changes Made

### 1. Updated `database_service.py`

#### Saving Metrics (lines 268-291)
Added serialization of `real_search_metrics` when caching:
```python
# Serialize real_search_metrics if present
real_search_metrics_json = None
if search_response.real_search_metrics:
    rsm = search_response.real_search_metrics
    real_search_metrics_json = {
        "total_sources_analyzed": rsm.total_sources_analyzed,
        "reddit_threads": rsm.reddit_threads,
        "expert_reviews": rsm.expert_reviews,
        "search_queries_executed": rsm.search_queries_executed,
        "search_queries": rsm.search_queries,
        "unique_sources": rsm.unique_sources
    }
```

#### Retrieving Metrics (lines 245-269)
Added deserialization of `real_search_metrics` when returning cached results:
```python
# Reconstruct real_search_metrics if present
from models import RealSearchMetrics
real_search_metrics = None
if cached_search.get("real_search_metrics"):
    rsm = cached_search["real_search_metrics"]
    real_search_metrics = RealSearchMetrics(
        total_sources_analyzed=rsm.get("total_sources_analyzed", 0),
        reddit_threads=rsm.get("reddit_threads", 0),
        expert_reviews=rsm.get("expert_reviews", 0),
        search_queries_executed=rsm.get("search_queries_executed", 0),
        search_queries=rsm.get("search_queries", []),
        unique_sources=rsm.get("unique_sources", 0)
    )
```

### 2. Database Migration

Created SQL migration file: `add_real_search_metrics_column.sql`

Adds JSONB column to `search_queries` table:
```sql
ALTER TABLE search_queries
ADD COLUMN IF NOT EXISTS real_search_metrics JSONB;
```

### 3. Migration Helper

Created `run_migration.py` to display the SQL that needs to be run in Supabase.

## How to Apply This Update

### Step 1: Run Database Migration
1. Go to https://supabase.com
2. Select your project
3. Go to **SQL Editor**
4. Copy the SQL from `add_real_search_metrics_column.sql` (or run `uv run python run_migration.py` to see it)
5. Click **Run**

### Step 2: Clear Old Cache (Optional but Recommended)
Old cache entries won't have `real_search_metrics`, so they'll still show zeros. You can:

**Option A: Let them expire naturally** (24-168 hours based on popularity)

**Option B: Clear all cache manually:**
```sql
DELETE FROM product_search_results;
DELETE FROM search_queries;
```

### Step 3: Test
1. Do a fresh search (not cached) - should show actual metrics
2. Repeat the same search (cached) - should STILL show the same metrics!

## Before vs After

### Before (Cached Result):
```
Search Transparency (Cached)
Kenny generated 0 AI search queries, analyzed 0 expert sources and user reviews
```
**Result**: Users think cached = no research done

### After (Cached Result):
```
Search Transparency (Cached)
Kenny generated 2 AI search queries, analyzed 40 expert sources and user reviews
```
**Result**: Users see the actual research work and trust the recommendations

## Backward Compatibility

✅ **Existing cache entries work fine** - they just won't have metrics (will show zeros)
✅ **New searches will automatically cache metrics** - no code changes needed after migration
✅ **No data loss** - old cache entries remain functional

## Future Improvements

This update addresses issue #2 from the cache analysis. Still outstanding:

1. **Cache key doesn't include user characteristics** - personalization may be ignored for cached results
3. **Buying characteristics not cached** - regenerated on every request
4. **README doesn't document caching behavior** - needs update

## Files Modified

- `database_service.py` - Added serialization/deserialization of `real_search_metrics`
- `add_real_search_metrics_column.sql` - Database migration
- `run_migration.py` - Helper to display migration SQL
- `CACHE_SEARCH_METRICS_UPDATE.md` - This documentation
