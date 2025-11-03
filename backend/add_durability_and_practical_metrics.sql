-- Add missing fields to products table for durability_data and practical_metrics

-- Add durability_data column (JSONB to store nested DurabilityData object)
ALTER TABLE products
ADD COLUMN IF NOT EXISTS durability_data JSONB DEFAULT NULL;

-- Add practical_metrics column (JSONB to store nested PracticalMetrics object)
ALTER TABLE products
ADD COLUMN IF NOT EXISTS practical_metrics JSONB DEFAULT NULL;

-- Add comments for documentation
COMMENT ON COLUMN products.durability_data IS 'Durability data from user reports and research: score, lifespan, failure points, repairability, etc.';
COMMENT ON COLUMN products.practical_metrics IS 'Practical usage metrics: cleaning time, setup, learning curve, weight, dishwasher safe, etc.';

-- Create indexes for common queries (using functional indexes)
CREATE INDEX IF NOT EXISTS idx_products_durability_score
ON products (((durability_data->>'score')::int));

CREATE INDEX IF NOT EXISTS idx_products_lifespan
ON products (((durability_data->>'average_lifespan_years')::float));

-- Example durability_data structure:
-- {
--   "score": 75,
--   "average_lifespan_years": 10.5,
--   "still_working_after_5years_percent": 85,
--   "total_user_reports": 234,
--   "common_failure_points": ["coating peels", "handle loosens"],
--   "repairability_score": 60,
--   "material_quality_indicators": ["solid construction", "heavy gauge steel"],
--   "data_sources": ["https://reddit.com/..."]
-- }

-- Example practical_metrics structure:
-- {
--   "cleaning_time_minutes": 10,
--   "cleaning_details": "Hand wash with mild soap",
--   "setup_time": "Ready",
--   "setup_details": "No assembly required",
--   "learning_curve": "Medium",
--   "learning_details": "Takes a few uses to master temperature control",
--   "maintenance_level": "Low",
--   "maintenance_details": "Occasional re-seasoning needed",
--   "weight_lbs": 8.5,
--   "weight_notes": "Heavy but manageable",
--   "dishwasher_safe": false,
--   "oven_safe": true,
--   "oven_max_temp": 500
-- }
