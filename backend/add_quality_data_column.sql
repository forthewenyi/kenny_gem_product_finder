-- Migration: Add quality_data column to products table
-- This stores durability and quality metrics for products

ALTER TABLE products
ADD COLUMN IF NOT EXISTS quality_data JSONB;

-- Add a comment to the column for documentation
COMMENT ON COLUMN products.quality_data IS
'Quality and durability metrics: durability_score, durability_evidence, common_failure_points, category_relative_tier, repairability_score, warranty_years';

-- Create an index for faster queries on the JSONB column (optional, for performance)
CREATE INDEX IF NOT EXISTS idx_products_quality_data
ON products USING GIN (quality_data);

-- Example of what this column will contain:
-- {
--   "durability_score": 8.5,
--   "durability_evidence": "Users report 10+ years of daily use...",
--   "common_failure_points": ["handle loosening after 5 years"],
--   "category_relative_tier": "premium",
--   "repairability_score": 7,
--   "warranty_years": 10
-- }
