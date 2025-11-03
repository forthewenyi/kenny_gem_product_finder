-- Add cache tracking fields to search_queries table

-- Add access_count field to track query popularity
ALTER TABLE search_queries
ADD COLUMN IF NOT EXISTS access_count INTEGER DEFAULT 0;

-- Create index on access_count for fast lookups
CREATE INDEX IF NOT EXISTS idx_search_queries_access_count
ON search_queries(access_count DESC);

-- Create a view for cache statistics
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

-- Comment the new field
COMMENT ON COLUMN search_queries.access_count IS 'Number of times this cached query has been accessed (for dynamic TTL)';
