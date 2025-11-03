# Cache Tracking and Dynamic TTL

## Overview

Kenny Gem Finder now implements intelligent cache tracking with dynamic TTL (Time To Live) based on query popularity. Popular searches are cached longer, while less popular searches expire faster to keep data fresh.

---

## Features

### 1. Dynamic TTL Based on Popularity

Cache expiration adapts to query access patterns:

| Access Count | Query Type | TTL | Example |
|--------------|------------|-----|---------|
| 0-1 accesses | Normal | 24 hours | First-time or rare searches |
| 2-4 accesses | Niche | 72 hours (3 days) | Moderately popular searches |
| 5+ accesses | Popular | 168 hours (1 week) | Frequently searched queries |

**Why this matters:**
- **Popular searches** (e.g., "cast iron skillet") get cached for 1 week - they change less frequently
- **Niche searches** (e.g., "ramen bowl set") get cached for 3 days - balanced freshness
- **Rare searches** (e.g., "truffle shaver") get cached for 24 hours - stay fresh

### 2. Access Count Tracking

Every cache hit increments the `access_count` field:
- First search: `access_count = 0` (initial cache)
- Second search: `access_count = 1` (first cache hit)
- Third search: `access_count = 2` (TTL increases to 72h)
- Sixth search: `access_count = 5` (TTL increases to 168h)

### 3. Cache Statistics View

SQL view provides real-time cache performance metrics:

```sql
SELECT * FROM cache_statistics;
```

Returns:
- `total_cached_queries`: Number of unique queries cached
- `total_cache_hits`: Total number of cache hits
- `avg_hits_per_query`: Average accesses per query
- `cache_hit_rate_percent`: Percentage of searches served from cache
- `popular_queries`: Count of queries with 5+ accesses
- `niche_queries`: Count of queries with 2-4 accesses
- `normal_queries`: Count of queries with 0-1 accesses

---

## How It Works

### Cache Hit Flow

```
User searches "chef knife"
    ↓
Check if query exists in cache
    ↓
Get access_count for this query
    ↓
Calculate TTL: _get_dynamic_ttl(access_count)
    ↓
Check if created_at + TTL > now()
    ↓
If valid:
  - Return cached results
  - Increment access_count
  - Update last_accessed_at
    ↓
If expired:
  - Perform fresh search
  - Cache new results with access_count=0
```

### Code Implementation

**1. Dynamic TTL Calculation** (`database_service.py:35-53`)

```python
def _get_dynamic_ttl(self, access_count: int) -> int:
    """Calculate dynamic cache TTL based on query popularity"""
    if access_count >= 5:
        # Popular search - cache for 1 week
        return self.cache_ttl_popular_hours  # 168
    elif access_count >= 2:
        # Niche search - cache for 3 days
        return self.cache_ttl_niche_hours    # 72
    else:
        # Normal/new search - cache for 24 hours
        return self.cache_ttl_normal_hours   # 24
```

**2. Cache Retrieval with Tracking** (`database_service.py:66-123`)

```python
async def get_cached_search(self, query: str, ...):
    # Get cached search and access_count
    access_count = cached_search.get("access_count", 0)

    # Calculate dynamic TTL
    ttl_hours = self._get_dynamic_ttl(access_count)
    cache_cutoff = datetime.now() - timedelta(hours=ttl_hours)

    # Check if cache is still valid
    if created_at < cache_cutoff:
        print(f"🕒 Cache expired (TTL: {ttl_hours}h, access_count: {access_count})")
        return None

    # Cache hit! Update tracking
    new_access_count = access_count + 1
    self.client.table("search_queries").update({
        "last_accessed_at": datetime.now().isoformat(),
        "access_count": new_access_count
    }).eq("id", cached_search["id"]).execute()

    print(f"✓ Cache hit (access #{new_access_count}, TTL: {ttl_hours}h)")
    return cached_results
```

**3. Cache Storage with Initialization** (`database_service.py:208-218`)

