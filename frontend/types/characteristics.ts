/**
 * Dynamic Characteristics Configuration System
 * Defines product-specific filters and characteristics questions
 */

export type CharacteristicCategory = 'filter' | 'characteristic'
export type CharacteristicPriority = 'high' | 'medium' | 'low'

/**
 * Option for a characteristic (e.g., "10 inch", "Gas stove")
 */
export interface CharacteristicOption {
  value: string
  label: string
  description?: string // Tooltip/helper text
  recommendedFor?: string[] // E.g., ["Daily cooks", "Large families"]
  icon?: string // Emoji or icon name
}

/**
 * Configuration for a single characteristic
 */
export interface CharacteristicConfig {
  id: string // e.g., "size", "stove_type"
  category: CharacteristicCategory // Where it appears

  // Display text
  question: string // For characteristics section: "What type of stove do you have?"
  filterLabel?: string // For filter bar: "SIZE"
  whyItMatters: string // Educational tooltip content

  // Options
  options: CharacteristicOption[]

  // Behavior
  priority: CharacteristicPriority // For progressive disclosure
  autoDetectable: boolean // Can we pre-fill from location/context?
  rememberAcrossSearches: boolean // Store in localStorage?
  conditionalOn?: string // Only show if another characteristic is selected
  multiSelect?: boolean // Allow multiple selections (default: false)

  // UI hints
  defaultValue?: string // Pre-selected value
  placeholder?: string // For dropdowns
}

/**
 * Product category characteristic set
 */
export interface ProductCharacteristics {
  productCategory: string // e.g., "cast_iron_skillet"
  categoryDisplayName: string // "Cast Iron Skillet"
  characteristics: CharacteristicConfig[]

  // Metadata
  keywords: string[] // Query matching: ["skillet", "pan", "cast iron"]
  relatedCategories?: string[] // Similar products
}

/**
 * User's characteristic answers
 */
export interface CharacteristicAnswers {
  [characteristicId: string]: string | string[] // Single or multi-select values
}

/**
 * Characteristic answer with metadata
 */
export interface CharacteristicAnswer {
  characteristicId: string
  value: string | string[]
  timestamp: number
  source: 'user_input' | 'auto_detected' | 'remembered'
}
