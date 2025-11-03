// Type definitions for context filters
// Component no longer used - types exported for use in other components

export type FilterCategory = 'value_preference'

export interface ContextFilters {
  value_preference?: 'save_now' | 'best_value' | 'buy_for_life'
}
