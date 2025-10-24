-- Add Durability Score fields to products table
-- Run this in Supabase SQL Editor after the initial schema

-- Add durability score columns
ALTER TABLE products
ADD COLUMN IF NOT EXISTS durability_score INTEGER CHECK (durability_score >= 0 AND durability_score <= 100),
ADD COLUMN IF NOT EXISTS longevity_score INTEGER CHECK (longevity_score >= 0 AND longevity_score <= 40),
ADD COLUMN IF NOT EXISTS failure_rate_score INTEGER CHECK (failure_rate_score >= 0 AND failure_rate_score <= 25),
ADD COLUMN IF NOT EXISTS repairability_score INTEGER CHECK (repairability_score >= 0 AND repairability_score <= 20),
ADD COLUMN IF NOT EXISTS material_quality_score INTEGER CHECK (material_quality_score >= 0 AND material_quality_score <= 15);

-- Add durability metadata columns
ALTER TABLE products
ADD COLUMN IF NOT EXISTS durability_data JSONB DEFAULT '{}'::jsonb;

-- Create index on durability score for sorting
CREATE INDEX IF NOT EXISTS idx_products_durability_score ON products(durability_score DESC);

-- Add comments
COMMENT ON COLUMN products.durability_score IS 'Overall durability score (0-100)';
COMMENT ON COLUMN products.longevity_score IS 'Longevity reports component (0-40 points)';
COMMENT ON COLUMN products.failure_rate_score IS 'Failure rate component (0-25 points)';
COMMENT ON COLUMN products.repairability_score IS 'Repairability component (0-20 points)';
COMMENT ON COLUMN products.material_quality_score IS 'Material quality component (0-15 points)';
COMMENT ON COLUMN products.durability_data IS 'Additional durability metadata (years in use, failure %, etc.)';

-- Create a view for high durability products
CREATE OR REPLACE VIEW high_durability_products AS
SELECT
    product_name,
    brand,
    tier,
    durability_score,
    price,
    cost_per_year,
    category
FROM products
WHERE durability_score >= 80
ORDER BY durability_score DESC, cost_per_year ASC;

COMMENT ON VIEW high_durability_products IS 'Products with durability score >= 80';
