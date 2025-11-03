'use client'

import { useState, useEffect } from 'react'
import type { ContextFilters, FilterCategory } from './ContextFiltersBar'

interface ContextFilterDrawerProps {
  isOpen: boolean
  onClose: () => void
  filters: ContextFilters
  onApplyFilters: (filters: ContextFilters) => void
  initialSection?: FilterCategory
}

type CollapsibleSection = 'value_preference'

export default function ContextFilterDrawer({
  isOpen,
  onClose,
  filters,
  onApplyFilters,
  initialSection
}: ContextFilterDrawerProps) {
  const [tempFilters, setTempFilters] = useState<ContextFilters>(filters)
  const [expandedSection, setExpandedSection] = useState<CollapsibleSection | null>(
    initialSection ? (initialSection as CollapsibleSection) : 'value_preference'
  )

  // Update temp filters when props change
  useEffect(() => {
    setTempFilters(filters)
  }, [filters])

  // Set expanded section based on initial section
  useEffect(() => {
    if (initialSection) {
      setExpandedSection(initialSection as CollapsibleSection)
    }
  }, [initialSection])

  const toggleSection = (section: CollapsibleSection) => {
    setExpandedSection(expandedSection === section ? null : section)
  }

  const handleApply = () => {
    onApplyFilters(tempFilters)
    onClose()
  }

  const handleClearAll = () => {
    setTempFilters({})
  }

  const handleRadioChange = (category: CollapsibleSection, value: 'save_now' | 'best_value' | 'buy_for_life') => {
    setTempFilters(prev => ({
      ...prev,
      [category]: prev[category] === value ? undefined : value
    }))
  }

  // Filter options
  const valuePreferenceOptions = [
    { value: 'save_now' as const, label: 'Save Now', description: 'Lowest upfront cost, 2-5 year lifespan' },
    { value: 'best_value' as const, label: 'Best Value', description: 'Sweet spot for durability, 8-15 years' },
    { value: 'buy_for_life' as const, label: 'Buy for Life', description: 'Maximum quality, 15-30+ years' }
  ]

  const FilterSection = ({
    section,
    title,
    options
  }: {
    section: CollapsibleSection
    title: string
    options: { value: 'save_now' | 'best_value' | 'buy_for_life'; label: string; description: string }[]
  }) => {
    const isExpanded = expandedSection === section
    const selectedValue = tempFilters[section]

    return (
      <div className="border-b border-gray-200">
        {/* Section Header */}
        <button
          onClick={() => toggleSection(section)}
          className="w-full flex items-center justify-between px-6 py-4 text-left hover:bg-gray-50 transition-colors"
        >
          <span className="text-[13px] uppercase tracking-wider font-semibold text-black">
            {title}
          </span>
          <span className="text-lg">
            {isExpanded ? '−' : '+'}
          </span>
        </button>

        {/* Section Content */}
        {isExpanded && (
          <div className="px-6 pb-4 space-y-3 animate-slideDown">
            {options.map(option => (
              <label
                key={option.value}
                className="flex items-start gap-3 py-3 cursor-pointer hover:bg-gray-50 px-3 -mx-3 rounded transition-colors"
              >
                <input
                  type="radio"
                  name={section}
                  value={option.value}
                  checked={selectedValue === option.value}
                  onChange={() => handleRadioChange(section, option.value)}
                  className="w-4 h-4 mt-0.5 text-black border-gray-300 focus:ring-black"
                />
                <div className="flex-1">
                  <div className="text-[13px] font-semibold text-gray-900">
                    {option.label}
                  </div>
                  <div className="text-[11px] text-gray-500 mt-0.5">
                    {option.description}
                  </div>
                </div>
              </label>
            ))}
          </div>
        )}
      </div>
    )
  }

  return (
    <>
      {/* Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-40 z-50 animate-fadeIn"
          onClick={onClose}
        />
      )}

      {/* Drawer */}
      <div
        className={`fixed top-0 right-0 h-full w-full md:w-[400px] bg-white shadow-2xl z-50 flex flex-col transition-transform duration-300 ease-out ${
          isOpen ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-5 border-b border-gray-200">
          <h2 className="text-[15px] uppercase tracking-wider font-bold">
            Filters
          </h2>
          <button
            onClick={onClose}
            className="text-2xl hover:text-gray-600 transition-colors"
            aria-label="Close filters"
          >
            ✕
          </button>
        </div>

        {/* Scrollable Content */}
        <div className="flex-1 overflow-y-auto">
          <FilterSection
            section="value_preference"
            title="Value Preference"
            options={valuePreferenceOptions}
          />
        </div>

        {/* Footer */}
        <div className="px-6 py-5 border-t border-gray-200 space-y-3 bg-white">
          {/* Clear All Link */}
          <button
            onClick={handleClearAll}
            className="text-[12px] text-gray-600 hover:text-black uppercase tracking-wide underline w-full text-center"
          >
            Clear All
          </button>

          {/* Apply Button */}
          <button
            onClick={handleApply}
            className="w-full bg-black text-white py-3.5 text-[12px] uppercase tracking-wider font-semibold hover:bg-gray-800 transition-colors"
          >
            Apply Filters
          </button>
        </div>
      </div>
    </>
  )
}
