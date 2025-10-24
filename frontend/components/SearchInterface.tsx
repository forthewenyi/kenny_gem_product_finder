'use client'

import { useState } from 'react'

interface SearchInterfaceProps {
  onSearch: (query: string, maxPrice?: number) => void
  isLoading: boolean
}

const exampleQueries = [
  "I need a cast iron skillet that won't rust easily",
  "Chef's knife for a beginner home cook",
  "Dutch oven I can pass down to my kids",
]

export default function SearchInterface({ onSearch, isLoading }: SearchInterfaceProps) {
  const [query, setQuery] = useState('')
  const [maxPrice, setMaxPrice] = useState(600)
  const [showFilters, setShowFilters] = useState(false)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim()) {
      onSearch(query, maxPrice)
    }
  }

  const handleExampleClick = (example: string) => {
    setQuery(example)
    onSearch(example, maxPrice)
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Submit on Enter (without Shift for new line)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      if (query.trim()) {
        onSearch(query, maxPrice)
      }
    }
  }

  const formatPrice = (price: number) => {
    if (price >= 600) return '$600+'
    return `$${price}`
  }

  return (
    <div className="w-full max-w-4xl mx-auto">
      {/* Hero Section */}
      <div className="text-center mb-8">
        <h1 className="text-5xl font-bold text-gray-900 mb-4">
          Kenny
        </h1>
        <p className="text-xl text-gray-600 mb-2">
          Buy less. Buy better. Know the real cost.
        </p>
      </div>

      {/* Search Form */}
      <form onSubmit={handleSubmit} className="mb-6">
        <div className="relative">
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Describe what you're looking for... (e.g., 'I need a chef's knife that stays sharp for beginners')"
            className="w-full px-6 py-4 text-lg border-2 border-gray-300 rounded-2xl focus:border-blue-500 focus:outline-none resize-none"
            rows={3}
            disabled={isLoading}
          />
        </div>

        <button
          type="submit"
          disabled={isLoading || !query.trim()}
          className="mt-4 w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold py-4 px-8 rounded-xl transition-colors text-lg"
        >
          {isLoading ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              Researching the web...
            </span>
          ) : (
            'Search for Kitchen Gems 🔍'
          )}
        </button>

        {/* Price Filter Toggle - Below Search Button */}
        <div className="mt-4">
          <button
            type="button"
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900 transition-colors"
          >
            <svg className={`w-4 h-4 transition-transform ${showFilters ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
            {showFilters ? 'Hide' : 'Show'} Price Filter
          </button>
        </div>

        {/* Price Range Slider - Collapsible */}
        {showFilters && (
          <div className="mt-3 p-4 bg-gray-50 rounded-xl border border-gray-200">
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Maximum Price: <span className="text-blue-600 font-semibold">{formatPrice(maxPrice)}</span>
            </label>
            <input
              type="range"
              min="20"
              max="600"
              step="10"
              value={maxPrice}
              onChange={(e) => setMaxPrice(parseInt(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
              disabled={isLoading}
            />
            <div className="flex justify-between text-xs text-gray-500 mt-2">
              <span>$20</span>
              <span>$100</span>
              <span>$200</span>
              <span>$400</span>
              <span>$600+</span>
            </div>
            <p className="text-xs text-gray-500 mt-3">
              Filter results to show products up to your budget
            </p>
          </div>
        )}
      </form>

      {/* Example Queries */}
      {!isLoading && (
        <div>
          <p className="text-sm text-gray-500 mb-3">Try these examples:</p>
          <div className="flex flex-wrap gap-2">
            {exampleQueries.map((example, idx) => (
              <button
                key={idx}
                onClick={() => handleExampleClick(example)}
                className="text-sm px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-full transition-colors"
              >
                {example}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
