'use client'

import type { Product } from '@/types'

interface FilterOptionsProps {
  products: Product[]
  selectedMaterials: string[]
  selectedTier?: string
  onMaterialClick: (material: string) => void
  onTierClick: (tier: string) => void
}

export default function FilterOptions({
  products,
  selectedMaterials,
  selectedTier,
  onMaterialClick,
  onTierClick
}: FilterOptionsProps) {
  // Extract unique materials from all products
  const allMaterials = new Set<string>()
  products.forEach(product => {
    // Handle products without materials array
    const materials = product.materials || []
    materials.forEach(material => {
      // Normalize material names
      const normalized = material.trim()
      if (normalized) allMaterials.add(normalized)
    })
  })

  const uniqueMaterials = Array.from(allMaterials).sort()

  // Tier options
  const tiers = [
    { value: 'good', label: 'Good', description: '$20-80, 2-5 years' },
    { value: 'better', label: 'Better', description: '$80-200, 8-15 years' },
    { value: 'best', label: 'Best', description: '$200+, 15-30+ years' }
  ]

  if (uniqueMaterials.length === 0) {
    return null
  }

  return (
    <div className="max-w-[1400px] mx-auto px-10 py-6 border-b border-gray-200">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Material Options */}
        <div>
          <div className="flex items-center gap-2 mb-3">
            <span className="text-[10px] uppercase tracking-wider text-gray-500 font-semibold">
              Material
            </span>
            <span className="text-[9px] text-gray-400">
              ({uniqueMaterials.length} options)
            </span>
          </div>
          <div className="flex gap-2 flex-wrap">
            {uniqueMaterials.map(material => {
              const isSelected = selectedMaterials.includes(material)
              return (
                <button
                  key={material}
                  onClick={() => onMaterialClick(material)}
                  className={`px-3 py-1.5 text-xs border transition-colors ${
                    isSelected
                      ? 'bg-black text-white border-black'
                      : 'bg-white text-gray-700 border-gray-300 hover:border-black'
                  }`}
                >
                  {material}
                </button>
              )
            })}
          </div>
        </div>

        {/* Value Tier Options */}
        <div>
          <div className="flex items-center gap-2 mb-3">
            <span className="text-[10px] uppercase tracking-wider text-gray-500 font-semibold">
              Value Tier
            </span>
          </div>
          <div className="flex gap-2 flex-wrap">
            {tiers.map(tier => {
              const isSelected = selectedTier === tier.value
              return (
                <button
                  key={tier.value}
                  onClick={() => onTierClick(tier.value)}
                  className={`px-3 py-1.5 text-xs border transition-colors ${
                    isSelected
                      ? 'bg-black text-white border-black'
                      : 'bg-white text-gray-700 border-gray-300 hover:border-black'
                  }`}
                >
                  <div className="flex flex-col items-start">
                    <span className="font-semibold uppercase">{tier.label}</span>
                    <span className="text-[9px] text-gray-400">{tier.description}</span>
                  </div>
                </button>
              )
            })}
          </div>
        </div>
      </div>
    </div>
  )
}
