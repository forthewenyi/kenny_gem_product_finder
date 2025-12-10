-- Migration: Rename trade_offs column to drawbacks
-- Run this in your Supabase SQL Editor

-- Rename the column in products table
ALTER TABLE products
RENAME COLUMN trade_offs TO drawbacks;

-- Update any views that reference the old column
DROP VIEW IF EXISTS search_results_with_products;

CREATE OR REPLACE VIEW search_results_with_products AS
SELECT
    sq.id AS search_id,
    sq.original_query,
    sq.normalized_query,
    sq.created_at AS search_date,
    sq.last_accessed_at,
    sq.tier_preference,
    sq.max_price,
    sq.processing_time_seconds,
    psr.tier,
    p.id AS product_id,
    p.name,  -- Fixed: was product_name
    p.brand,
    p.price,
    p.expected_lifespan_years,
    p.cost_per_year,
    p.cost_per_day,
    p.why_its_a_gem,  -- Fixed: was why_gem
    p.key_features,
    p.drawbacks,  -- Updated from trade_offs
    p.best_for,
    p.web_sources,
    p.maintenance_level,
    p.category
FROM search_queries sq
JOIN product_search_results psr ON psr.search_query_id = sq.id
JOIN products p ON p.id = psr.product_id;

-- Verify the migration
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'products'
  AND column_name IN ('trade_offs', 'drawbacks');
