-- Add missing fields to products table for durability_data and practical_metrics
-- SIMPLE VERSION (no indexes)

-- Add durability_data column (JSONB to store nested DurabilityData object)
ALTER TABLE products
ADD COLUMN IF NOT EXISTS durability_data JSONB DEFAULT NULL;

-- Add practical_metrics column (JSONB to store nested PracticalMetrics object)
ALTER TABLE products
ADD COLUMN IF NOT EXISTS practical_metrics JSONB DEFAULT NULL;

-- Add comments for documentation
COMMENT ON COLUMN products.durability_data IS 'Durability data from user reports and research: score, lifespan, failure points, repairability, etc.';
COMMENT ON COLUMN products.practical_metrics IS 'Practical usage metrics: cleaning time, setup, learning curve, weight, dishwasher safe, etc.';
