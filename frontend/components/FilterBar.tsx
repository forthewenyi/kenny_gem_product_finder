'use client'

import type { ContextFilters, FilterCategory } from './ContextFiltersBar'
import type { ProductCharacteristics, CharacteristicAnswers } from '@/types/characteristics'
import FilterDropdown from './FilterDropdown'
import ValuePreferenceDropdown from './ValuePreferenceDropdown'

interface FilterBarProps {
  // Characteristics filters
  selectedCharacteristics: string[]
  onRemoveCharacteristic: (characteristic: string) => void

  // Category filter
  selectedCategory?: string
  onRemoveCategory?: () => void

  // Material filters
  selectedMaterials: string[]
  onRemoveMaterial: (material: string) => void

  // Tier filter
  selectedTier?: string
  onRemoveTier?: () => void

  // Context filters (Budget, Life Stage, Space, Frequency)
  contextFilters?: ContextFilters
  onContextFilterClick?: (category: FilterCategory) => void
  onClearContextFilters?: () => void
  onAllFiltersClick?: () => void
  onValuePreferenceChange?: (value: 'save_now' | 'best_value' | 'buy_for_life') => void

  // Dynamic characteristics props
  productConfig?: ProductCharacteristics | null
  characteristicAnswers?: CharacteristicAnswers
  onCharacteristicAnswer?: (characteristicId: string, value: string | string[]) => void
  onClearCharacteristicAnswer?: (characteristicId: string) => void
}

