/**
 * Product Characteristics Configuration
 * Defines dynamic filters and characteristics for different product categories
 */

import type { ProductCharacteristics } from '@/types/characteristics'

/**
 * Cast Iron Skillet Characteristics
 */
const CAST_IRON_SKILLET: ProductCharacteristics = {
  productCategory: 'cast_iron_skillet',
  categoryDisplayName: 'Cast Iron Skillet',
  keywords: ['cast iron', 'skillet', 'pan', 'frying pan', 'cast-iron'],

  characteristics: [
    // FILTER: Size
    {
      id: 'size',
      category: 'filter',
      filterLabel: 'SIZE',
      question: 'What size skillet do you need?',
      whyItMatters: 'Size affects how many people you can cook for and whether it fits in your oven. Larger skillets (12"+) are heavy when full.',
      options: [
        {
          value: '8',
          label: '8"',
          description: 'Perfect for eggs, small portions',
          recommendedFor: ['1-2 people', 'Side dishes'],
          icon: '🍳'
        },
        {
          value: '10',
          label: '10"',
          description: 'Most versatile everyday size',
          recommendedFor: ['2-3 people', 'Daily cooking'],
          icon: '🍳'
        },
        {
          value: '12',
          label: '12"',
          description: 'Great for family meals',
          recommendedFor: ['3-4 people', 'Family cooking'],
          icon: '🍳'
        },
        {
          value: '14',
          label: '14+"',
          description: 'Large gatherings, whole chickens',
          recommendedFor: ['4+ people', 'Entertaining'],
          icon: '🍳'
        }
      ],
      priority: 'high',
      autoDetectable: false,
      rememberAcrossSearches: true,
      placeholder: 'Select size'
    },

    // FILTER: Surface
    {
      id: 'surface',
      category: 'filter',
      filterLabel: 'SURFACE',
      question: 'What surface finish do you prefer?',
      whyItMatters: 'Pre-seasoned means ready to use immediately. Bare requires initial seasoning. Enameled never needs seasoning but can chip.',
      options: [
        {
          value: 'pre_seasoned',
          label: 'Pre-seasoned',
          description: 'Ready to cook, needs maintenance',
          recommendedFor: ['Beginners', 'Quick start']
        },
        {
          value: 'bare',
          label: 'Bare/Unseasoned',
          description: 'Build your own seasoning',
          recommendedFor: ['Enthusiasts', 'Custom control']
        },
        {
          value: 'enameled',
          label: 'Enameled',
          description: 'No seasoning needed, dishwasher safe',
          recommendedFor: ['Low maintenance', 'Dishwasher users']
        }
      ],
      priority: 'high',
      autoDetectable: false,
      rememberAcrossSearches: false
    },

    // FILTER: Features
    {
      id: 'features',
      category: 'filter',
      filterLabel: 'FEATURES',
      question: 'What features do you need?',
      whyItMatters: 'Helper handles make large skillets easier to lift. Pour spouts prevent drips. Lids are useful for covered cooking.',
      options: [
        { value: 'helper_handle', label: 'Helper Handle', icon: '🔧' },
        { value: 'pour_spouts', label: 'Pour Spouts', icon: '💧' },
        { value: 'lid_included', label: 'Lid Included', icon: '🎩' },
        { value: 'dual_handles', label: 'Dual Handles', icon: '🤲' }
      ],
      priority: 'medium',
      autoDetectable: false,
      rememberAcrossSearches: false,
      multiSelect: true
    },

    // CHARACTERISTIC: Stove Type
    {
      id: 'stove_type',
      category: 'characteristic',
      filterLabel: 'STOVE TYPE',
      question: 'What type of stove do you have?',
      whyItMatters: 'Induction stoves require magnetic cookware (cast iron works!). Glass tops need flat bottoms to prevent scratching. This affects which skillets will work for you.',
      options: [
        {
          value: 'gas',
          label: 'Gas',
          description: 'Works with all cast iron',
          icon: '🔥'
        },
        {
          value: 'electric_coil',
          label: 'Electric Coil',
          description: 'Works with all cast iron',
          icon: '⚡'
        },
        {
          value: 'glass_top',
          label: 'Glass Top/Ceramic',
          description: 'Requires flat, smooth bottom',
          icon: '✨'
        },
        {
          value: 'induction',
          label: 'Induction',
          description: 'Cast iron is naturally induction-compatible',
          icon: '🧲'
        }
      ],
      priority: 'high',
      autoDetectable: false,
      rememberAcrossSearches: true
    },

    // CHARACTERISTIC: Household Size
    {
      id: 'household_size',
      category: 'characteristic',
      filterLabel: 'HOUSEHOLD SIZE',
      question: 'How many people do you typically cook for?',
      whyItMatters: 'This helps us recommend the right size. A 10" skillet is perfect for 2-3 people, while 12"+ works better for families.',
      options: [
        { value: '1-2', label: '1-2 people', icon: '👤' },
        { value: '2-4', label: '2-4 people', icon: '👥' },
        { value: '4-6', label: '4-6 people', icon: '👨‍👩‍👧‍👦' },
        { value: '6+', label: '6+ people', icon: '👨‍👩‍👧‍👦👨‍👩‍👧‍👦' }
      ],
      priority: 'high',
      autoDetectable: false,
      rememberAcrossSearches: true
    },

    // CHARACTERISTIC: Cooking Frequency
    {
      id: 'cooking_frequency',
      category: 'characteristic',
      filterLabel: 'COOKING FREQUENCY',
      question: 'How often do you cook with cast iron?',
      whyItMatters: 'Frequent use builds better seasoning naturally. Occasional users might prefer enameled (no seasoning needed). This affects our tier and surface recommendations.',
      options: [
        { value: 'occasional', label: 'Occasionally (1-2x/month)', icon: '📅' },
        { value: 'regular', label: 'Regularly (1-2x/week)', icon: '📆' },
        { value: 'daily', label: 'Daily', icon: '🗓️' },
        { value: 'professional', label: 'Professional/Commercial', icon: '👨‍🍳' }
      ],
      priority: 'medium',
      autoDetectable: false,
      rememberAcrossSearches: true
    },

    // CHARACTERISTIC: Dishwasher Availability
    {
      id: 'dishwasher',
      category: 'characteristic',
      filterLabel: 'DISHWASHER',
      question: 'Do you have a dishwasher?',
      whyItMatters: 'Bare cast iron cannot go in the dishwasher (ruins seasoning). Enameled cast iron is dishwasher-safe. This affects our surface finish recommendation.',
      options: [
        { value: 'yes_use_it', label: 'Yes, and I use it regularly', icon: '✅' },
        { value: 'yes_avoid', label: 'Yes, but I avoid using it', icon: '🤔' },
        { value: 'no', label: 'No dishwasher', icon: '❌' }
      ],
      priority: 'medium',
      autoDetectable: false,
      rememberAcrossSearches: true
    },

    // CHARACTERISTIC: Water Hardness (auto-detectable)
    {
      id: 'water_hardness',
      category: 'characteristic',
      filterLabel: 'WATER HARDNESS',
      question: "What's your water hardness?",
      whyItMatters: 'Hard water leaves mineral deposits that can interfere with seasoning. We can help you choose skillets with better rust resistance and provide water-specific care tips.',
      options: [
        {
          value: 'soft',
          label: 'Soft',
          description: 'West Coast, Pacific Northwest',
          icon: '💧'
        },
        {
          value: 'medium',
          label: 'Medium',
          description: 'Most of US',
          icon: '💦'
        },
        {
          value: 'hard',
          label: 'Hard',
          description: 'Southwest, Texas, Florida',
          icon: '💎'
        },
        {
          value: 'unknown',
          label: "I'm not sure",
          icon: '❓'
        }
      ],
      priority: 'low',
      autoDetectable: true,
      rememberAcrossSearches: true
    },

    // CHARACTERISTIC: Maintenance Commitment
    {
      id: 'maintenance',
      category: 'characteristic',
      filterLabel: 'MAINTENANCE',
      question: 'How much maintenance are you willing to do?',
      whyItMatters: 'Cast iron maintenance varies by type. Enameled = dishwasher safe, minimal care (~2 min/use). Traditional = hand wash, dry immediately, oil after each use (~5-10 min). Bare iron needs initial seasoning (2-3 hours first time) plus regular upkeep.',
      options: [
        {
          value: 'minimal',
          label: 'Minimal - Just wash & go',
          description: 'Dishwasher safe, no seasoning needed',
          recommendedFor: ['Enameled cast iron', 'Busy schedules'],
          icon: '✨'
        },
        {
          value: 'moderate',
          label: 'Moderate - Quick care',
          description: 'Hand wash, dry, light oil (~5 min)',
          recommendedFor: ['Pre-seasoned cast iron', 'Regular cooking'],
          icon: '🧼'
        },
        {
          value: 'high',
          label: 'High - Full care routine',
          description: 'Hand wash, dry, oil, re-season as needed',
          recommendedFor: ['Bare cast iron', 'Enthusiasts'],
          icon: '🛠️'
        },
        {
          value: 'enthusiast',
          label: 'Enthusiast - I enjoy the ritual',
          description: 'Full seasoning routine, restoration projects',
          recommendedFor: ['Vintage collectors', 'DIY lovers'],
          icon: '❤️'
        }
      ],
      priority: 'high',
      autoDetectable: false,
      rememberAcrossSearches: true
    },

    // CHARACTERISTIC: Oven Usage
    {
      id: 'oven_usage',
      category: 'characteristic',
      filterLabel: 'OVEN USAGE',
      question: 'Do you cook in the oven?',
      whyItMatters: 'Cast iron is oven-safe at high temps, perfect for searing then finishing in the oven. Some handles get very hot - we can recommend options with stay-cool handles or helper handles.',
      options: [
        { value: 'never', label: 'Never/Rarely', icon: '❌' },
        { value: 'sometimes', label: 'Sometimes', icon: '🤔' },
        { value: 'often', label: 'Often (weekly+)', icon: '♨️' }
      ],
      priority: 'low',
      autoDetectable: false,
      rememberAcrossSearches: true,
      conditionalOn: undefined
    }
  ]
}

