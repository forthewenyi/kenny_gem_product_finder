-- Migration: Create popular_search_terms table for dynamic navigation
-- This table tracks search term frequency to power the dropdown menus

CREATE TABLE IF NOT EXISTS popular_search_terms (
  id BIGSERIAL PRIMARY KEY,
  query_term TEXT NOT NULL,
  category TEXT NOT NULL CHECK (category IN ('cookware', 'knives', 'bakeware')),
  search_count INTEGER DEFAULT 1,
  last_searched TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  CONSTRAINT unique_term_category UNIQUE(query_term, category)
);

-- Index for fast queries by category and count
CREATE INDEX IF NOT EXISTS idx_popular_search_terms_category_count
ON popular_search_terms(category, search_count DESC);

-- Seed data for cold start
INSERT INTO popular_search_terms (query_term, category, search_count) VALUES
-- Cookware
('Cast Iron Skillet', 'cookware', 50),
('Stainless Steel Pan', 'cookware', 45),
('Dutch Oven', 'cookware', 40),
('Non-Stick Pan', 'cookware', 35),
('Wok', 'cookware', 30),
('Saucepan Set', 'cookware', 25),
('Roasting Pan', 'cookware', 20),
('Grill Pan', 'cookware', 15),

-- Knives
('Chef''s Knife', 'knives', 60),
('Paring Knife', 'knives', 40),
('Bread Knife', 'knives', 35),
('Knife Sharpener', 'knives', 30),
('Cutting Board', 'knives', 25),
('Knife Set', 'knives', 20),
('Santoku Knife', 'knives', 15),
('Utility Knife', 'knives', 10),

-- Bakeware
('Sheet Pan', 'bakeware', 55),
('Mixing Bowls', 'bakeware', 45),
('Measuring Cups', 'bakeware', 40),
('Stand Mixer', 'bakeware', 35),
('Loaf Pan', 'bakeware', 30),
('Muffin Tin', 'bakeware', 25),
('Baking Sheet', 'bakeware', 20),
('Cake Pan', 'bakeware', 15)
ON CONFLICT (query_term, category) DO NOTHING;