export default function FilterBar({
  selectedCharacteristics,
  onRemoveCharacteristic,
  selectedCategory,
  onRemoveCategory,
  selectedMaterials,
  onRemoveMaterial,
  selectedTier,
  onRemoveTier,
  contextFilters,
  onContextFilterClick,
  onClearContextFilters,
  onAllFiltersClick,
  onValuePreferenceChange,
  productConfig,
  characteristicAnswers,
  onCharacteristicAnswer,
  onClearCharacteristicAnswer
}: FilterBarProps) {
  const hasCharacteristics = selectedCharacteristics.length > 0
  const hasMaterials = selectedMaterials.length > 0
  const hasContextFilters = contextFilters && Object.values(contextFilters).filter(v => v).length > 0
  const hasCharacteristicAnswers = characteristicAnswers && Object.keys(characteristicAnswers).length > 0
  const hasAnyFilters = hasCharacteristics || selectedCategory || hasMaterials || selectedTier || hasContextFilters || hasCharacteristicAnswers

  // Get all characteristics from config (both filters and characteristics)
  const allCharacteristics = productConfig ? productConfig.characteristics : []

  const clearAll = () => {
    selectedCharacteristics.forEach(char => onRemoveCharacteristic(char))
    selectedMaterials.forEach(mat => onRemoveMaterial(mat))
    if (selectedCategory && onRemoveCategory) onRemoveCategory()
    if (selectedTier && onRemoveTier) onRemoveTier()
    if (hasContextFilters && onClearContextFilters) onClearContextFilters()
    // Clear dynamic characteristic answers
    if (characteristicAnswers && onClearCharacteristicAnswer) {
      Object.keys(characteristicAnswers).forEach(id => onClearCharacteristicAnswer(id))
    }
  }


  return (
    <div className="border-t border-b border-gray-200 py-6 px-10 max-w-[1400px] mx-auto">
      {/* Filter Buttons Row */}
      <div className="flex gap-2 flex-wrap mb-4">
        {/* ALL FILTERS Button */}
        {onAllFiltersClick && (
          <button
            onClick={onAllFiltersClick}
            className="flex items-center gap-2 px-3 py-1.5 text-[11px] uppercase tracking-wider font-semibold bg-white text-black border border-gray-300 hover:border-black transition-colors"
          >
            ≡ ALL FILTERS
          </button>
        )}

        {/* VALUE PREFERENCE Dropdown */}
        {contextFilters !== undefined && onClearContextFilters && onValuePreferenceChange && (
          <ValuePreferenceDropdown
            value={contextFilters.value_preference}
            onChange={onValuePreferenceChange}
            onClear={onClearContextFilters}
          />
        )}

        {/* Dynamic Characteristic Dropdowns */}
        {allCharacteristics.length > 0 && onCharacteristicAnswer && onClearCharacteristicAnswer && (
          <>
            {allCharacteristics.map((characteristic) => (
              <FilterDropdown
                key={characteristic.id}
                characteristic={characteristic}
                value={characteristicAnswers?.[characteristic.id]}
                onChange={(value) => onCharacteristicAnswer(characteristic.id, value)}
                onClear={() => onClearCharacteristicAnswer(characteristic.id)}
              />
            ))}
          </>
        )}

        {/* Clear All Button */}
        {hasAnyFilters && (
          <button
            onClick={clearAll}
            className="ml-auto px-3 py-1.5 text-[11px] text-gray-600 hover:text-black uppercase tracking-wide underline"
          >
            Clear All
          </button>
        )}
      </div>

      {/* Filter Categories */}
      <div className="space-y-4">

        {/* All Filters Section */}
        {hasAnyFilters && (
          <div>
            <div className="text-[10px] uppercase tracking-wider text-gray-500 mb-2 font-semibold">
              All Filters
            </div>
            <div className="flex gap-2 flex-wrap">
              {/* Context filter pill */}
              {contextFilters?.value_preference && (
                <div className="flex items-center gap-2 px-3 py-1.5 bg-black text-white text-xs tracking-wide">
                  <span className="text-[10px] text-gray-300 uppercase">Value:</span>
                  <span>
                    {contextFilters.value_preference === 'save_now' && 'Save Now'}
                    {contextFilters.value_preference === 'best_value' && 'Best Value'}
                    {contextFilters.value_preference === 'buy_for_life' && 'Buy for Life'}
                  </span>
                  <button
                    onClick={onClearContextFilters}
                    className="text-white hover:text-gray-300 text-xs font-bold ml-1"
                  >
                    ✕
                  </button>
                </div>
              )}

              {/* Category pill */}
              {selectedCategory && (
                <div className="flex items-center gap-2 px-3 py-1.5 bg-black text-white text-xs tracking-wide">
                  <span className="text-[10px] text-gray-300 uppercase">Category:</span>
                  <span>{selectedCategory}</span>
                  <button
                    onClick={onRemoveCategory}
                    className="text-white hover:text-gray-300 text-xs font-bold ml-1"
                  >
                    ✕
                  </button>
                </div>
              )}

              {/* Material pills */}
              {selectedMaterials.map((material) => (
                <div
                  key={material}
                  className="flex items-center gap-2 px-3 py-1.5 bg-black text-white text-xs tracking-wide"
                >
                  <span className="text-[10px] text-gray-300 uppercase">Material:</span>
                  <span>{material}</span>
                  <button
                    onClick={() => onRemoveMaterial(material)}
                    className="text-white hover:text-gray-300 text-xs font-bold ml-1"
                  >
                    ✕
                  </button>
                </div>
              ))}

              {/* Tier pill */}
              {selectedTier && (
                <div className="flex items-center gap-2 px-3 py-1.5 bg-black text-white text-xs tracking-wide">
                  <span className="text-[10px] text-gray-300 uppercase">Value Tier:</span>
                  <span>{selectedTier}</span>
                  <button
                    onClick={onRemoveTier}
                    className="text-white hover:text-gray-300 text-xs font-bold ml-1"
                  >
                    ✕
                  </button>
                </div>
              )}

              {/* Characteristic pills */}
              {selectedCharacteristics.map((char) => (
                <div
                  key={char}
                  className="flex items-center gap-2 px-3 py-1.5 bg-black text-white text-xs tracking-wide"
                >
                  <span>{char}</span>
                  <button
                    onClick={() => onRemoveCharacteristic(char)}
                    className="text-white hover:text-gray-300 text-xs font-bold ml-1"
                  >
                    ✕
                  </button>
                </div>
              ))}

              {/* Dynamic characteristic answer pills */}
              {characteristicAnswers && onClearCharacteristicAnswer && Object.entries(characteristicAnswers).map(([id, value]) => {
                const characteristic = allCharacteristics.find(c => c.id === id)
                if (!characteristic) return null

                const displayValue = Array.isArray(value)
                  ? value.length === 1
                    ? characteristic.options.find(o => o.value === value[0])?.label || value[0]
                    : `${value.length} selected`
                  : characteristic.options.find(o => o.value === value)?.label || value

                return (
                  <div
                    key={id}
                    className="flex items-center gap-2 px-3 py-1.5 bg-black text-white text-xs tracking-wide"
                  >
                    <span className="text-[10px] text-gray-300 uppercase">{characteristic.filterLabel}:</span>
                    <span>{displayValue}</span>
                    <button
                      onClick={() => onClearCharacteristicAnswer(id)}
                      className="text-white hover:text-gray-300 text-xs font-bold ml-1"
                    >
                      ✕
                    </button>
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {/* Individual Filter Categories - Show only when active */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Material Filter */}
          {hasMaterials && (
            <div>
              <div className="text-[10px] uppercase tracking-wider text-gray-500 mb-2 font-semibold">
                Material
              </div>
              <div className="flex gap-2 flex-wrap">
                {selectedMaterials.map((material) => (
                  <div
                    key={material}
                    className="flex items-center gap-1.5 px-3 py-1 border border-gray-300 text-xs"
                  >
                    <span>{material}</span>
                    <button
                      onClick={() => onRemoveMaterial(material)}
                      className="text-gray-500 hover:text-black text-xs"
                    >
                      ✕
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Value Tier Filter */}
          {selectedTier && (
            <div>
              <div className="text-[10px] uppercase tracking-wider text-gray-500 mb-2 font-semibold">
                Value Tier
              </div>
              <div className="flex gap-2 flex-wrap">
                <div className="flex items-center gap-1.5 px-3 py-1 border border-gray-300 text-xs">
                  <span>{selectedTier}</span>
                  <button
                    onClick={onRemoveTier}
                    className="text-gray-500 hover:text-black text-xs"
                  >
                    ✕
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Category Filter */}
          {selectedCategory && (
            <div>
              <div className="text-[10px] uppercase tracking-wider text-gray-500 mb-2 font-semibold">
                Category
              </div>
              <div className="flex gap-2 flex-wrap">
                <div className="flex items-center gap-1.5 px-3 py-1 border border-gray-300 text-xs">
                  <span>{selectedCategory}</span>
                  <button
                    onClick={onRemoveCategory}
                    className="text-gray-500 hover:text-black text-xs"
                  >
                    ✕
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
