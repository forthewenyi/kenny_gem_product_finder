'use client'

interface FilterBarProps {
  selectedCharacteristics: string[]
  onRemoveFilter: (characteristic: string) => void
}

export default function FilterBar({
  selectedCharacteristics,
  onRemoveFilter
}: FilterBarProps) {
  const hasFilters = selectedCharacteristics.length > 0

  return (
    <div className="border-t border-b border-gray-200 py-4 px-10 max-w-[1400px] mx-auto">
      <div className="flex gap-4 items-center flex-wrap">
        {/* Filters Label */}
        <div className="flex items-center gap-2">
          <span className="text-sm">☰</span>
          <span className="text-xs uppercase tracking-wide font-semibold text-gray-700">
            {hasFilters ? 'Active Filters:' : 'Filters'}
          </span>
        </div>

        {/* No Filters State */}
        {!hasFilters && (
          <span className="text-xs text-gray-500 tracking-wide">
            Click on characteristics above to filter products
          </span>
        )}

        {/* Selected Filters Pills */}
        {selectedCharacteristics.map((char) => (
          <div
            key={char}
            className="flex items-center gap-2 px-4 py-2 bg-black text-white text-xs uppercase tracking-wide"
          >
            <span>{char}</span>
            <button
              onClick={() => onRemoveFilter(char)}
              className="text-white hover:text-gray-300 font-bold"
            >
              ✕
            </button>
          </div>
        ))}

        {/* Clear All Button */}
        {selectedCharacteristics.length > 1 && (
          <button
            onClick={() => {
              selectedCharacteristics.forEach(char => onRemoveFilter(char))
            }}
            className="text-xs text-gray-600 hover:text-black uppercase tracking-wide underline"
          >
            Clear All
          </button>
        )}
      </div>
    </div>
  )
}
