'use client'

import type { BuyingCharacteristic, AggregatedCharacteristic } from '@/types'

interface CharacteristicsSectionProps {
  query?: string
  buyingCharacteristics?: BuyingCharacteristic[] | null
  aggregatedCharacteristics: AggregatedCharacteristic[]
  selectedCharacteristics?: string[]
  onCharacteristicClick?: (characteristic: string) => void
}

// Fuzzy matching: Check if AI buying characteristic matches any aggregated characteristic
function findMatchingAggregatedChar(
  buyingLabel: string,
  aggregatedChars: AggregatedCharacteristic[]
): AggregatedCharacteristic | null {
  const normalizedBuying = buyingLabel.toLowerCase().replace(/[^a-z0-9\s]/g, '')

  for (const aggChar of aggregatedChars) {
    const normalizedAgg = aggChar.label.toLowerCase().replace(/[^a-z0-9\s]/g, '')

    // Exact match
    if (normalizedBuying === normalizedAgg) {
      return aggChar
    }

    // Partial match: buying label contains aggregated label or vice versa
    if (normalizedBuying.includes(normalizedAgg) || normalizedAgg.includes(normalizedBuying)) {
      return aggChar
    }

    // Word-level matching: check if key words overlap
    const buyingWords = normalizedBuying.split(/\s+/)
    const aggWords = normalizedAgg.split(/\s+/)

    // If at least 50% of words match (and at least 1 word)
    const matchingWords = buyingWords.filter(word =>
      word.length > 2 && aggWords.some(aggWord => aggWord.includes(word) || word.includes(aggWord))
    )

    if (matchingWords.length > 0 && matchingWords.length >= Math.min(buyingWords.length, aggWords.length) * 0.5) {
      return aggChar
    }
  }

  return null
}

export default function CharacteristicsSection({
  query,
  buyingCharacteristics,
  aggregatedCharacteristics,
  selectedCharacteristics = [],
  onCharacteristicClick
}: CharacteristicsSectionProps) {
  // Format query for display
  const displayQuery = query && query.trim() ? query : 'Kitchen Products'

  // Don't render if no buying characteristics
  if (!buyingCharacteristics || buyingCharacteristics.length === 0) {
    return null
  }

  // Map buying characteristics to include clickability info
  const characteristics = buyingCharacteristics.map((buyingChar) => {
    const matchedAggChar = findMatchingAggregatedChar(buyingChar.label, aggregatedCharacteristics)
    const isClickable = matchedAggChar !== null
    const isSelected = matchedAggChar ? selectedCharacteristics.includes(matchedAggChar.label) : false

    return {
      ...buyingChar,
      isClickable,
      isSelected,
      matchedLabel: matchedAggChar?.label || null,
      productCount: matchedAggChar?.count || 0
    }
  })

  return (
    <section className="max-w-[1400px] mx-auto px-10 pb-10">
      {/* Section Header */}
      <div className="mb-4">
        <h2 className="text-sm font-semibold uppercase tracking-wide mb-1">
          What to Look For
        </h2>
        <p className="text-xs text-gray-500 tracking-wide">
          AI-generated buying guidance based on expert reviews and quality insights
        </p>
      </div>

      {/* Characteristics Grid - Text-based cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        {characteristics.map((char, index) => {
          const handleClick = () => {
            if (char.isClickable && char.matchedLabel && onCharacteristicClick) {
              onCharacteristicClick(char.matchedLabel)
            }
          }

          return (
            <div
              key={index}
              onClick={handleClick}
              className={`
                border p-4 transition-all
                ${char.isClickable
                  ? 'border-black cursor-pointer hover:bg-gray-50 hover:shadow-md'
                  : 'border-gray-300 bg-gray-50 opacity-60 cursor-default'
                }
                ${char.isSelected ? 'bg-black text-white ring-2 ring-black' : ''}
              `}
            >
              {/* Selected Indicator */}
              {char.isSelected && (
                <div className="flex justify-end mb-2">
                  <div className="bg-white text-black rounded-full w-5 h-5 flex items-center justify-center text-xs font-bold">
                    ✓
                  </div>
                </div>
              )}

              {/* Label */}
              <div className={`text-xs font-bold uppercase tracking-wide mb-2 ${
                char.isSelected ? 'text-white' : 'text-black'
              }`}>
                {char.label}
              </div>

              {/* Reason */}
              <div className={`text-[10px] mb-3 ${
                char.isSelected ? 'text-gray-200' : 'text-gray-600'
              }`}>
                {char.reason}
              </div>

              {/* Explanation */}
              <div className={`text-[11px] leading-relaxed ${
                char.isSelected ? 'text-gray-100' : 'text-gray-700'
              }`}>
                {char.explanation}
              </div>

              {/* Clickability indicator */}
              {char.isClickable && char.productCount > 0 && !char.isSelected && (
                <div className="mt-3 pt-3 border-t border-gray-200 text-[10px] text-gray-500">
                  {char.productCount} product{char.productCount !== 1 ? 's' : ''} • Click to filter
                </div>
              )}

              {!char.isClickable && (
                <div className="mt-3 pt-3 border-t border-gray-300 text-[10px] text-gray-400 italic">
                  No matching products
                </div>
              )}
            </div>
          )
        })}
      </div>

      {/* Footer Note */}
      <div className="mt-4 text-xs text-gray-500 flex items-center gap-1">
        <span>ℹ️</span>
        <span>These characteristics are generated by AI based on Reddit, expert reviews, and quality research</span>
      </div>
    </section>
  )
}
