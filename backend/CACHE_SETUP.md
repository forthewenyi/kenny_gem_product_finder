# Database Caching Setup Guide

## Overview

Kenny Gem Finder now supports **Supabase PostgreSQL caching** to dramatically speed up repeat searches and reduce API costs.

### Benefits:
- **10x faster**: Cache hits return in <1 second instead of 30-40 seconds
- **Cost savings**: Eliminates repeat Google Search API calls ($5/1000 queries after free tier)
- **Reduced load**: Less strain on Gemini AI API
- **Better UX**: Instant results for popular searches

---

## Current Status

✅ **Database Connection**: ACTIVE
✅ **Supabase Credentials**: Configured in `.env`
✅ **Code Integration**: Enabled in `main.py`
⚠️  **Schema**: May need migration (see below)

---

## How Caching Works

### 1. First Search (Cache Miss)
```
User searches "chef knife"
    ↓
Backend checks cache → NOT FOUND
    ↓
Performs full AI search (30-40s):
  - Generate 10 contextual queries
  - Search Google Custom Search API
  - AI synthesizes 9 products
    ↓
Saves results to Supabase
    ↓
Returns results to user
```

### 2. Repeat Search (Cache Hit)
```
User searches "chef knife" again
    ↓
Backend checks cache → FOUND!
    ↓
Returns cached results (<1s)
    ↓
User gets instant results
```

### 3. Cache Expiration
- **TTL**: 24 hours (configurable)
- Expired caches are automatically skipped
- Fresh search is performed if cache is stale

---

## Setup Instructions

### Step 1: Verify Connection

The database is already connected! Your `.env` file has:
```bash
SUPABASE_URL=https://nuzndrucvjyvezgafgcd.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIs...
```

Test the connection:
```bash
python3 test_db_connection.py
```

Expected output:
```
✅ DatabaseService initialized successfully!
✅ Products table exists!
✅ Search queries table exists!
```

---

### Step 2: Verify/Update Schema

The schema may need updating to match the current Product model.

**Option A: Run Migration SQL (Recommended)**

1. Go to your Supabase dashboard:
   https://supabase.com/dashboard/project/nuzndrucvjyvezgafgcd

2. Navigate to: **SQL Editor** (left sidebar)

3. Create a new query and paste the contents of:
   `supabase_schema_migration.sql`

4. Click **Run** to execute the migration

This will:
- Create tables with the correct schema
- Add indexes for performance
- Set up foreign keys and constraints

**Option B: Test Without Migration**

The code is designed to work with the existing schema. Just try a search:

1. Open http://localhost:3000
2. Search for "chef knife"
3. Wait 30-40 seconds for results
4. Check the backend logs for cache-related messages

---

### Step 3: Verify Caching Works

After running a search, check if it was cached:

```bash
python3 test_schema_fields.py
```

This will show if products were saved to the database.

Then search for the same term again - it should return instantly!

---

## Schema Details

### Tables Created:

1. **search_queries**
   - Stores search queries with context
   - Tracks when searches were performed
   - Links to products via junction table

2. **products**
   - Stores product details (name, brand, price, etc.)
   - Includes value metrics (cost per year, lifespan)
   - Contains characteristics, materials, trade-offs
   - Stores web sources (Reddit, reviews)

3. **product_search_results**
   - Junction table linking products to searches
   - Tracks which tier (good/better/best) each product was in

4. **user_comparisons**
   - Stores product comparison sessions
   - For future feature: save comparisons

### Key Fields:

```sql
products:
  - id (UUID, primary key)
  - name (TEXT)
  - brand (TEXT)
  - tier (TEXT: good/better/best)
  - category (TEXT: cookware, knives, bakeware)
  - price, cost_per_year, cost_per_day
  - characteristics (JSONB array)
  - materials (JSONB array)
  - key_features (JSONB array)
  - trade_offs (JSONB array)
  - web_sources (JSONB array)
  - why_its_a_gem (TEXT)
  - maintenance_level (TEXT)
  - created_at, updated_at
```

---

## Monitoring & Debugging

### Check Cache Status

Look for these messages in backend logs:

**Cache Hit** (instant results):
```
🔍 Checking cache for query: 'chef knife'
✓ Cache hit! Returning cached results
```

**Cache Miss** (fresh search):
```
🔍 Checking cache for query: 'dutch oven'
✗ Cache miss. Performing fresh search...
```

**Cache Disabled** (if error):
```
⚠️  Database caching disabled: connection failed
```

### View Cached Data

Connect to Supabase and query:

```sql
-- See all cached searches
SELECT original_query, created_at, last_accessed_at
FROM search_queries
ORDER BY created_at DESC;

-- See all cached products
SELECT name, brand, tier, price
FROM products
ORDER BY created_at DESC;

-- See cache hit count
SELECT
    sq.original_query,
    COUNT(DISTINCT psr.product_id) as product_count,
    sq.created_at as first_search,
    sq.last_accessed_at as last_accessed
FROM search_queries sq
LEFT JOIN product_search_results psr ON sq.id = psr.search_query_id
GROUP BY sq.id
ORDER BY sq.last_accessed_at DESC;
```

---

## Configuration Options

Edit `database_service.py` to customize:

### Cache TTL (Time To Live)

```python
# Line 25 in database_service.py
self.cache_ttl_hours = 24  # Change to 12, 48, etc.
```

### Disable Caching

In `main.py`, line 41:

```python
# To disable caching
db_service = None
```

Or remove Supabase credentials from `.env`

---

## Troubleshooting

### Issue: Cache not working

**Symptom**: Every search takes 30-40s
**Check**:
1. Look for "Cache hit" messages in logs
2. Run `test_db_connection.py`
3. Check if products are being saved:
   ```bash
   python3 test_schema_fields.py
   ```

**Fix**:
- Ensure Supabase project is active
- Run migration SQL
- Check `.env` credentials

### Issue: Schema mismatch errors

**Symptom**: Errors like "column 'name' does not exist"
**Fix**: Run `supabase_schema_migration.sql` in Supabase SQL Editor

### Issue: Slow cache queries

**Symptom**: Cache hits still take 2-5 seconds
**Fix**:
- Ensure indexes are created (included in migration SQL)
- Check Supabase dashboard for performance issues
- Consider upgrading Supabase plan

---

## Performance Metrics

### Expected Performance:

| Scenario | Time | API Calls |
|----------|------|-----------|
| First search (cache miss) | 30-40s | ~10 Google Search + 2-3 Gemini |
| Repeat search (cache hit) | <1s | 0 API calls |
| Expired cache search | 30-40s | ~10 Google Search + 2-3 Gemini |

### Cost Savings Example:

If 100 users search "chef knife":
- **Without cache**: 100 × $0.005 = $0.50
- **With cache**: 1 × $0.005 = $0.005
- **Savings**: $0.495 (99% reduction)

---

## Next Steps

1. ✅ Connection is working
2. ⚠️  Run migration SQL (recommended)
3. 🧪 Test with a search
4. 📊 Monitor cache hit rate
5. 🚀 Enjoy faster searches!

## Files Reference

- `database_service.py` - Cache implementation
- `supabase_schema_migration.sql` - Database schema
- `test_db_connection.py` - Connection test
- `test_schema_fields.py` - Schema verification
- `.env` - Credentials configuration
