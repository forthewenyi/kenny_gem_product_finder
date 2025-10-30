'use client'

import type { AggregatedCharacteristic } from '@/types'

interface CharacteristicsSectionProps {
  query?: string
  aggregatedCharacteristics: AggregatedCharacteristic[]
  selectedCharacteristics?: string[]
  onCharacteristicClick?: (characteristic: string) => void
}

// Generate helpful reason text based on characteristic label
function getCharacteristicReason(label: string): string {
  const lowerLabel = label.toLowerCase()

  // Size-related
  if (lowerLabel.includes('inch') || lowerLabel.includes('capacity')) {
    return 'Most versatile'
  }

  // Pre-seasoned / Ready to use
  if (lowerLabel.includes('pre-seasoned') || lowerLabel.includes('ready')) {
    return 'Ready to use'
  }

  // Handle-related
  if (lowerLabel.includes('handle') && lowerLabel.includes('helper')) {
    return 'Easier to lift'
  }
  if (lowerLabel.includes('handle') && (lowerLabel.includes('ergonomic') || lowerLabel.includes('comfortable'))) {
    return 'Better grip'
  }
  if (lowerLabel.includes('tang')) {
    return 'Better balance'
  }

  // Material-related
  if (lowerLabel.includes('steel') || lowerLabel.includes('iron')) {
    return 'Long lasting'
  }
  if (lowerLabel.includes('non-stick') || lowerLabel.includes('nonstick')) {
    return 'Easy cooking'
  }

  // Cleaning-related
  if (lowerLabel.includes('dishwasher')) {
    return 'Easy cleaning'
  }
  if (lowerLabel.includes('smooth')) {
    return 'Easier cleaning'
  }

  // Heat-related
  if (lowerLabel.includes('oven safe') || lowerLabel.includes('oven-safe')) {
    return 'Versatile cooking'
  }
  if (lowerLabel.includes('heavy') || lowerLabel.includes('thick')) {
    return 'Even heating'
  }

  // Weight-related
  if (lowerLabel.includes('lightweight') || lowerLabel.includes('light weight')) {
    return 'Easy handling'
  }

  // Digital/Controls
  if (lowerLabel.includes('digital')) {
    return 'Precise control'
  }

  // Quiet operation
  if (lowerLabel.includes('quiet')) {
    return 'Less noise'
  }

  // Compact/Small
  if (lowerLabel.includes('compact')) {
    return 'Saves space'
  }

  // Default
  return 'Common choice'
}

export default function CharacteristicsSection({
  query,
  aggregatedCharacteristics,
  selectedCharacteristics = [],
  onCharacteristicClick
}: CharacteristicsSectionProps) {
  // Format query for display
  const displayQuery = query && query.trim() ? query : 'Kitchen Products'

  // Use aggregated characteristics from search results
  // These are real characteristics extracted from the products found
  const characteristics = aggregatedCharacteristics.slice(0, 5).map((char, index) => ({
    label: char.label,
    reason: getCharacteristicReason(char.label),
    count: char.count,
    productNames: char.product_names,
    // Use Unsplash with characteristic as keyword
    imageUrl: `https://images.unsplash.com/photo-1556909172-54557c7e4fb7?w=800&auto=format&fit=crop&q=${encodeURIComponent(char.label)}`
  }))

  // Calculate unique product count
  const uniqueProductCount = new Set(
    aggregatedCharacteristics.flatMap(c => c.product_names)
  ).size

  return (
    <section className="max-w-[1400px] mx-auto px-10 pb-10">
      {/* Section Header */}
      <div className="mb-4">
        <h2 className="text-sm font-semibold uppercase tracking-wide mb-1">
          Kenny's Buying Guide for {displayQuery}
        </h2>
        <p className="text-xs text-gray-500 tracking-wide">
          Based on {uniqueProductCount} product{uniqueProductCount !== 1 ? 's' : ''} found, here's what to look for:
        </p>
      </div>

      {/* Characteristics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-0">
        {characteristics.map((char, index) => {
          const isSelected = selectedCharacteristics.includes(char.label)
          return (
            <div
              key={index}
              onClick={() => onCharacteristicClick?.(char.label)}
              className={`relative overflow-hidden cursor-pointer group transition-all ${
                isSelected ? 'ring-4 ring-black ring-inset' : ''
              }`}
              style={{ paddingBottom: '100%' }}
            >
              {/* Image */}
              <img
                src={char.imageUrl}
                alt={char.label}
                className={`absolute top-0 left-0 w-full h-full object-cover transition-all ${
                  isSelected ? 'opacity-100 brightness-110' : 'group-hover:opacity-90'
                }`}
              />

              {/* Gradient Overlay */}
              <div className={`absolute top-0 left-0 w-full h-full bg-gradient-to-b from-transparent via-transparent ${
                isSelected ? 'to-black/60' : 'to-black/40'
              }`} />

              {/* Selected Indicator */}
              {isSelected && (
                <div className="absolute top-3 right-3 bg-black text-white rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold">
                  ✓
                </div>
              )}

              {/* Label */}
              <div className="absolute bottom-5 left-5 z-10 text-white">
                <div className={`text-xs font-semibold uppercase tracking-wide mb-0.5 drop-shadow-md ${
                  isSelected ? 'text-white font-bold' : ''
                }`}>
                  {char.label}
                </div>
                <div className="text-[9px] font-normal drop-shadow-md">
                  {char.reason}
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Footer Note */}
      <div className="mt-4 text-xs text-gray-500 flex items-center gap-1">
        <span>ℹ️</span>
        <span>These are real product characteristics extracted from the search results</span>
      </div>
    </section>
  )
}
