'use client'

import { useState } from 'react'

interface SearchInterfaceProps {
  onSearch: (query: string) => void
  isLoading: boolean
}

const exampleQueries = [
  "I need a cast iron skillet that won't rust easily",
  "Chef's knife for a beginner home cook",
  "Dutch oven I can pass down to my kids",
  "Budget pan for college student that won't warp",
]

export default function SearchInterface({ onSearch, isLoading }: SearchInterfaceProps) {
  const [query, setQuery] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim()) {
      onSearch(query)
    }
  }

  const handleExampleClick = (example: string) => {
    setQuery(example)
    onSearch(example)
  }

  return (
    <div className="w-full max-w-4xl mx-auto">
      {/* Hero Section */}
      <div className="text-center mb-8">
        <h1 className="text-5xl font-bold text-gray-900 mb-4">
          Kenny
        </h1>
        <p className="text-xl text-gray-600 mb-2">
          Find Kitchen Products That Actually Last
        </p>
        <p className="text-sm text-gray-500">
          Discover high-quality options organized by Good/Better/Best with transparent value metrics
        </p>
      </div>

      {/* Search Form */}
      <form onSubmit={handleSubmit} className="mb-6">
        <div className="relative">
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
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
