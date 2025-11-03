-- Kenny Gem Finder Database Schema Migration
-- Updated to match current Product model with new fields

-- Drop existing tables if they exist (careful in production!)
DROP TABLE IF EXISTS product_search_results CASCADE;
DROP TABLE IF EXISTS user_comparisons CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS search_queries CASCADE;

-- Search Queries Table
CREATE TABLE search_queries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    original_query TEXT NOT NULL,
    normalized_query TEXT NOT NULL,
    tier_preference TEXT,
    max_price DECIMAL(10, 2),
    context JSONB DEFAULT '{}',
    sources_searched TEXT[],
    search_queries_used TEXT[],
    processing_time_seconds DECIMAL(10, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_accessed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Products Table (Updated Schema)
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    brand TEXT NOT NULL,
    tier TEXT NOT NULL CHECK (tier IN ('good', 'better', 'best')),
    category TEXT NOT NULL DEFAULT 'general',

    -- Value metrics (flattened from ValueMetrics object)
    price DECIMAL(10, 2) NOT NULL,
    expected_lifespan_years DECIMAL(5, 1) NOT NULL,
    cost_per_year DECIMAL(10, 2) NOT NULL,
    cost_per_day DECIMAL(10, 4) NOT NULL,

    -- Product details
    why_its_a_gem TEXT,
    key_features JSONB DEFAULT '[]',
    materials JSONB DEFAULT '[]',
    characteristics JSONB DEFAULT '[]',
    trade_offs JSONB DEFAULT '[]',
    best_for TEXT,
    web_sources JSONB DEFAULT '[]',
    maintenance_level TEXT DEFAULT 'Medium',

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Unique constraint on name + brand
    UNIQUE(name, brand)
);

-- Product Search Results (Junction Table)
CREATE TABLE product_search_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    search_query_id UUID NOT NULL REFERENCES search_queries(id) ON DELETE CASCADE,
    tier TEXT NOT NULL CHECK (tier IN ('good', 'better', 'best')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Unique constraint to prevent duplicate links
    UNIQUE(product_id, search_query_id)
);

-- User Comparisons Table
CREATE TABLE user_comparisons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_ids UUID[] NOT NULL,
    session_id TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for better query performance
CREATE INDEX idx_search_queries_normalized ON search_queries(normalized_query);
CREATE INDEX idx_search_queries_created_at ON search_queries(created_at DESC);
CREATE INDEX idx_products_tier ON products(tier);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_price ON products(price);
CREATE INDEX idx_product_search_results_product_id ON product_search_results(product_id);
CREATE INDEX idx_product_search_results_search_query_id ON product_search_results(search_query_id);

-- Updated_at trigger for products table
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Grant necessary permissions (adjust if using different roles)
-- ALTER TABLE search_queries ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE products ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE product_search_results ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE user_comparisons ENABLE ROW LEVEL SECURITY;

-- Create policies for public access (adjust based on your security requirements)
-- Example: Allow anonymous users to read products but not modify
-- CREATE POLICY "Allow public read access" ON products FOR SELECT USING (true);
-- CREATE POLICY "Allow public read access" ON search_queries FOR SELECT USING (true);

COMMENT ON TABLE search_queries IS 'Stores user search queries with context and metadata';
COMMENT ON TABLE products IS 'Stores kitchen product recommendations with full details';
COMMENT ON TABLE product_search_results IS 'Junction table linking products to searches';
COMMENT ON TABLE user_comparisons IS 'Stores user product comparison sessions';
