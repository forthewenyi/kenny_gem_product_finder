'use client'

import { useState, useRef, useEffect } from 'react'
import type { ContextFilters } from './ContextFiltersBar'

interface ValuePreferenceDropdownProps {
  value: ContextFilters['value_preference']
  onChange: (value: 'save_now' | 'best_value' | 'buy_for_life') => void
  onClear: () => void
}

const VALUE_OPTIONS = [
  {
    value: 'save_now' as const,
    label: 'Save Now',
    description: 'Lowest upfront cost, 2-5 year lifespan'
  },
  {
    value: 'best_value' as const,
    label: 'Best Value',
    description: 'Sweet spot for durability, 8-15 years'
  },
  {
    value: 'buy_for_life' as const,
    label: 'Buy for Life',
    description: 'Maximum quality, 15-30+ years'
  }
]

export default function ValuePreferenceDropdown({
  value,
  onChange,
  onClear
}: ValuePreferenceDropdownProps) {
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

  const handleOptionClick = (optionValue: 'save_now' | 'best_value' | 'buy_for_life') => {
    if (value === optionValue) {
      onClear()
      setIsOpen(false)
    } else {
      onChange(optionValue)
      setIsOpen(false)
    }
  }

  const getDisplayLabel = () => {
    if (!value) return 'VALUE PREFERENCE'
    const option = VALUE_OPTIONS.find(o => o.value === value)
    return option?.label || 'VALUE PREFERENCE'
  }

  const hasValue = !!value

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Dropdown Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`flex items-center gap-2 px-3 py-1.5 text-[11px] uppercase tracking-wider font-semibold transition-colors ${
          hasValue
            ? 'bg-black text-white'
            : 'bg-white text-black border border-gray-300 hover:border-black'
        }`}
      >
        {getDisplayLabel()}
        <span className="text-[10px]">{isOpen ? '▲' : '▼'}</span>
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute top-full left-0 mt-1 bg-white border border-gray-300 shadow-lg z-50 min-w-[280px] animate-slideDown">
          {/* Header */}
          <div className="px-4 py-3 border-b border-gray-200 bg-gray-50">
            <p className="text-[10px] text-gray-600 leading-relaxed">
              💡 Choose your value approach: prioritize upfront savings, long-term value, or maximum durability
            </p>
          </div>

          {/* Options */}
          <div>
            {VALUE_OPTIONS.map((option) => {
              const selected = value === option.value

              return (
                <button
                  key={option.value}
                  onClick={() => handleOptionClick(option.value)}
                  className={`w-full text-left px-4 py-3 hover:bg-gray-50 transition-colors border-b border-gray-100 last:border-b-0 ${
                    selected ? 'bg-gray-100' : ''
                  }`}
                >
                  <div className="flex items-start gap-2">
                    {/* Radio indicator */}
                    <div className={`flex-shrink-0 w-4 h-4 mt-0.5 border rounded-full ${
                      selected
                        ? 'bg-black border-black'
                        : 'border-gray-300'
                    } flex items-center justify-center`}>
                      {selected && (
                        <span className="text-white text-[10px]">✓</span>
                      )}
                    </div>

                    <div className="flex-1">
                      <span className={`text-[12px] font-semibold ${
                        selected ? 'text-black' : 'text-gray-900'
                      }`}>
                        {option.label}
                      </span>

                      <p className="text-[10px] text-gray-500 mt-1">
                        {option.description}
                      </p>
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
