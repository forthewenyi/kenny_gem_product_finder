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

export interface QualityData {
  score: number // 0-100
  average_lifespan_years: number
  still_working_after_5years_percent: number // 0-100
  total_user_reports: number
  common_failure_points: string[]
  repairability_score: number // 0-100
  material_quality_indicators: string[]
  data_sources: string[]
}

export interface PracticalMetrics {
  cleaning_time_minutes?: number | null
  cleaning_details: string
  setup_time: string
  setup_details: string
  learning_curve: string
  learning_details: string
  maintenance_level: string
  maintenance_details: string
  weight_lbs?: number | null
  weight_notes?: string | null
  dishwasher_safe: boolean
  oven_safe: boolean
  oven_max_temp?: number | null
}

export interface Product {
  name: string
  brand: string
  tier: TierLevel
  category: string
  value_metrics: ValueMetrics
  quality_data?: QualityData | null
  practical_metrics?: PracticalMetrics | null
  characteristics: string[] // NEW: Normalized characteristics for filtering
  key_features: string[]
  materials: string[]
  why_its_a_gem: string
  key_differentiator?: string | null // What makes THIS product special vs competitors
  image_url?: string | null // Product image URL from web search
  web_sources: WebSource[]
  reddit_mentions?: number | null
  professional_reviews: string[]
  maintenance_level: string
  purchase_links: Array<{name: string, url: string}>
  environmental_warnings?: string[] | null
  best_for: string
  drawbacks: string[]
}

export interface ProductTier {
  tier: TierLevel
  products: Product[]
  quality?: QualityData | null
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

export interface AggregatedCharacteristic {
  label: string
  count: number
  product_names: string[]
}

export interface BuyingCharacteristic {
  label: string
  reason: string
  explanation: string
  image_keyword: string
}

export interface RealSearchMetrics {
  total_sources_analyzed: number
  reddit_threads: number
  expert_reviews: number
  search_queries_executed: number
  search_queries: string[]
  unique_sources: number
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
  aggregated_characteristics: AggregatedCharacteristic[] // Real characteristics from products for filtering
  buying_characteristics?: BuyingCharacteristic[] | null // AI-generated buying guidance
  real_search_metrics?: RealSearchMetrics | null // Real search metrics
  // Search transparency data
  search_queries?: Array<{ phase: string; query: string }>
  total_sources_analyzed?: number
  queries_generated?: number
  sources_by_phase?: {
    context_discovery?: number
    material_science?: number
    product_identification?: number
    frustration_research?: number
    value_synthesis?: number
  }
}

export interface SearchQuery {
  query: string
  tier_preference?: TierLevel
  max_price?: number
  context?: Record<string, string>
  characteristics?: Record<string, string | string[]>
}

export interface Category {
  id: string
  name: string
  icon: string
  description: string
}