/**
 * Chef Knife Characteristics (example for future expansion)
 */
const CHEF_KNIFE: ProductCharacteristics = {
  productCategory: 'chef_knife',
  categoryDisplayName: 'Chef Knife',
  keywords: ['chef knife', 'kitchen knife', 'cooking knife', "chef's knife"],

  characteristics: [
    {
      id: 'blade_length',
      category: 'filter',
      filterLabel: 'BLADE LENGTH',
      question: 'What blade length do you prefer?',
      whyItMatters: '8" is most versatile. 10" for large cutting tasks. 6" for small kitchens.',
      options: [
        { value: '6', label: '6"', recommendedFor: ['Small hands', 'Compact kitchens'] },
        { value: '8', label: '8"', recommendedFor: ['Most versatile', 'Beginners'] },
        { value: '10', label: '10"', recommendedFor: ['Large tasks', 'Professionals'] }
      ],
      priority: 'high',
      autoDetectable: false,
      rememberAcrossSearches: true
    },
    {
      id: 'blade_style',
      category: 'filter',
      filterLabel: 'STYLE',
      question: 'What blade style do you prefer?',
      whyItMatters: 'Western (German) style is heavier and more durable. Japanese style is lighter and sharper.',
      options: [
        { value: 'western', label: 'Western/German', description: 'Heavier, more durable' },
        { value: 'japanese', label: 'Japanese', description: 'Lighter, sharper edge' }
      ],
      priority: 'high',
      autoDetectable: false,
      rememberAcrossSearches: false
    }
  ]
}

