'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { getPopularSearches, trackSearch, type PopularSearchItem } from '@/lib/api'

interface NavigationDropdownProps {
  category: 'cookware' | 'knives' | 'bakeware'
  label: string
  onSearch: (query: string, category: string) => void
}

export default function NavigationDropdown({ category, label, onSearch }: NavigationDropdownProps) {
  const [isOpen, setIsOpen] = useState(false)

  // Fetch popular searches on hover/click
  const { data, isLoading } = useQuery({
    queryKey: ['popular-searches', category],
    queryFn: () => getPopularSearches(category),
    enabled: isOpen, // Only fetch when dropdown is open
    staleTime: 1000 * 60 * 60, // Cache for 1 hour
  })

  const handleItemClick = async (term: string) => {
    // Track the search (fire-and-forget)
    trackSearch(term, category)

    // Trigger the search
    onSearch(term, category)

    // Close dropdown
    setIsOpen(false)
  }

  const handleMouseEnter = () => {
    setIsOpen(true)
  }

  const handleMouseLeave = () => {
    setIsOpen(false)
  }

  return (
    <div
      className="relative"
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      {/* Trigger Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="text-xs uppercase tracking-wide text-black border-b-2 border-transparent hover:border-black transition-colors pb-0.5 cursor-pointer"
        aria-expanded={isOpen}
        aria-haspopup="true"
      >
        {label}
      </button>

      {/* Dropdown Menu - Now part of the same hover zone */}
      {isOpen && (
        <div className="absolute top-full left-0 pt-2 z-50">
          <div className="bg-white shadow-xl rounded-xl border border-gray-200 py-1.5 min-w-[240px] animate-slideDown">
          {isLoading && (
            <div className="px-4 py-3 text-[11px] text-[#79786c] uppercase tracking-wide">
              Loading...
            </div>
          )}

          {!isLoading && data?.items && data.items.length === 0 && (
            <div className="px-4 py-3 text-[11px] text-[#79786c] uppercase tracking-wide">
              No popular searches yet
            </div>
          )}

          {!isLoading && data?.items && data.items.length > 0 && (
            <ul className="max-h-[400px] overflow-y-auto">
              {data.items.map((item: PopularSearchItem, idx: number) => (
                <li key={idx}>
                  <button
                    onClick={() => handleItemClick(item.term)}
                    className="w-full text-left px-5 py-2.5 text-[11px] hover:bg-[#f8f8f8] transition-colors flex items-center justify-between group"
                  >
                    <span className="text-black uppercase tracking-wide group-hover:font-medium">
                      {item.term}
                    </span>
                    <span className="text-[10px] text-[#79786c] lowercase">
                      {item.count}
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          )}
          </div>
        </div>
      )}
    </div>
  )
}
