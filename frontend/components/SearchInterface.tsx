'use client'

import { useState } from 'react'

interface SearchInterfaceProps {
  onSearch: (query: string, maxPrice?: number) => void
  isLoading: boolean
  // WebSocket progress props
  wsConnected?: boolean
  progressMessage?: string
  currentAgent?: string
  totalSearches?: number
}

export default function SearchInterface({
  onSearch,
  isLoading,
  wsConnected,
  progressMessage,
  currentAgent,
  totalSearches
}: SearchInterfaceProps) {
  const [query, setQuery] = useState('')

  // Map technical phase names to user-friendly display names
  const getPhaseDisplayName = (phase: string) => {
    switch (phase) {
      case 'product_finder':
        return 'Researching What Makes a Great Product'
      case 'context_discovery':
      case 'contextual_search':
        return 'Researching Top Products & Reviews'
      default:
        return phase
    }
  }

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
      {/* Search Bar with Input Filters */}
      <form onSubmit={handleSubmit} role="search" aria-label="Search for kitchen products">
        <div className="flex items-start gap-3 flex-wrap">
          {/* Search Input */}
          <div className="flex items-center border border-black py-3 px-4 flex-1 min-w-[300px] max-w-[600px]">
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
        </div>
      </form>

      {/* Helper Text */}
      <p id="search-helper-text" className="text-[13px] text-gray-500 mt-3 tracking-wide">
        {isLoading ? (
          <span className="flex items-center gap-2">
            <span className="inline-block animate-swing-pickaxe text-2xl">⛏️</span>
            <span>
              {wsConnected && progressMessage ? (
                <>
                  {progressMessage}
                  {currentAgent && <span className="ml-2">{getPhaseDisplayName(currentAgent)}</span>}
                  {totalSearches !== undefined && totalSearches > 0 && (
                    <span className="ml-2">{totalSearches} AI searches executed</span>
                  )}
                </>
              ) : (
                'Kenny is digging... Analyzing Reddit, expert reviews, and user reports'
              )}
            </span>
          </span>
        ) : (
          '💡 Search to see Kenny\'s buying guidance'
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
