'use client'

import { useState } from 'react'

interface SearchInterfaceProps {
  onSearch: (query: string, maxPrice?: number) => void
  isLoading: boolean
}

export default function SearchInterface({ onSearch, isLoading }: SearchInterfaceProps) {
  const [query, setQuery] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim()) {
      onSearch(query)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      if (query.trim()) {
        onSearch(query)
      }
    }
  }

  return (
    <div>
      {/* Search Bar - Simple box with icon */}
      <form onSubmit={handleSubmit} role="search" aria-label="Search for kitchen products">
        <div className="flex items-center border border-black py-3 px-4 max-w-[600px] focus-within:ring-2 focus-within:ring-blue-500 transition-shadow">
          <span className="mr-3 text-base" aria-hidden="true">🔍</span>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="SEARCH FOR KITCHEN ITEMS"
            disabled={isLoading}
            className="border-none outline-none text-xs uppercase tracking-wide w-full bg-transparent placeholder:text-gray-400"
            aria-label="Search for kitchen products"
            aria-describedby="search-helper-text"
          />
        </div>
      </form>

      {/* Helper Text */}
      <p id="search-helper-text" className="text-[11px] text-gray-500 mt-2 tracking-wide">
        {isLoading ? (
          <span className="flex items-center gap-2">
            <span className="inline-block animate-swing-pickaxe text-2xl">⛏️</span>
            <span>Kenny is digging... Analyzing Reddit, expert reviews, and user reports (20-30 seconds for thorough search)</span>
          </span>
        ) : (
          '💡 Search to see Kenny\'s buying guidance for different items'
        )}
      </p>

      <style jsx>{`
        @keyframes swing-pickaxe {
          0%, 100% {
            transform: rotate(-15deg);
          }
          50% {
            transform: rotate(15deg);
          }
        }

        .animate-swing-pickaxe {
          animation: swing-pickaxe 1.5s ease-in-out infinite;
          display: inline-block;
          transform-origin: center center;
        }
      `}</style>
    </div>
  )
}
