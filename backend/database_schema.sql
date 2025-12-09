-- Kenny Gem Finder Database Schema
-- Run this in your Supabase SQL Editor

-- Products table - cache of product data
CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,  -- Fixed: actual column name is 'name', not 'product_name'
    brand TEXT,
    price DECIMAL(10, 2) NOT NULL,
    expected_lifespan_years DECIMAL(10, 2) NOT NULL,  -- Fixed: uses DECIMAL to support ranges like 15.5
    tier TEXT NOT NULL CHECK (tier IN ('good', 'better', 'best')),
    cost_per_year DECIMAL(10, 2),
    cost_per_day DECIMAL(10, 4),
    why_its_a_gem TEXT,  -- Fixed: actual column name
    key_features JSONB DEFAULT '[]'::jsonb,
    materials JSONB DEFAULT '[]'::jsonb,  -- Added: missing from original schema
    characteristics JSONB DEFAULT '[]'::jsonb,  -- Added: missing from original schema
    drawbacks JSONB DEFAULT '[]'::jsonb,  -- Fixed: JSONB array, renamed from trade_offs
    best_for TEXT,
    web_sources JSONB DEFAULT '[]'::jsonb,
    maintenance_level TEXT,
    category TEXT,
    quality_data JSONB,  -- Added: quality metrics
    practical_metrics JSONB,  -- Added: practical usage metrics
    professional_reviews JSONB DEFAULT '[]'::jsonb,  -- Added: missing field
    purchase_links JSONB DEFAULT '[]'::jsonb,  -- Added: missing field
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Search queries table - cache search queries and their results
CREATE TABLE IF NOT EXISTS search_queries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    original_query TEXT NOT NULL,
    normalized_query TEXT NOT NULL,
    tier_preference TEXT CHECK (tier_preference IN ('good', 'better', 'best')),
    max_price DECIMAL(10, 2),
    context JSONB DEFAULT '{}'::jsonb,
    result_product_ids JSONB DEFAULT '[]'::jsonb,
    sources_searched JSONB DEFAULT '[]'::jsonb,
    search_queries_used JSONB DEFAULT '[]'::jsonb,
    educational_insights JSONB DEFAULT '[]'::jsonb,
    processing_time_seconds DECIMAL(10, 3),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_accessed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Product-Search junction table (many-to-many)
CREATE TABLE IF NOT EXISTS product_search_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    search_query_id UUID REFERENCES search_queries(id) ON DELETE CASCADE,
    tier TEXT NOT NULL CHECK (tier IN ('good', 'better', 'best')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(product_id, search_query_id)
);

-- User comparisons table - track product comparisons
CREATE TABLE IF NOT EXISTS user_comparisons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_ids JSONB NOT NULL,
    session_id TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_products_tier ON products(tier);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_price ON products(price);
CREATE INDEX IF NOT EXISTS idx_products_tier_price ON products(tier, price);
CREATE INDEX IF NOT EXISTS idx_search_queries_normalized ON search_queries(normalized_query);
CREATE INDEX IF NOT EXISTS idx_search_queries_created_at ON search_queries(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_product_search_results_product_id ON product_search_results(product_id);
CREATE INDEX IF NOT EXISTS idx_product_search_results_search_id ON product_search_results(search_query_id);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update updated_at
DROP TRIGGER IF EXISTS update_products_updated_at ON products;
CREATE TRIGGER update_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Function to normalize search queries for better cache hits
CREATE OR REPLACE FUNCTION normalize_query(query TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN LOWER(TRIM(REGEXP_REPLACE(query, '\s+', ' ', 'g')));
END;
$$ LANGUAGE plpgsql;

-- View for easy search result retrieval
CREATE OR REPLACE VIEW search_results_with_products AS
SELECT
    sq.id AS search_id,
    sq.original_query,
    sq.normalized_query,
    sq.created_at AS search_date,
    sq.last_accessed_at,
    json_agg(
        json_build_object(
            'tier', psr.tier,
            'product', row_to_json(p.*)
        ) ORDER BY psr.tier, p.price
    ) AS results
FROM search_queries sq
JOIN product_search_results psr ON sq.id = psr.search_query_id
JOIN products p ON psr.product_id = p.id
GROUP BY sq.id;

-- Enable Row Level Security (RLS)
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE search_queries ENABLE ROW LEVEL SECURITY;
ALTER TABLE product_search_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_comparisons ENABLE ROW LEVEL SECURITY;

-- Create policies for public read access (anonymous users can read cached data)
CREATE POLICY "Enable read access for all users" ON products
    FOR SELECT USING (true);

CREATE POLICY "Enable read access for all users" ON search_queries
    FOR SELECT USING (true);

CREATE POLICY "Enable read access for all users" ON product_search_results
    FOR SELECT USING (true);

CREATE POLICY "Enable read access for all users" ON user_comparisons
    FOR SELECT USING (true);

-- Create policies for insert access (anonymous users can cache data)
CREATE POLICY "Enable insert for all users" ON products
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Enable insert for all users" ON search_queries
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Enable insert for all users" ON product_search_results
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Enable insert for all users" ON user_comparisons
    FOR INSERT WITH CHECK (true);

-- Update policy for search queries (to update last_accessed_at)
CREATE POLICY "Enable update for all users" ON search_queries
    FOR UPDATE USING (true);

COMMENT ON TABLE products IS 'Cached product data from AI searches';
COMMENT ON TABLE search_queries IS 'Cached search queries and metadata';
COMMENT ON TABLE product_search_results IS 'Junction table linking products to search queries';
COMMENT ON TABLE user_comparisons IS 'User product comparison sessions';
