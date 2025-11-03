'use client'

import { useState, useRef, useEffect } from 'react'
import type { CharacteristicConfig } from '@/types/characteristics'

interface FilterDropdownProps {
  characteristic: CharacteristicConfig
  value: string | string[] | undefined
  onChange: (value: string | string[]) => void
  onClear: () => void
}

export default function FilterDropdown({
  characteristic,
  value,
  onChange,
  onClear
}: FilterDropdownProps) {
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
      return () => document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isOpen])

  const handleOptionClick = (optionValue: string, e: React.MouseEvent) => {
    e.stopPropagation()
    console.log('Option clicked:', optionValue)

    if (characteristic.multiSelect) {
      // Multi-select logic
      const currentValues = Array.isArray(value) ? value : value ? [value] : []
      if (currentValues.includes(optionValue)) {
        const newValues = currentValues.filter(v => v !== optionValue)
        if (newValues.length === 0) {
          onClear()
        } else {
          onChange(newValues)
        }
      } else {
        onChange([...currentValues, optionValue])
      }
    } else {
      // Single select logic
      if (value === optionValue) {
        onClear()
        setIsOpen(false)
      } else {
        onChange(optionValue)
        setIsOpen(false)
      }
    }
  }

  const getDisplayLabel = () => {
    if (!value) return characteristic.placeholder || characteristic.filterLabel || 'Select'

    if (Array.isArray(value)) {
      if (value.length === 0) return characteristic.placeholder || characteristic.filterLabel || 'Select'
      if (value.length === 1) {
        const option = characteristic.options.find(o => o.value === value[0])
        return option?.label || value[0]
      }
      return `${value.length} selected`
    }

    const option = characteristic.options.find(o => o.value === value)
    return option?.label || value
  }

  const isSelected = (optionValue: string): boolean => {
    if (!value) return false
    if (Array.isArray(value)) return value.includes(optionValue)
    return value === optionValue
  }

  const hasValue = Array.isArray(value) ? value.length > 0 : !!value

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Dropdown Button */}
      <button
        type="button"
        onClick={(e) => {
          e.stopPropagation()
          e.preventDefault()
          console.log('FilterDropdown clicked:', characteristic.filterLabel, 'current isOpen:', isOpen, 'will toggle to:', !isOpen)
          setIsOpen(prev => !prev)
        }}
        className={`flex items-center gap-2 px-3 py-1.5 text-[11px] uppercase tracking-wider font-semibold transition-colors cursor-pointer select-none ${
          hasValue
            ? 'bg-black text-white'
            : 'bg-white text-black border border-gray-300 hover:border-black'
        }`}
        style={{ pointerEvents: 'auto' }}
      >
        {characteristic.filterLabel || characteristic.question}
        <span className="text-[10px]">{isOpen ? '▲' : '▼'}</span>
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute top-full left-0 mt-1 bg-white border border-gray-300 shadow-lg z-[9999] min-w-[200px] max-w-[300px] animate-slideDown">
          {/* Header with "Why it matters" tooltip */}
          {characteristic.whyItMatters && (
            <div className="px-4 py-3 border-b border-gray-200 bg-gray-50">
              <p className="text-[10px] text-gray-600 leading-relaxed">
                💡 {characteristic.whyItMatters}
              </p>
            </div>
          )}

          {/* Options */}
          <div className="max-h-[300px] overflow-y-auto">
            {characteristic.options.map((option) => {
              const selected = isSelected(option.value)

              return (
                <button
                  key={option.value}
                  type="button"
                  onClick={(e) => handleOptionClick(option.value, e)}
                  className={`w-full text-left px-4 py-3 hover:bg-gray-50 transition-colors border-b border-gray-100 last:border-b-0 ${
                    selected ? 'bg-gray-100' : ''
                  }`}
                >
                  <div className="flex items-start gap-2">
                    {/* Checkbox/Radio indicator */}
                    <div className={`flex-shrink-0 w-4 h-4 mt-0.5 border rounded ${
                      characteristic.multiSelect ? '' : 'rounded-full'
                    } ${
                      selected
                        ? 'bg-black border-black'
                        : 'border-gray-300'
                    } flex items-center justify-center`}>
                      {selected && (
                        <span className="text-white text-[10px]">✓</span>
                      )}
                    </div>

                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        {option.icon && <span className="text-sm">{option.icon}</span>}
                        <span className={`text-[12px] font-semibold ${
                          selected ? 'text-black' : 'text-gray-900'
                        }`}>
                          {option.label}
                        </span>
                      </div>

                      {option.description && (
                        <p className="text-[10px] text-gray-500 mt-1">
                          {option.description}
                        </p>
                      )}

                      {option.recommendedFor && option.recommendedFor.length > 0 && (
                        <p className="text-[10px] text-gray-400 mt-1">
                          Best for: {option.recommendedFor.join(', ')}
                        </p>
                      )}
                    </div>
                  </div>
                </button>
              )
            })}
          </div>

          {/* Footer - Clear button */}
          {hasValue && (
            <div className="px-4 py-2 border-t border-gray-200 bg-gray-50">
              <button
                onClick={() => {
                  onClear()
                  setIsOpen(false)
                }}
                className="text-[10px] text-gray-600 hover:text-black uppercase tracking-wide underline"
              >
                Clear
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
