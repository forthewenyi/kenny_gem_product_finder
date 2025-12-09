'use client'

import { useState } from 'react'
import type { Product } from '@/types'

interface FilterBarProps {
  products: Product[]

  // Characteristics
  selectedCharacteristics: string[]
  onToggleCharacteristic: (char: string) => void

  // Brands
  selectedBrands: string[]
  onToggleBrand: (brand: string) => void

  // Tiers
  selectedTiers: string[]
  onToggleTier: (tier: string) => void

  // Materials
  selectedMaterials: string[]
  onToggleMaterial: (material: string) => void

  // Price
  maxPrice?: number
  onMaxPriceChange: (price: number | undefined) => void

  // Clear all
  onClearAll: () => void
}

export default function FilterBar({
  products,
  selectedCharacteristics,
  onToggleCharacteristic,
  selectedBrands,
  onToggleBrand,
  selectedTiers,
  onToggleTier,
  selectedMaterials,
  onToggleMaterial,
  maxPrice,
  onMaxPriceChange,
  onClearAll
}: FilterBarProps) {
  const [openSection, setOpenSection] = useState<string | null>(null)

  // Get unique values from products
  const uniqueBrands = Array.from(new Set(products.map(p => p.brand))).sort()
  const uniqueMaterials = Array.from(new Set(products.flatMap(p => p.materials || []))).sort()
  const uniqueCharacteristics = Array.from(new Set(products.flatMap(p => p.characteristics || []))).sort()

  // Get price range
  const prices = products.map(p => p.value_metrics.upfront_price)
  const minPrice = Math.min(...prices)
  const maxPriceAvailable = Math.max(...prices)

  // Check if any filters are active
  const hasFilters = selectedCharacteristics.length > 0 ||
                    selectedBrands.length > 0 ||
                    selectedTiers.length > 0 ||
                    selectedMaterials.length > 0 ||
                    maxPrice !== undefined

  const totalFilterCount = selectedCharacteristics.length +
                          selectedBrands.length +
                          selectedTiers.length +
                          selectedMaterials.length +
                          (maxPrice !== undefined ? 1 : 0)

  return (
    <div className="max-w-[1400px] mx-auto px-10 mb-6">
      <div className="border border-black">
        {/* Header with filter buttons */}
        <div className="flex items-center justify-between border-b border-black p-4">
          <div className="flex items-center gap-3">
            <h3 className="text-xs uppercase tracking-wide font-semibold">
              Filters {totalFilterCount > 0 && `(${totalFilterCount})`}
            </h3>

            {/* Filter type buttons */}
            <div className="flex gap-2">
              <button
                onClick={() => setOpenSection(openSection === 'tier' ? null : 'tier')}
                className="text-xs uppercase tracking-wide px-2 py-1 border border-black hover:bg-black hover:text-white transition-colors"
              >
                Value {selectedTiers.length > 0 && `(${selectedTiers.length})`}
              </button>

              <button
                onClick={() => setOpenSection(openSection === 'price' ? null : 'price')}
                className="text-xs uppercase tracking-wide px-2 py-1 border border-black hover:bg-black hover:text-white transition-colors"
              >
                Price {maxPrice !== undefined && '✓'}
              </button>

              <button
                onClick={() => setOpenSection(openSection === 'brand' ? null : 'brand')}
                className="text-xs uppercase tracking-wide px-2 py-1 border border-black hover:bg-black hover:text-white transition-colors"
              >
                Brand {selectedBrands.length > 0 && `(${selectedBrands.length})`}
              </button>

              <button
                onClick={() => setOpenSection(openSection === 'material' ? null : 'material')}
                className="text-xs uppercase tracking-wide px-2 py-1 border border-black hover:bg-black hover:text-white transition-colors"
              >
                Material {selectedMaterials.length > 0 && `(${selectedMaterials.length})`}
              </button>

              <button
                onClick={() => setOpenSection(openSection === 'characteristic' ? null : 'characteristic')}
                className="text-xs uppercase tracking-wide px-2 py-1 border border-black hover:bg-black hover:text-white transition-colors"
              >
                Features {selectedCharacteristics.length > 0 && `(${selectedCharacteristics.length})`}
              </button>
            </div>
          </div>

          {hasFilters && (
            <button
              onClick={onClearAll}
              className="text-xs uppercase tracking-wide hover:underline"
            >
              Clear All
            </button>
          )}
        </div>

        {/* Filter Sections */}
        {openSection === 'tier' && (
          <div className="p-4 border-b border-black">
            <div className="flex flex-wrap gap-2">
              {['good', 'better', 'best'].map((tier) => (
                <button
                  key={tier}
                  onClick={() => onToggleTier(tier)}
                  className={`text-xs uppercase tracking-wide px-3 py-2 border border-black transition-colors ${
                    selectedTiers.includes(tier)
                      ? 'bg-black text-white'
                      : 'hover:bg-gray-100'
                  }`}
                >
                  {tier}
                </button>
              ))}
            </div>
          </div>
        )}

        {openSection === 'price' && (
          <div className="p-4 border-b border-black">
            <div className="space-y-3">
              <div className="text-xs uppercase tracking-wide font-semibold">
                Maximum Price: {maxPrice ? `$${Math.round(maxPrice)}` : 'Any'}
              </div>
              <input
                type="range"
                min={minPrice}
                max={maxPriceAvailable}
                step="10"
                value={maxPrice || maxPriceAvailable}
                onChange={(e) => onMaxPriceChange(Number(e.target.value))}
                className="w-full"
              />
              <div className="flex justify-between text-[10px] uppercase tracking-wide">
                <span>${Math.round(minPrice)}</span>
                <span>${Math.round(maxPriceAvailable)}</span>
              </div>
              {maxPrice !== undefined && (
                <button
                  onClick={() => onMaxPriceChange(undefined)}
                  className="text-xs uppercase tracking-wide border border-black px-3 py-1 hover:bg-black hover:text-white transition-colors"
                >
                  Clear
                </button>
              )}
            </div>
          </div>
        )}

        {openSection === 'brand' && (
          <div className="p-4 border-b border-black">
            <div className="flex flex-wrap gap-2">
              {uniqueBrands.map((brand) => (
                <button
                  key={brand}
                  onClick={() => onToggleBrand(brand)}
                  className={`text-xs uppercase tracking-wide px-3 py-2 border border-black transition-colors ${
                    selectedBrands.includes(brand)
                      ? 'bg-black text-white'
                      : 'hover:bg-gray-100'
                  }`}
                >
                  {brand}
                </button>
              ))}
            </div>
          </div>
        )}

        {openSection === 'material' && (
          <div className="p-4 border-b border-black">
            <div className="flex flex-wrap gap-2">
              {uniqueMaterials.map((material) => (
                <button
                  key={material}
                  onClick={() => onToggleMaterial(material)}
                  className={`text-xs uppercase tracking-wide px-3 py-2 border border-black transition-colors ${
                    selectedMaterials.includes(material)
                      ? 'bg-black text-white'
                      : 'hover:bg-gray-100'
                  }`}
                >
                  {material}
                </button>
              ))}
            </div>
          </div>
        )}

        {openSection === 'characteristic' && (
          <div className="p-4 border-b border-black">
            <div className="flex flex-wrap gap-2">
              {uniqueCharacteristics.map((char) => (
                <button
                  key={char}
                  onClick={() => onToggleCharacteristic(char)}
                  className={`text-xs uppercase tracking-wide px-3 py-2 border border-black transition-colors ${
                    selectedCharacteristics.includes(char)
                      ? 'bg-black text-white'
                      : 'hover:bg-gray-100'
                  }`}
                >
                  {char}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Active Filters Display */}
        {hasFilters && (
          <div className="p-4">
            <div className="text-[10px] uppercase tracking-wide text-gray-500 mb-2">Active Filters:</div>
            <div className="flex flex-wrap gap-2">
              {selectedCharacteristics.map((char) => (
                <button
                  key={char}
                  onClick={() => onToggleCharacteristic(char)}
                  className="border border-black px-3 py-1 text-xs uppercase tracking-wide hover:bg-black hover:text-white transition-colors flex items-center gap-2"
                >
                  <span>{char}</span>
                  <span>×</span>
                </button>
              ))}
              {selectedBrands.map((brand) => (
                <button
                  key={brand}
                  onClick={() => onToggleBrand(brand)}
                  className="border border-black px-3 py-1 text-xs uppercase tracking-wide hover:bg-black hover:text-white transition-colors flex items-center gap-2"
                >
                  <span>{brand}</span>
                  <span>×</span>
                </button>
              ))}
              {selectedTiers.map((tier) => (
                <button
                  key={tier}
                  onClick={() => onToggleTier(tier)}
                  className="border border-black px-3 py-1 text-xs uppercase tracking-wide hover:bg-black hover:text-white transition-colors flex items-center gap-2"
                >
                  <span>{tier}</span>
                  <span>×</span>
                </button>
              ))}
              {selectedMaterials.map((material) => (
                <button
                  key={material}
                  onClick={() => onToggleMaterial(material)}
                  className="border border-black px-3 py-1 text-xs uppercase tracking-wide hover:bg-black hover:text-white transition-colors flex items-center gap-2"
                >
                  <span>{material}</span>
                  <span>×</span>
                </button>
              ))}
              {maxPrice !== undefined && (
                <button
                  onClick={() => onMaxPriceChange(undefined)}
                  className="border border-black px-3 py-1 text-xs uppercase tracking-wide hover:bg-black hover:text-white transition-colors flex items-center gap-2"
                >
                  <span>Max ${Math.round(maxPrice)}</span>
                  <span>×</span>
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
