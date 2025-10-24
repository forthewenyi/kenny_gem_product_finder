// TypeScript types matching the backend API

export type ProductTier = 'good' | 'better' | 'best'

export interface ValueMetrics {
  upfront_price: number
  expected_lifespan_years: number
  cost_per_year: number
  cost_per_day: number
}

export interface WebSource {
  url: string
  title: string
  snippet: string
  relevance_score?: number | null
}

export interface Product {
  name: string
  brand: string
  tier: ProductTier
  category: string
  value_metrics: ValueMetrics
  key_features: string[]
  materials: string[]
  why_its_a_gem: string
  web_sources: WebSource[]
  reddit_mentions?: number | null
  professional_reviews: string[]
  maintenance_level: string
  purchase_links: Array<{name: string, url: string}>
  environmental_warnings?: string[] | null
  best_for: string
  trade_offs: string[]
}

export interface TierResults {
  good: Product[]
  better: Product[]
  best: Product[]
}

export interface SearchResponse {
  results: TierResults
  search_metadata: {
    sources_searched: string[]
    search_queries_used: string[]
  }
  processing_time_seconds: number
  educational_insights: string[]
}

export interface SearchQuery {
  query: string
  tier_preference?: ProductTier
  max_price?: number
  context?: Record<string, string>
}

export interface Category {
  id: string
  name: string
  icon: string
  description: string
}
