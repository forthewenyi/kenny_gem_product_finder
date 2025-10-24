'use client'

import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { searchProducts } from '@/lib/api'
import type { SearchResponse, Product } from '@/types'

import SearchInterface from '@/components/SearchInterface'
import ProductCard from '@/components/ProductCard'
import LoadingState from '@/components/LoadingState'
import TierBadge from '@/components/TierBadge'
import DurabilityScore from '@/components/DurabilityScore'
import BeforeYouBuy from '@/components/BeforeYouBuy'

export default function Home() {
  const [results, setResults] = useState<SearchResponse | null>(null)
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null)
  const [comparisonMode, setComparisonMode] = useState(false)
  const [compareProducts, setCompareProducts] = useState<Product[]>([])

  const searchMutation = useMutation({
    mutationFn: ({ query, maxPrice }: { query: string; maxPrice?: number }) =>
      searchProducts({ query, max_price: maxPrice }),
    onSuccess: (data) => {
      setResults(data)
      setSelectedProduct(null)
      setComparisonMode(false)
      setCompareProducts([])
    },
  })

  const handleSearch = (query: string, maxPrice?: number) => {
    searchMutation.mutate({ query, maxPrice })
  }

  const toggleCompare = (product: Product) => {
    if (compareProducts.find(p => p.name === product.name)) {
      setCompareProducts(compareProducts.filter(p => p.name !== product.name))
    } else if (compareProducts.length < 3) {
      setCompareProducts([...compareProducts, product])
    }
  }

  const clearComparison = () => {
    setCompareProducts([])
    setComparisonMode(false)
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
            {/* Metadata and Comparison Toggle */}
            <div className="max-w-6xl mx-auto mb-8">
              <div className="flex items-center justify-between text-sm text-gray-600">
                <div>
                  Found {allProducts.length} products in {results.processing_time_seconds}s
                  {results.search_metadata.cached && (
                    <span className="ml-2 text-green-600 font-medium">⚡ Cached</span>
                  )}
                </div>
                <div className="flex items-center gap-4">
                  <span>Searched {results.search_metadata.sources_searched.length} sources</span>
                  <button
                    onClick={() => setComparisonMode(!comparisonMode)}
                    className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                      comparisonMode
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    }`}
                  >
                    {comparisonMode ? '✓ Comparing' : 'Compare Products'}
                  </button>
                </div>
              </div>
            </div>

            {/* Comparison Bar */}
            {comparisonMode && (
              <div className="max-w-6xl mx-auto mb-8">
                <div className="bg-blue-50 border-2 border-blue-200 rounded-xl p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-semibold text-blue-900">
                        Select products to compare (max 3)
                      </h3>
                      <p className="text-sm text-blue-700 mt-1">
                        {compareProducts.length === 0 && 'Click on product cards to add them'}
                        {compareProducts.length > 0 && `${compareProducts.length} selected`}
                      </p>
                    </div>
                    <div className="flex gap-2">
                      {compareProducts.length >= 2 && (
                        <button
                          onClick={() => {
                            // Scroll to comparison view
                            document.getElementById('comparison-view')?.scrollIntoView({ behavior: 'smooth' })
                          }}
                          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
                        >
                          View Comparison
                        </button>
                      )}
                      <button
                        onClick={clearComparison}
                        className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
                      >
                        Clear
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}

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

            {/* Before You Buy - Alternatives Section */}
            {results.before_you_buy && (
              <div className="max-w-6xl mx-auto">
                <BeforeYouBuy data={results.before_you_buy} />
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
                      onClick={() => comparisonMode ? toggleCompare(product) : setSelectedProduct(product)}
                      comparisonMode={comparisonMode}
                      isSelected={compareProducts.some(p => p.name === product.name)}
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
                      onClick={() => comparisonMode ? toggleCompare(product) : setSelectedProduct(product)}
                      comparisonMode={comparisonMode}
                      isSelected={compareProducts.some(p => p.name === product.name)}
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
                      onClick={() => comparisonMode ? toggleCompare(product) : setSelectedProduct(product)}
                      comparisonMode={comparisonMode}
                      isSelected={compareProducts.some(p => p.name === product.name)}
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

            {/* Side-by-Side Comparison View */}
            {compareProducts.length >= 2 && (
              <div id="comparison-view" className="max-w-6xl mx-auto mt-12">
                <div className="bg-white border-2 border-blue-200 rounded-2xl p-8">
                  <h2 className="text-2xl font-bold text-gray-900 mb-6">
                    Product Comparison
                  </h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {compareProducts.map((product, idx) => (
                      <div key={idx} className="relative">
                        <button
                          onClick={() => toggleCompare(product)}
                          className="absolute -top-2 -right-2 z-10 w-8 h-8 bg-red-500 text-white rounded-full hover:bg-red-600 transition-colors flex items-center justify-center font-bold"
                          title="Remove from comparison"
                        >
                          ×
                        </button>
                        <div className="border-2 border-gray-200 rounded-xl p-6">
                          <div className="mb-4">
                            <TierBadge tier={product.tier} />
                          </div>
                          <h3 className="font-bold text-lg mb-1">{product.name}</h3>
                          <p className="text-sm text-gray-600 mb-4">{product.brand}</p>

                          <div className="space-y-3">
                            <div className="bg-blue-50 rounded-lg p-3">
                              <div className="text-xs text-gray-600">Price</div>
                              <div className="text-xl font-bold text-blue-900">
                                ${product.value_metrics.upfront_price}
                              </div>
                            </div>

                            <div className="bg-green-50 rounded-lg p-3">
                              <div className="text-xs text-gray-600">Lifespan</div>
                              <div className="text-xl font-bold text-green-900">
                                {product.value_metrics.expected_lifespan_years} years
                              </div>
                            </div>

                            <div className="bg-purple-50 rounded-lg p-3">
                              <div className="text-xs text-gray-600">Cost/Year</div>
                              <div className="text-xl font-bold text-purple-900">
                                ${product.value_metrics.cost_per_year}
                              </div>
                            </div>

                            <div className="bg-orange-50 rounded-lg p-3">
                              <div className="text-xs text-gray-600">Cost/Day</div>
                              <div className="text-xl font-bold text-orange-900">
                                ${product.value_metrics.cost_per_day}
                              </div>
                            </div>
                          </div>

                          <div className="mt-4 pt-4 border-t">
                            <h4 className="text-sm font-semibold text-gray-900 mb-2">
                              Key Features:
                            </h4>
                            <ul className="space-y-1">
                              {product.key_features.slice(0, 3).map((feature, i) => (
                                <li key={i} className="text-xs text-gray-600 flex items-start">
                                  <span className="text-green-500 mr-1">✓</span>
                                  {feature}
                                </li>
                              ))}
                            </ul>
                          </div>

                          {product.best_for && (
                            <div className="mt-4 pt-4 border-t">
                              <h4 className="text-sm font-semibold text-gray-900 mb-1">
                                Best for:
                              </h4>
                              <p className="text-xs text-gray-600">{product.best_for}</p>
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Comparison Winner */}
                  <div className="mt-8 p-6 bg-gradient-to-r from-yellow-50 to-orange-50 rounded-xl border border-yellow-200">
                    <h3 className="font-bold text-yellow-900 mb-2">🏆 Best Value</h3>
                    <p className="text-sm text-yellow-800">
                      {compareProducts.reduce((best, current) =>
                        current.value_metrics.cost_per_year < best.value_metrics.cost_per_year ? current : best
                      ).name} has the lowest cost per year at ${compareProducts.reduce((best, current) =>
                        current.value_metrics.cost_per_year < best.value_metrics.cost_per_year ? current : best
                      ).value_metrics.cost_per_year}/year
                    </p>
                  </div>
                </div>
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

              {/* Durability Score Breakdown */}
              {selectedProduct.durability_score && (
                <div className="mb-6">
                  <DurabilityScore score={selectedProduct.durability_score} showBreakdown={true} size="md" />
                </div>
              )}

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