/**
 * All product characteristics configurations
 */
export const PRODUCT_CHARACTERISTICS: ProductCharacteristics[] = [
  CAST_IRON_SKILLET,
  CHEF_KNIFE
  // Add more product categories here
]

/**
 * Get characteristics for a product based on search query
 */
export function getCharacteristicsForQuery(query: string): ProductCharacteristics | null {
  const normalizedQuery = query.toLowerCase().trim()

  for (const productConfig of PRODUCT_CHARACTERISTICS) {
    // Check if any keywords match the query
    const matches = productConfig.keywords.some(keyword =>
      normalizedQuery.includes(keyword.toLowerCase())
    )

    if (matches) {
      return productConfig
    }
  }

  return null
}

/**
 * Get filter characteristics (for filter bar)
 */
export function getFilterCharacteristics(config: ProductCharacteristics) {
  return config.characteristics.filter(c => c.category === 'filter')
}

/**
 * Get question characteristics (for characteristics section)
 */
export function getQuestionCharacteristics(config: ProductCharacteristics) {
  return config.characteristics.filter(c => c.category === 'characteristic')
}

/**
 * Get high priority characteristics (show first)
 */
export function getHighPriorityCharacteristics(config: ProductCharacteristics) {
  return config.characteristics
    .filter(c => c.category === 'characteristic' && c.priority === 'high')
    .sort((a, b) => a.priority.localeCompare(b.priority))
}
