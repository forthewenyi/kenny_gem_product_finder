'use client'

interface FilterBarProps {
  // Result filters (client-side filtering of displayed products)
  selectedCharacteristics: string[]
  onRemoveCharacteristic: (characteristic: string) => void

  selectedMaterials: string[]
  onRemoveMaterial: (material: string) => void

  selectedTier?: string
  onRemoveTier?: () => void
}

export default function FilterBar({
  selectedCharacteristics,
  onRemoveCharacteristic,
  selectedMaterials,
  onRemoveMaterial,
  selectedTier,
  onRemoveTier
}: FilterBarProps) {
  const hasCharacteristics = selectedCharacteristics.length > 0
  const hasMaterials = selectedMaterials.length > 0
  const hasAnyFilters = hasCharacteristics || hasMaterials || selectedTier

  const clearAll = () => {
    selectedCharacteristics.forEach(char => onRemoveCharacteristic(char))
    selectedMaterials.forEach(mat => onRemoveMaterial(mat))
    if (selectedTier && onRemoveTier) onRemoveTier()
  }


  // Don't show filter bar if no filters are active
  if (!hasAnyFilters) {
    return null
  }

  return (
    <div className="border-t border-b border-gray-200 py-4 px-10 max-w-[1400px] mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="text-[11px] uppercase tracking-wider text-gray-600 font-semibold">
          📊 Filter Results
          <span className="text-[10px] text-gray-400 ml-2 normal-case tracking-normal">
            (Narrow down products already shown)
          </span>
        </div>
        <button
          onClick={clearAll}
          className="px-3 py-1 text-[10px] text-gray-600 hover:text-black uppercase tracking-wide underline"
        >
          Clear All
        </button>
      </div>

      {/* Active Result Filters */}
      <div className="flex gap-2 flex-wrap">
        {/* Characteristic pills (from clicking aggregated_characteristics) */}
        {selectedCharacteristics.map((char) => (
          <div
            key={char}
            className="flex items-center gap-2 px-3 py-1.5 bg-gray-100 border border-gray-300 text-xs"
          >
            <span className="text-[10px] text-gray-500 uppercase">Characteristic:</span>
            <span className="text-gray-900">{char}</span>
            <button
              onClick={() => onRemoveCharacteristic(char)}
              className="text-gray-500 hover:text-black text-xs font-bold ml-1"
            >
              ✕
            </button>
          </div>
        ))}

        {/* Material pills */}
        {selectedMaterials.map((material) => (
          <div
            key={material}
            className="flex items-center gap-2 px-3 py-1.5 bg-gray-100 border border-gray-300 text-xs"
          >
            <span className="text-[10px] text-gray-500 uppercase">Material:</span>
            <span className="text-gray-900">{material}</span>
            <button
              onClick={() => onRemoveMaterial(material)}
              className="text-gray-500 hover:text-black text-xs font-bold ml-1"
            >
              ✕
            </button>
          </div>
        ))}

        {/* Tier pill */}
        {selectedTier && (
          <div className="flex items-center gap-2 px-3 py-1.5 bg-gray-100 border border-gray-300 text-xs">
            <span className="text-[10px] text-gray-500 uppercase">Tier:</span>
            <span className="text-gray-900">{selectedTier}</span>
            <button
              onClick={onRemoveTier}
              className="text-gray-500 hover:text-black text-xs font-bold ml-1"
            >
              ✕
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
