// TypeScript types matching the backend API

export type TierLevel = 'good' | 'better' | 'best'

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

export interface DurabilityData {
  score: number // 0-100
  average_lifespan_years: number
  still_working_after_5years_percent: number // 0-100
  total_user_reports: number
  common_failure_points: string[]
  repairability_score: number // 0-100
  material_quality_indicators: string[]
  data_sources: string[]
}

export interface Product {
  name: string
  brand: string
  tier: TierLevel
  category: string
  value_metrics: ValueMetrics
  durability_data?: DurabilityData | null
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

export interface ProductTier {
  tier: TierLevel
  products: Product[]
  durability?: DurabilityData | null
}

export interface AlternativeSolution {
  problem: string
  consumer_solution: string
  consumer_cost: number
  consumer_issues: string[]
  your_solution: string
  your_cost: number
  why_better: string
  how_to: string
  savings_per_year: number
  when_to_buy_instead?: string | null
}

export interface BeforeYouBuy {
  title: string
  subtitle: string
  alternatives: AlternativeSolution[]
  educational_insight: string
}

export interface TierResults {
  good: Product[]
  better: Product[]
  best: Product[]
}

export interface SearchResponse {
  before_you_buy?: BeforeYouBuy | null
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
  tier_preference?: TierLevel
  max_price?: number
  context?: Record<string, string>
}

export interface Category {
  id: string
  name: string
  icon: string
  description: string
}
