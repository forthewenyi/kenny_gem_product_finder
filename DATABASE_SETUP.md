# Database Setup Guide - Kenny Gem Finder

## Overview

Kenny Gem Finder now includes **Supabase PostgreSQL database caching** to reduce API calls and improve performance. This guide will help you set up the database schema.

---

## Step 1: Create Database Tables

1. **Go to your Supabase Dashboard**: https://supabase.com/dashboard
2. **Navigate to SQL Editor**: Click on "SQL Editor" in the left sidebar
3. **Run the schema**: Copy the entire contents of `backend/database_schema.sql` and paste it into the SQL Editor
4. **Execute**: Click "Run" to create all tables, indexes, and policies

---

## Database Schema

### Tables Created

#### `products`
Caches product information from AI searches
- `id` (UUID) - Primary key
- `product_name`, `brand`, `price`, `expected_lifespan_years`
- `tier` (good/better/best)
- `cost_per_year`, `cost_per_day` - Calculated value metrics
- `why_gem`, `key_features`, `trade_offs`, `best_for`
- `web_sources` (JSONB) - Array of source URLs
- `category`, `maintenance_level`
- Timestamps: `created_at`, `updated_at`

#### `search_queries`
Caches search queries and their results
- `id` (UUID) - Primary key
- `original_query`, `normalized_query`
- `tier_preference`, `max_price`
- `context` (JSONB) - User context
- `result_product_ids` (JSONB)
- `sources_searched`, `search_queries_used` (JSONB arrays)
- `educational_insights` (JSONB array)
- `processing_time_seconds`
- Timestamps: `created_at`, `last_accessed_at`

#### `product_search_results`
Junction table linking products to searches (many-to-many)
- `product_id` → products(id)
- `search_query_id` → search_queries(id)
- `tier` - Tier classification for this search

#### `user_comparisons`
Tracks product comparison sessions
- `id` (UUID) - Primary key
- `product_ids` (JSONB array)
- `session_id`
- Timestamp: `created_at`

---

## Features

### Caching Strategy

**24-Hour Cache TTL**
- Search results are cached for 24 hours
- Same query returns cached results instantly
- Cache is automatically invalidated after 24 hours

**Cache Matching**
- Queries are normalized (lowercase, trimmed)
- Exact match on query text
- Optional filters: `tier_preference`, `max_price`

### How It Works

1. **User searches** for "chef's knife for beginners"
2. **Backend checks cache** first
   - ✓ **Cache hit**: Returns results instantly (0.0s processing time)
   - ✗ **Cache miss**: Calls Tavily API + OpenAI, then caches result
3. **Results are cached** with products and metadata
4. **Next search** for same query returns from cache

### Performance Benefits

| Scenario | Without Cache | With Cache |
|----------|---------------|------------|
| First search | ~10-30s | ~10-30s |
| Repeat search | ~10-30s | ~0.1s ⚡ |
| API costs | $0.02-0.05 | $0.00 |

---

## Environment Variables

Already configured in your `.env` files:

**Backend (`backend/.env`)**
```bash
SUPABASE_URL=https://nuzndrucvjyvezgafgcd.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Frontend (`frontend/.env.local`)**
```bash
NEXT_PUBLIC_SUPABASE_URL=https://nuzndrucvjyvezgafgcd.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## Security

### Row Level Security (RLS)

All tables have RLS enabled with policies:
- **Read access**: All users (anonymous OK)
- **Insert access**: All users (for caching)
- **Update access**: Limited (only search_queries for `last_accessed_at`)

This allows public caching while maintaining security.

---

## Monitoring Cache Performance

Check if cache is working:

1. **Backend logs**: Look for these messages:
   ```
   ✓ Database caching enabled
   🔍 Checking cache for query: 'chef's knife'
   ✗ Cache miss. Performing fresh search...
   💾 Caching search results to database...
   ✓ Results cached successfully
   ```

2. **Frontend UI**: Cached results show "⚡ Cached" badge

3. **Supabase Dashboard**:
   - Go to Table Editor
   - Check `products` and `search_queries` tables
   - See cached data

---

## Querying the Database

### Useful SQL Queries

**View all cached products:**
```sql
SELECT product_name, brand, price, tier, created_at
FROM products
ORDER BY created_at DESC;
```

**View cached searches:**
```sql
SELECT original_query, created_at, processing_time_seconds
FROM search_queries
ORDER BY created_at DESC;
```

**See search results with products:**
```sql
SELECT * FROM search_results_with_products
LIMIT 10;
```

**Clear old cache (older than 7 days):**
```sql
DELETE FROM search_queries
WHERE created_at < NOW() - INTERVAL '7 days';
```

---

## Troubleshooting

### Cache not working?

1. **Check backend logs** for database errors
2. **Verify credentials** in `.env` file
3. **Test connection**:
   ```bash
   cd backend
   source venv/bin/activate
   python -c "from database_service import DatabaseService; db = DatabaseService(); print('✓ Connected')"
   ```

### Database connection failed?

- Verify `SUPABASE_URL` and `SUPABASE_ANON_KEY` are correct
- Check Supabase project is active
- Ensure tables were created (run schema.sql again)

### Cache always missing?

- Check query normalization (case-sensitive?)
- Verify 24-hour TTL hasn't expired
- Check `search_queries` table has data

---

## Next Steps

✅ **Database schema created**
✅ **Caching enabled in backend**
✅ **Frontend connected**

**Now you can:**
1. Run a search query
2. Run the **same** query again - see instant results!
3. Monitor cache hits in Supabase Dashboard
4. Analyze query patterns and popular products

---

## Database Maintenance

### Recommended Schedule

**Weekly:**
- Review popular searches in `search_queries`
- Monitor database size

**Monthly:**
- Clear old cache (> 30 days)
- Analyze product performance
- Update tier classifications if needed

**As Needed:**
- Manually clear specific cached queries
- Update product information
- Add new product categories

---

**Database caching is now live! 🎉**

Your API costs will decrease significantly as searches are cached and reused.
