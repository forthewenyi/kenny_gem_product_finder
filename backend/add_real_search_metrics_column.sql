-- Migration: Add real_search_metrics column to search_queries table
-- This stores the actual search transparency metrics (queries executed, sources analyzed, etc.)
-- so that cached results can show users the original research work done

ALTER TABLE search_queries
ADD COLUMN IF NOT EXISTS real_search_metrics JSONB;

-- Add a comment to the column for documentation
COMMENT ON COLUMN search_queries.real_search_metrics IS
'Search transparency metrics showing the actual research work: total_sources_analyzed, reddit_threads, expert_reviews, search_queries_executed, search_queries array, unique_sources';

-- Create an index for faster queries on the JSONB column (optional, for performance)
CREATE INDEX IF NOT EXISTS idx_search_queries_real_search_metrics
ON search_queries USING GIN (real_search_metrics);

-- Example of what this column will contain:
-- {
--   "total_sources_analyzed": 40,
--   "reddit_threads": 5,
--   "expert_reviews": 8,
--   "search_queries_executed": 2,
--   "search_queries": ["best dutch oven reddit 2024", "dutch oven wirecutter review"],
--   "unique_sources": 35
-- }
