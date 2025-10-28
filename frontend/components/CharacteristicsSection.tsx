'use client'

import { useQuery } from '@tanstack/react-query'
import { generateCharacteristics, Characteristic as APICharacteristic } from '@/lib/api'

interface Characteristic {
  label: string
  reason: string
  imageUrl: string
  explanation?: string
}

const placeholderCharacteristics: Characteristic[] = [
  {
    label: 'PRE-SEASONED',
    reason: 'Ready to use',
    imageUrl: 'https://images.unsplash.com/photo-1556909172-54557c7e4fb7?w=800&auto=format&fit=crop'
  },
  {
    label: '10-12 INCH',
    reason: 'Most versatile',
    imageUrl: 'https://images.unsplash.com/photo-1565895405227-33f37c6c0e56?w=800&auto=format&fit=crop'
  },
  {
    label: 'HEAVY BOTTOM',
    reason: 'Even heating',
    imageUrl: 'https://images.unsplash.com/photo-1584990347449-39910cbee3f6?w=800&auto=format&fit=crop'
  },
  {
    label: 'HELPER HANDLE',
    reason: 'Easier to lift',
    imageUrl: 'https://images.unsplash.com/photo-1616486701797-0f33f61038ec?w=800&auto=format&fit=crop'
  },
  {
    label: 'SMOOTH INTERIOR',
    reason: 'Easier cleaning',
    imageUrl: 'https://images.unsplash.com/photo-1610701596007-11502861dcfa?w=800&auto=format&fit=crop'
  }
]

interface CharacteristicsSectionProps {
  query?: string
  location?: string
  selectedCharacteristics?: string[]
  onCharacteristicClick?: (characteristic: string) => void
}

export default function CharacteristicsSection({
  query,
  location,
  selectedCharacteristics = [],
  onCharacteristicClick
}: CharacteristicsSectionProps) {
  // Format query for display
  const displayQuery = query && query.trim() ? query : 'Kitchen Products'
  const searchQuery = query && query.trim() ? query : 'kitchen products'

  // Fetch dynamic characteristics from API
  const { data, isLoading, isError } = useQuery({
    queryKey: ['characteristics', searchQuery, location],
    queryFn: () => generateCharacteristics(searchQuery, location || 'Austin, TX'),
    enabled: !!searchQuery, // Only fetch if we have a query
    staleTime: 1000 * 60 * 60, // Cache for 1 hour
  })

  // Use API data if available, otherwise fall back to placeholder
  const characteristics = data?.characteristics
    ? data.characteristics.map((char: APICharacteristic, index: number) => ({
        label: char.label,
        reason: char.reason,
        explanation: char.explanation,
        // Use Unsplash with image_keyword, or fallback to placeholder images
        imageUrl: `https://images.unsplash.com/photo-1556909172-54557c7e4fb7?w=800&auto=format&fit=crop&q=${char.image_keyword}`
      }))
    : placeholderCharacteristics

  return (
    <section className="max-w-[1400px] mx-auto px-10 pb-10">
      {/* Section Header */}
      <div className="mb-4">
        <h2 className="text-sm font-semibold uppercase tracking-wide mb-1">
          Kenny's Buying Guide for {displayQuery}
          {isLoading && <span className="ml-2 text-xs text-gray-400">(generating...)</span>}
        </h2>
        <p className="text-xs text-gray-500 tracking-wide">
          Based on your location {location ? `(${location})` : '(Austin, TX)'} and typical use, here's what to look for:
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
        <span>These suggestions change based on what you search for</span>
      </div>
    </section>
  )
}