```python
search_data = {
    "original_query": query,
    "normalized_query": normalized_query,
    "tier_preference": tier_preference,
    "max_price": max_price,
    "context": context or {},
    "sources_searched": search_response.search_metadata.get("sources_searched", []),
    "search_queries_used": search_response.search_metadata.get("search_queries_used", []),
    "processing_time_seconds": search_response.processing_time_seconds,
    "access_count": 0  # Initialize access count for new cache entries
}
```

---

## Database Schema

### Table: `search_queries`

```sql
ALTER TABLE search_queries
ADD COLUMN IF NOT EXISTS access_count INTEGER DEFAULT 0;

-- Index for fast lookups
CREATE INDEX IF NOT EXISTS idx_search_queries_access_count
ON search_queries(access_count DESC);
```

### View: `cache_statistics`

```sql
CREATE OR REPLACE VIEW cache_statistics AS
SELECT
    COUNT(*) as total_cached_queries,
    SUM(access_count) as total_cache_hits,
    AVG(access_count) as avg_hits_per_query,
    COUNT(CASE WHEN access_count >= 5 THEN 1 END) as popular_queries,
    COUNT(CASE WHEN access_count BETWEEN 2 AND 4 THEN 1 END) as niche_queries,
    COUNT(CASE WHEN access_count < 2 THEN 1 END) as normal_queries,
    SUM(CASE WHEN access_count > 0 THEN access_count - 1 ELSE 0 END) as total_hits,
    COUNT(*) as total_searches,
    ROUND(
        100.0 * SUM(CASE WHEN access_count > 0 THEN access_count - 1 ELSE 0 END)
        / NULLIF(SUM(access_count), 0),
        2
    ) as cache_hit_rate_percent
FROM search_queries;
```

---

## Setup Instructions

### 1. Run SQL Migration

```bash
# In Supabase SQL Editor, run:
cat backend/add_cache_tracking.sql
```

This adds:
- `access_count` field to `search_queries` table
- Index on `access_count` for performance
- `cache_statistics` view for monitoring

### 2. Verify Cache Tracking

```bash
cd backend
python test_cache_statistics.py
```

Expected output:
```
📊 CACHE STATISTICS
===============================================================
✅ Cache Statistics:
  Total Cached Queries: 5
  Total Cache Hits: 12
  Average Hits Per Query: 2.40
  Cache Hit Rate: 58.33%

📈 Query Distribution:
  Popular Queries (5+ accesses, 168h TTL): 1
  Niche Queries (2-4 accesses, 72h TTL): 2
  Normal Queries (0-1 accesses, 24h TTL): 2

📋 RECENT SEARCHES
===============================================================
  [POPULAR] "cast iron skillet"
    Access count: 6 | TTL: 168h (1 week)
    Created: 2025-10-30 | Last accessed: 2025-10-30

  [NICHE] "chef knife"
    Access count: 3 | TTL: 72h (3 days)
    Created: 2025-10-29 | Last accessed: 2025-10-30
```

---

## Monitoring Cache Performance

### View Cache Statistics

```python
from supabase import create_client
import os

client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_ANON_KEY"))
stats = client.table("cache_statistics").select("*").execute()
print(stats.data)
```

### View Recent Searches with Access Counts

```python
searches = (
    client.table("search_queries")
    .select("original_query, access_count, created_at, last_accessed_at")
    .order("access_count", desc=True)
    .limit(10)
    .execute()
)

for search in searches.data:
    print(f"{search['original_query']}: {search['access_count']} accesses")
```

### Console Logs

When backend is running, you'll see cache tracking in logs:

```
✓ Cache hit for 'chef knife' (access #4, TTL: 72h)
🕒 Cache expired for 'air fryer' (TTL: 24h, access_count: 1)
✓ Cache hit for 'cast iron skillet' (access #7, TTL: 168h)
```

---

## Testing Dynamic TTL

### Test 1: Normal → Niche Transition (24h → 72h)

```bash
# First search (access_count=0, 24h TTL)
curl "http://localhost:8000/search?query=wok"

# Second search (access_count=1, 24h TTL)
curl "http://localhost:8000/search?query=wok"

# Third search (access_count=2, 72h TTL - UPGRADE!)
curl "http://localhost:8000/search?query=wok"
```

