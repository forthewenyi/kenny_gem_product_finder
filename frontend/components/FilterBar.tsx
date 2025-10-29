'use client'

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
}

export default function FilterBar({
  selectedCharacteristics,
  onRemoveCharacteristic,
  selectedCategory,
  onRemoveCategory,
  selectedMaterials,
  onRemoveMaterial,
  selectedTier,
  onRemoveTier
}: FilterBarProps) {
  const hasCharacteristics = selectedCharacteristics.length > 0
  const hasMaterials = selectedMaterials.length > 0
  const hasAnyFilters = hasCharacteristics || selectedCategory || hasMaterials || selectedTier

  const clearAll = () => {
    selectedCharacteristics.forEach(char => onRemoveCharacteristic(char))
    selectedMaterials.forEach(mat => onRemoveMaterial(mat))
    if (selectedCategory && onRemoveCategory) onRemoveCategory()
    if (selectedTier && onRemoveTier) onRemoveTier()
  }

  return (
    <div className="border-t border-b border-gray-200 py-6 px-10 max-w-[1400px] mx-auto">
      {/* Header Row */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <span className="text-sm">☰</span>
          <span className="text-xs uppercase tracking-wide font-semibold text-gray-700">
            Filters
          </span>
        </div>

        {hasAnyFilters && (
          <button
            onClick={clearAll}
            className="text-xs text-gray-600 hover:text-black uppercase tracking-wide underline"
          >
            Clear All
          </button>
        )}
      </div>

      {/* Filter Categories */}
      <div className="space-y-4">
        {/* No Filters State */}
        {!hasAnyFilters && (
          <div className="text-xs text-gray-500 tracking-wide">
            Click on characteristics above or select filters below to refine your results
          </div>
        )}

        {/* All Filters Section */}
        {hasAnyFilters && (
          <div>
            <div className="text-[10px] uppercase tracking-wider text-gray-500 mb-2 font-semibold">
              All Filters
            </div>
            <div className="flex gap-2 flex-wrap">
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
