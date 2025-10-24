'use client'

import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { searchProducts } from '@/lib/api'
import type { SearchResponse, Product } from '@/types'

import SearchInterface from '@/components/SearchInterface'
import ProductCard from '@/components/ProductCard'
import LoadingState from '@/components/LoadingState'
import TierBadge from '@/components/TierBadge'

export default function Home() {
  const [results, setResults] = useState<SearchResponse | null>(null)
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null)

  const searchMutation = useMutation({
    mutationFn: (query: string) => searchProducts({ query }),
    onSuccess: (data) => {
      setResults(data)
      setSelectedProduct(null)
    },
  })

  const handleSearch = (query: string) => {
    searchMutation.mutate(query)
  }

  const allProducts = results
    ? [
        ...results.results.best.map(p => ({ ...p, tier: 'best' as const })),
        ...results.results.better.map(p => ({ ...p, tier: 'better' as const })),
        ...results.results.good.map(p => ({ ...p, tier: 'good' as const })),
      ]
    : []

  return (
    <main className="min-h-screen bg-gradient-to-b from-gray-50 to-white py-12 px-4">
      <div className="container mx-auto">
        {/* Search Interface */}
        <SearchInterface
          onSearch={handleSearch}
          isLoading={searchMutation.isPending}
        />

        {/* Loading State */}
        {searchMutation.isPending && <LoadingState />}

        {/* Error State */}
        {searchMutation.isError && (
          <div className="max-w-2xl mx-auto mt-12 p-6 bg-red-50 border border-red-200 rounded-lg">
            <h3 className="text-lg font-semibold text-red-900 mb-2">
              Search Failed
            </h3>
            <p className="text-red-700">
              {searchMutation.error instanceof Error
                ? searchMutation.error.message
                : 'An error occurred while searching. Please try again.'}
            </p>
            <button
              onClick={() => searchMutation.reset()}
              className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
            >
              Try Again
            </button>
          </div>
        )}

        {/* Results */}
        {results && !searchMutation.isPending && (
          <div className="mt-12">
            {/* Metadata */}
            <div className="max-w-6xl mx-auto mb-8">
              <div className="flex items-center justify-between text-sm text-gray-600">
                <div>
                  Found {allProducts.length} products in {results.processing_time_seconds}s
                </div>
                <div>
                  Searched {results.search_metadata.sources_searched.length} sources
                </div>
              </div>
            </div>

            {/* Educational Insights */}
            {results.educational_insights.length > 0 && (
              <div className="max-w-6xl mx-auto mb-8">
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <h3 className="font-semibold text-yellow-900 mb-2">💡 Good to Know</h3>
                  <ul className="space-y-1">
                    {results.educational_insights.map((insight, idx) => (
                      <li key={idx} className="text-sm text-yellow-800">
                        • {insight}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}

            {/* BEST Tier */}
            {results.results.best.length > 0 && (
              <div className="max-w-6xl mx-auto mb-12">
                <div className="mb-6">
                  <TierBadge tier="best" size="lg" />
                  <p className="text-sm text-gray-600 mt-2">
                    Lifetime investment • 15-30+ years • Heirloom quality
                  </p>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {results.results.best.map((product, idx) => (
                    <ProductCard
                      key={idx}
                      product={product}
                      onClick={() => setSelectedProduct(product)}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* BETTER Tier */}
            {results.results.better.length > 0 && (
              <div className="max-w-6xl mx-auto mb-12">
                <div className="mb-6">
                  <TierBadge tier="better" size="lg" />
                  <p className="text-sm text-gray-600 mt-2">
                    Best value • 8-15 years • First-time homeowners
                  </p>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {results.results.better.map((product, idx) => (
                    <ProductCard
                      key={idx}
                      product={product}
                      onClick={() => setSelectedProduct(product)}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* GOOD Tier */}
            {results.results.good.length > 0 && (
              <div className="max-w-6xl mx-auto mb-12">
                <div className="mb-6">
                  <TierBadge tier="good" size="lg" />
                  <p className="text-sm text-gray-600 mt-2">
                    Budget-friendly • 2-5 years • Students & renters
                  </p>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {results.results.good.map((product, idx) => (
                    <ProductCard
                      key={idx}
                      product={product}
                      onClick={() => setSelectedProduct(product)}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* No Results */}
            {allProducts.length === 0 && (
              <div className="max-w-2xl mx-auto text-center py-12">
                <p className="text-gray-600">
                  No products found. Try a different search query.
                </p>
              </div>
            )}
          </div>
        )}

        {/* Product Detail Modal (Simple version) */}
        {selectedProduct && (
          <div
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
            onClick={() => setSelectedProduct(null)}
          >
            <div
              className="bg-white rounded-2xl p-8 max-w-2xl max-h-[90vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="mb-4">
                <TierBadge tier={selectedProduct.tier} size="lg" />
              </div>
              <h2 className="text-3xl font-bold text-gray-900 mb-2">
                {selectedProduct.name}
              </h2>
              <p className="text-lg text-gray-600 mb-6">{selectedProduct.brand}</p>

              {/* Value Metrics */}
              <div className="bg-blue-50 rounded-xl p-6 mb-6">
                <h3 className="font-semibold text-blue-900 mb-4">💰 Value Analysis</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <div className="text-sm text-gray-600">Upfront Price</div>
                    <div className="text-2xl font-bold text-blue-900">
                      ${selectedProduct.value_metrics.upfront_price}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600">Lifespan</div>
                    <div className="text-2xl font-bold text-blue-900">
                      {selectedProduct.value_metrics.expected_lifespan_years} years
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600">Cost per Year</div>
                    <div className="text-xl font-semibold text-blue-900">
                      ${selectedProduct.value_metrics.cost_per_year}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600">Cost per Day</div>
                    <div className="text-xl font-semibold text-blue-900">
                      ${selectedProduct.value_metrics.cost_per_day}
                    </div>
                  </div>
                </div>
              </div>

              {/* Why It's a Gem */}
              <div className="mb-6">
                <h3 className="font-semibold text-gray-900 mb-2">🔍 Why it's a gem</h3>
                <p className="text-gray-700">{selectedProduct.why_its_a_gem}</p>
              </div>

              {/* Key Features */}
              <div className="mb-6">
                <h3 className="font-semibold text-gray-900 mb-2">✓ Key Features</h3>
                <ul className="space-y-2">
                  {selectedProduct.key_features.map((feature, idx) => (
                    <li key={idx} className="flex items-start">
                      <span className="text-green-500 mr-2">✓</span>
                      <span className="text-gray-700">{feature}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Trade-offs */}
              {selectedProduct.trade_offs && selectedProduct.trade_offs.length > 0 && (
                <div className="mb-6">
                  <h3 className="font-semibold text-gray-900 mb-2">⚠️ Trade-offs</h3>
                  <ul className="space-y-2">
                    {selectedProduct.trade_offs.map((tradeoff, idx) => (
                      <li key={idx} className="text-sm text-gray-600">
                        • {tradeoff}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Web Sources */}
              {selectedProduct.web_sources && selectedProduct.web_sources.length > 0 && (
                <div className="mb-6">
                  <h3 className="font-semibold text-gray-900 mb-2">📚 Sources</h3>
                  <div className="space-y-2">
                    {selectedProduct.web_sources.slice(0, 3).map((source, idx) => (
                      <a
                        key={idx}
                        href={source.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="block text-sm text-blue-600 hover:text-blue-800 hover:underline"
                      >
                        {source.url.includes('reddit') ? '🟠 Reddit' : '🔗'} {source.title}
                      </a>
                    ))}
                  </div>
                </div>
              )}

              <button
                onClick={() => setSelectedProduct(null)}
                className="w-full mt-6 px-6 py-3 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        )}
      </div>
    </main>
  )
}