Expected logs:
```
Search 1: ❌ No cache (first search)
Search 2: ✓ Cache hit (access #1, TTL: 24h)
Search 3: ✓ Cache hit (access #2, TTL: 72h)  ← TTL increased!
```

### Test 2: Niche → Popular Transition (72h → 168h)

```bash
# Fourth search (access_count=3, 72h TTL)
curl "http://localhost:8000/search?query=wok"

# Fifth search (access_count=4, 72h TTL)
curl "http://localhost:8000/search?query=wok"

# Sixth search (access_count=5, 168h TTL - UPGRADE!)
curl "http://localhost:8000/search?query=wok"
```

Expected logs:
```
Search 4: ✓ Cache hit (access #3, TTL: 72h)
Search 5: ✓ Cache hit (access #4, TTL: 72h)
Search 6: ✓ Cache hit (access #5, TTL: 168h)  ← TTL increased!
```

---

## Benefits

### 1. Performance
- Popular searches stay cached longer (less API calls)
- Average cache hit rate improves over time
- Backend logs show cache performance in real-time

### 2. Freshness
- Rare searches expire quickly (24h)
- Ensures users see recent products and prices
- Balances performance with data accuracy

### 3. Cost Savings
- Fewer Google Custom Search API calls
- Fewer Gemini API calls
- Lower Supabase read/write operations

### 4. Visibility
- `cache_statistics` view provides insights
- Track which searches are most popular
- Monitor cache hit rate percentage
- Identify queries that need better caching

---

## Example Cache Evolution

A query's journey from "normal" to "popular":

```
Day 1, 10:00 AM - First search: "stand mixer"
  - access_count: 0
  - TTL: 24h
  - Expires: Day 2, 10:00 AM

Day 1, 2:00 PM - Second search: "stand mixer"
  - access_count: 1
  - TTL: 24h (still normal)
  - Expires: Day 2, 10:00 AM

Day 1, 5:00 PM - Third search: "stand mixer"
  - access_count: 2
  - TTL: 72h (upgraded to niche!)
  - Expires: Day 4, 5:00 PM

Day 2, 9:00 AM - Fourth search: "stand mixer"
  - access_count: 3
  - TTL: 72h (still niche)
  - Expires: Day 5, 9:00 AM

Day 2, 3:00 PM - Fifth search: "stand mixer"
  - access_count: 4
  - TTL: 72h (still niche)
  - Expires: Day 5, 3:00 PM

Day 3, 11:00 AM - Sixth search: "stand mixer"
  - access_count: 5
  - TTL: 168h (upgraded to popular!)
  - Expires: Day 10, 11:00 AM
```

---

## Troubleshooting

### Cache statistics view not found

**Error:**
```
relation "cache_statistics" does not exist
```

**Fix:**
```bash
# Run the SQL migration in Supabase SQL Editor
cat backend/add_cache_tracking.sql
```

### Access count not incrementing

**Check logs:**
```bash
tail -f /tmp/backend_restart.log | grep "Cache hit"
```

Should see:
```
✓ Cache hit for 'chef knife' (access #2, TTL: 24h)
✓ Cache hit for 'chef knife' (access #3, TTL: 72h)
```

### Cache hit rate is 0%

**Possible causes:**
- Cache is empty (no searches yet)
- All searches are unique (no repeated queries)
- Cache has expired (search again to rebuild)

**Fix:**
```bash
# Test by searching the same query multiple times
curl "http://localhost:8000/search?query=chef+knife"
sleep 2
curl "http://localhost:8000/search?query=chef+knife"
```

---

## Summary

✅ **Dynamic TTL:** Cache duration adapts to query popularity
✅ **Access Tracking:** Every cache hit increments access_count
✅ **Performance Monitoring:** cache_statistics view provides insights
✅ **Cost Optimization:** Popular searches cached up to 1 week
✅ **Data Freshness:** Rare searches expire after 24 hours

Your cache is now intelligent and self-optimizing! 🚀
