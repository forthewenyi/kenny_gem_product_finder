'use client'

import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { searchProducts } from '@/lib/api'
import type { SearchResponse, Product } from '@/types'
import { useSearchWebSocket } from '@/hooks/useSearchWebSocket'

import TopBanner from '@/components/TopBanner'
import Header from '@/components/Header'
import PageTitle from '@/components/PageTitle'
import CharacteristicsSection from '@/components/CharacteristicsSection'
import FilterBar from '@/components/FilterBar'
import SearchInterface from '@/components/SearchInterface'
import ProductCard from '@/components/ProductCard'
import SearchCounter from '@/components/SearchCounter'
import SearchMetrics from '@/components/SearchMetrics'
import ProductDetailModal from '@/components/ProductDetailModal'

export default function HomePageContent() {
  const [results, setResults] = useState<SearchResponse | null>(null)
  const [compareProducts, setCompareProducts] = useState<Product[]>([])
  const [currentQuery, setCurrentQuery] = useState<string>('')
  const [currentCategory, setCurrentCategory] = useState<string>('all')
  const [selectedProductForModal, setSelectedProductForModal] = useState<Product | null>(null)

  // Filter states
  const [selectedCharacteristics, setSelectedCharacteristics] = useState<string[]>([])
  const [selectedBrands, setSelectedBrands] = useState<string[]>([])
  const [selectedTiers, setSelectedTiers] = useState<string[]>([])
  const [selectedMaterials, setSelectedMaterials] = useState<string[]>([])
  const [maxPrice, setMaxPrice] = useState<number | undefined>(undefined)
  const [maxCostPerYear, setMaxCostPerYear] = useState<number | undefined>(undefined)

  // WebSocket hook for real-time search progress
  const {
    isConnected: wsConnected,
    progressMessage,
    currentAgent,
    totalSearches,
    sendSearch: sendWebSocketSearch,
  } = useSearchWebSocket()

  // Helper function to find source URL for a review
  const findReviewSource = (reviewText: string, product: Product) => {
    if (!product.web_sources || product.web_sources.length === 0) return null

    // Common review source keywords to search for
    const sourceKeywords = [
      'Wirecutter', 'America\'s Test Kitchen', 'ATK', 'Serious Eats',
      'Cook\'s Illustrated', 'Consumer Reports', 'Good Housekeeping',
      'Food Network', 'Bon Appétit', 'Epicurious', 'The Spruce Eats',
      'CNET', 'reviewed.com', 'NY Times', 'New York Times'
    ]

    // Try to find a matching source
    for (const keyword of sourceKeywords) {
      if (reviewText.toLowerCase().includes(keyword.toLowerCase())) {
        // Find matching web source
        const source = product.web_sources.find(s =>
          s.url.toLowerCase().includes(keyword.toLowerCase().replace(/[''\s]/g, '')) ||
          s.title?.toLowerCase().includes(keyword.toLowerCase())
        )
        if (source) {
          return { name: keyword, url: source.url }
        }
      }
    }

    return null
  }

  const searchMutation = useMutation({
    mutationFn: ({ query, maxPrice, context }: { query: string; maxPrice?: number; context?: Record<string, string> }) =>
      searchProducts({
        query,
        max_price: maxPrice,
        context: context, // Pass context filters (value_preference) to search
      }),
    onSuccess: (data) => {
      setResults(data)
      setCompareProducts([])
    },
  })

  const handleSearch = (query: string, maxPriceParam?: number) => {
    setCurrentQuery(query)
    // Reset all filters on new search
    setSelectedCharacteristics([])
    setSelectedBrands([])
    setSelectedTiers([])
    setSelectedMaterials([])
    setMaxPrice(undefined)
    setMaxCostPerYear(undefined)

    // Start WebSocket for real-time progress updates
    sendWebSocketSearch(query, maxPriceParam, undefined, undefined)

    // Also call regular API for actual results
    searchMutation.mutate({ query, maxPrice: maxPriceParam })
  }

  const handleNavigate = (category: string) => {
    setCurrentCategory(category)
  }

  const handleCharacteristicClick = (characteristic: string) => {
    // Multi-select toggle for characteristic selection (used for filtering products)
    // No longer syncs with personalization filters - they are separate
    const isCurrentlySelected = selectedCharacteristics.includes(characteristic)
    setSelectedCharacteristics(prev =>
      isCurrentlySelected
        ? prev.filter(c => c !== characteristic)  // Remove if selected
        : [...prev, characteristic]                // Add if not selected
    )
  }

  const handleRemoveCharacteristic = (characteristic: string) => {
    setSelectedCharacteristics(prev => prev.filter(c => c !== characteristic))
  }

  const toggleCompare = (product: Product) => {
    if (compareProducts.find(p => p.name === product.name)) {
      setCompareProducts(compareProducts.filter(p => p.name !== product.name))
    } else if (compareProducts.length < 3) {
      const newSelection = [...compareProducts, product]
      setCompareProducts(newSelection)

      if (newSelection.length === 3) {
        setTimeout(() => {
          document.getElementById('comparison-view')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
        }, 300)
      }
    }
  }

  const clearComparison = () => {
    setCompareProducts([])
  }

  // Reorder: Good → Better → Best
  const allProducts = results
    ? [
        ...results.results.good.map(p => ({ ...p, tier: 'good' as const })),
        ...results.results.better.map(p => ({ ...p, tier: 'better' as const })),
        ...results.results.best.map(p => ({ ...p, tier: 'best' as const })),
      ]
    : []

  // Client-side filtering with all filter types
  const filteredProducts = allProducts.filter(product => {
    // Filter by characteristics
    if (selectedCharacteristics.length > 0) {
      const characteristics = product.characteristics || []
      const hasCharacteristic = selectedCharacteristics.some(selectedChar =>
        characteristics.includes(selectedChar)
      )
      if (!hasCharacteristic) return false
    }

    // Filter by brands
    if (selectedBrands.length > 0) {
      if (!selectedBrands.includes(product.brand)) return false
    }

    // Filter by tiers
    if (selectedTiers.length > 0) {
      if (!selectedTiers.includes(product.tier)) return false
    }

    // Filter by materials
    if (selectedMaterials.length > 0) {
      const materials = product.materials || []
      const hasMaterial = selectedMaterials.some(selectedMat =>
        materials.some(mat => mat.toLowerCase().includes(selectedMat.toLowerCase()))
      )
      if (!hasMaterial) return false
    }

    // Filter by max price
    if (maxPrice !== undefined) {
      if (product.value_metrics.upfront_price > maxPrice) return false
    }

    // Filter by max cost per year
    if (maxCostPerYear !== undefined) {
      if (product.value_metrics.cost_per_year > maxCostPerYear) return false
    }

    return true
  })

  // Determine Kenny's Pick
  const kennysPick = results && results.results.better.length > 0
    ? results.results.better.reduce((best, current) =>
        current.value_metrics.cost_per_year < best.value_metrics.cost_per_year ? current : best
      )
    : null

  const getSelectionNumber = (product: Product) => {
    const index = compareProducts.findIndex(p => p.name === product.name)
    return index !== -1 ? index + 1 : undefined
  }

  return (
    <main className="min-h-screen bg-white">
      {/* Top Banner */}
      <TopBanner />

      {/* Header */}
      <Header onNavigate={handleNavigate} onSearch={handleSearch} />

      {/* Page Title */}
      <PageTitle query={currentQuery} category={currentCategory} />

      {/* Search Bar with Input Filters */}
      <div className="max-w-[1400px] mx-auto px-10 pb-5">
        <SearchInterface
          onSearch={handleSearch}
          isLoading={searchMutation.isPending}
          wsConnected={wsConnected}
          progressMessage={progressMessage}
          currentAgent={currentAgent}
          totalSearches={totalSearches}
        />
      </div>

      {/* Characteristics Section - Show AI buying guidance if available */}
      {!searchMutation.isPending && results && results.buying_characteristics && results.buying_characteristics.length > 0 && (
        <CharacteristicsSection
          query={currentQuery}
          buyingCharacteristics={results.buying_characteristics}
          aggregatedCharacteristics={results.aggregated_characteristics || []}
          selectedCharacteristics={selectedCharacteristics}
          onCharacteristicClick={handleCharacteristicClick}
        />
      )}

      {/* Search Metrics */}
      {!searchMutation.isPending && results && (
        <div className="max-w-[1400px] mx-auto px-10 pb-5">
          <SearchMetrics
            query={currentQuery}
            searchQueries={results.search_queries}
            totalSourcesAnalyzed={results.total_sources_analyzed}
            queriesGenerated={results.queries_generated}
            sourcesByPhase={results.sources_by_phase}
            totalProductsResearched={allProducts.length}
            totalProductsDisplayed={filteredProducts.length}
            fromCache={false}
          />
        </div>
      )}

      <div className="container mx-auto px-4">
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
            {/* Floating Selection Notice */}
            {compareProducts.length > 0 && (
              <div className="fixed bottom-5 left-1/2 -translate-x-1/2 bg-black text-white py-4 px-6 rounded-xl shadow-2xl z-50 animate-fadeInUp">
                <div className="flex items-center gap-4">
                  <span className="text-[13px] uppercase tracking-wide font-medium">
                    {compareProducts.length} product{compareProducts.length !== 1 ? 's' : ''} selected
                  </span>
                  {compareProducts.length === 3 && (
                    <span className="text-[11px] text-gray-300">
                      • Scroll down to compare
                    </span>
                  )}
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

            {/* Result Filter Bar - Only shows when filters are active */}
            <FilterBar
              products={allProducts}
              selectedCharacteristics={selectedCharacteristics}
              onToggleCharacteristic={(char) => {
                if (selectedCharacteristics.includes(char)) {
                  setSelectedCharacteristics(selectedCharacteristics.filter(c => c !== char))
                } else {
                  setSelectedCharacteristics([...selectedCharacteristics, char])
                }
              }}
              selectedBrands={selectedBrands}
              onToggleBrand={(brand) => {
                if (selectedBrands.includes(brand)) {
                  setSelectedBrands(selectedBrands.filter(b => b !== brand))
                } else {
                  setSelectedBrands([...selectedBrands, brand])
                }
              }}
              selectedTiers={selectedTiers}
              onToggleTier={(tier) => {
                if (selectedTiers.includes(tier)) {
                  setSelectedTiers(selectedTiers.filter(t => t !== tier))
                } else {
                  setSelectedTiers([...selectedTiers, tier])
                }
              }}
              selectedMaterials={selectedMaterials}
              onToggleMaterial={(material) => {
                if (selectedMaterials.includes(material)) {
                  setSelectedMaterials(selectedMaterials.filter(m => m !== material))
                } else {
                  setSelectedMaterials([...selectedMaterials, material])
                }
              }}
              maxPrice={maxPrice}
              onMaxPriceChange={setMaxPrice}
              maxCostPerYear={maxCostPerYear}
              onMaxCostPerYearChange={setMaxCostPerYear}
              onClearAll={() => {
                setSelectedCharacteristics([])
                setSelectedBrands([])
                setSelectedTiers([])
                setSelectedMaterials([])
                setMaxPrice(undefined)
                setMaxCostPerYear(undefined)
              }}
            />

            {/* Product Grid */}
            {filteredProducts.length > 0 && (
              <div className="max-w-[1400px] mx-auto px-10 mb-16">
                <p className="text-center mb-6 text-[13px] text-[#79786c] uppercase tracking-wide">
                  👆 Click to view details • Use "Select to Compare" button for side-by-side comparison
                  {selectedCharacteristics.length > 0 && (
                    <span className="block mt-1 text-[11px]">
                      Showing {filteredProducts.length} of {allProducts.length} products
                    </span>
                  )}
                </p>

                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-[2px]">
                  {filteredProducts.map((product, idx) => (
                    <ProductCard
                      key={idx}
                      product={product}
                      onClick={() => toggleCompare(product)}
                      onViewDetails={() => setSelectedProductForModal(product)}
                      comparisonMode={true}
                      isSelected={compareProducts.some(p => p.name === product.name)}
                      selectionNumber={getSelectionNumber(product)}
                      isKennysPick={kennysPick?.name === product.name}
                      animationDelay={idx}
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

        {/* Search Counter */}
        {results && !searchMutation.isPending && allProducts.length > 0 && results.real_search_metrics && (
          <SearchCounter
            metrics={results.real_search_metrics}
            query={currentQuery && currentQuery.trim() ? currentQuery : 'kitchen products'}
          />
        )}

        {/* Comparison Section */}
        {results && !searchMutation.isPending && compareProducts.length >= 2 && (
          <div id="comparison-view" className="max-w-[1400px] mx-auto px-10 mt-20 mb-16">
            {/* Comparison Title */}
            <div className="text-center mb-12">
              <h2 className="text-4xl font-bold uppercase tracking-wide mb-3">
                Which {currentQuery || 'Product'} is<br />right for you?
              </h2>
              <p className="text-[14px] text-[#79786c]">
                Showing {compareProducts.length} product{compareProducts.length !== 1 ? 's' : ''}
              </p>
            </div>

            {/* 3-Column Product Headers - Simplified */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mb-12">
              {compareProducts.map((product, idx) => {
                const tierColors = {
                  good: 'bg-[#dbe9cc] text-[#3d5a00]',
                  better: 'bg-[#fce7b8] text-[#8b5a00]',
                  best: 'bg-[#ffe4e6] text-[#9f1239]'
                }
                const tierLabel = product.tier.charAt(0).toUpperCase() + product.tier.slice(1)
                const isKennysPick = kennysPick?.name === product.name
                const valueScore = product.quality_data?.score || 0

                // Generate star rating
                const getStars = (score: number) => {
                  const starsOutOf5 = (score / 100) * 5
                  const fullStars = Math.round(starsOutOf5)  // Round to nearest whole star
                  let stars = '★'.repeat(fullStars)
                  const emptyStars = 5 - fullStars
                  stars += '☆'.repeat(emptyStars)
                  return stars
                }

                return (
                  <div key={idx} className="relative text-center bg-[#f8f8f8] p-5">
                    <span className={`absolute top-3 left-3 text-xs px-2 py-1 uppercase tracking-wide font-semibold ${tierColors[product.tier]}`}>
                      {tierLabel}
                    </span>

                    {isKennysPick && (
                      <span className="absolute top-3 right-3 bg-black text-white px-2 py-1 text-xs uppercase tracking-wide">
                        💎 Kenny's Pick
                      </span>
                    )}

                    <h3 className="font-semibold text-[16px] uppercase tracking-wide mt-8 mb-2">
                      {product.name}
                    </h3>

                    <div className="text-xl font-bold text-gray-900 mb-2">
                      ${product.value_metrics.upfront_price}
                    </div>

                    {valueScore > 0 && (
                      <div className="flex items-center justify-center gap-2">
                        <span className="text-yellow-500 text-lg">{getStars(valueScore)}</span>
                        <span className="text-sm font-medium text-gray-600">Value: {(valueScore / 10).toFixed(1)}</span>
                      </div>
                    )}
                  </div>
                )
              })}
            </div>

            {/* Comparison Rows - VALUE Framework Order */}
            {/* Updated Nov 5: Reorganized to PRODUCT → SERVICE → EQUITY → PRICE & ACTION */}
            {/* Single column containers with internal dividers for cleaner layout */}
            <div className="mt-12 bg-white space-y-6">
              {/* 1. PRODUCT */}
              <div className="border-t pt-6">
                <h3 className="text-xs uppercase tracking-wide text-gray-500 mb-4 font-semibold">PRODUCT</h3>

                <div className="grid grid-cols-3 gap-4">
                  {compareProducts.map((product, idx) => (
                    <div key={idx} className="bg-[#f8f8f8] p-4">
                      {/* Brand */}
                      <div className="pb-3 border-b border-gray-200">
                        <div className="text-xs text-gray-500 uppercase mb-1 font-semibold">Brand:</div>
                        <div className="text-sm font-medium text-gray-900">
                          {product.brand || 'Unknown Brand'}
                        </div>
                      </div>

                      {/* Materials */}
                      <div className="py-3 border-b border-gray-200">
                        <div className="text-xs text-gray-500 uppercase mb-1 font-semibold">Materials:</div>
                        <div className="space-y-1">
                          {product.materials && product.materials.length > 0 ? (
                            product.materials.map((mat, matIdx) => (
                              <div key={matIdx} className="text-xs text-gray-700 leading-relaxed">• {mat}</div>
                            ))
                          ) : (
                            <div className="text-xs text-gray-400">Not specified</div>
                          )}
                        </div>
                      </div>

                      {/* Key Features */}
                      <div className="py-3 border-b border-gray-200">
                        <div className="text-xs text-gray-500 uppercase mb-1 font-semibold">Key Features:</div>
                        <div className="space-y-1">
                          {product.key_features && product.key_features.length > 0 ? (
                            (Array.isArray(product.key_features) ? product.key_features : [product.key_features]).slice(0, 3).map((feature, fIdx) => (
                              <div key={fIdx} className="text-xs text-gray-700 leading-relaxed">• {feature}</div>
                            ))
                          ) : (
                            <div className="text-xs text-gray-400">Not specified</div>
                          )}
                        </div>
                      </div>

                      {/* Why It's a Gem */}
                      <div className="py-3 border-b border-gray-200">
                        <div className="text-xs text-gray-500 uppercase mb-1 font-semibold">Why It's a Gem:</div>
                        <div className="text-xs text-gray-700 leading-relaxed">
                          {product.why_its_a_gem || 'High-quality, value-focused option'}
                        </div>
                      </div>

                      {/* What Sets It Apart */}
                      <div className={product.key_differentiator ? "py-3 bg-blue-50 -mx-4 px-4 border-y border-blue-200" : "py-3"}>
                        {product.key_differentiator ? (
                          <>
                            <div className="text-xs text-blue-900 uppercase mb-1 font-semibold flex items-center gap-1">
                              <span>⭐</span>
                              What Sets It Apart:
                            </div>
                            <div className="text-xs text-gray-800 leading-relaxed">
                              {product.key_differentiator}
                            </div>
                          </>
                        ) : (
                          <>
                            <div className="text-xs text-gray-500 uppercase mb-1 font-semibold flex items-center gap-1">
                              <span>⭐</span>
                              What Sets It Apart:
                            </div>
                            <div className="text-xs text-gray-400">Not specified</div>
                          </>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* 2. SERVICE */}
              <div className="border-t pt-6">
                <h3 className="text-xs uppercase tracking-wide text-gray-500 mb-4 font-semibold">SERVICE</h3>

                <div className="grid grid-cols-3 gap-4">
                  {compareProducts.map((product, idx) => (
                    <div key={idx} className="bg-[#f8f8f8] p-4">
                      {/* Learning Curve */}
                      <div className="pb-3 border-b border-gray-200">
                        <div className="flex items-center justify-between mb-1">
                          <div className="text-xs font-semibold text-gray-700">📚 Learning Curve</div>
                          <div className="text-xs font-bold text-gray-900">
                            {product.practical_metrics?.learning_curve || 'Medium'}
                          </div>
                        </div>
                        <div className="text-xs text-gray-600 leading-relaxed">
                          {product.practical_metrics?.learning_details || 'Easy to start using right away'}
                        </div>
                      </div>

                      {/* Maintenance */}
                      <div className="py-3 border-b border-gray-200">
                        <div className="flex items-center justify-between mb-1">
                          <div className="text-xs font-semibold text-gray-700">🔧 Maintenance</div>
                          <div className="text-xs font-bold text-gray-900">
                            {product.practical_metrics?.maintenance_level || product.maintenance_level || 'Medium'}
                          </div>
                        </div>
                        <div className="text-xs text-gray-600 leading-relaxed">
                          {product.practical_metrics?.maintenance_details || 'Regular care required to maintain performance'}
                        </div>
                      </div>

                      {/* Honest Drawbacks */}
                      <div className="py-3">
                        <div className="text-xs text-gray-500 uppercase mb-1 font-semibold">⚠ Honest Drawbacks:</div>
                        <div className="space-y-1">
                          {(product.drawbacks && product.drawbacks.length > 0) ? (
                            product.drawbacks.map((item, dIdx) => (
                              <div key={dIdx} className="text-xs text-gray-600 leading-relaxed">• {item}</div>
                            ))
                          ) : (
                            <div className="text-xs text-gray-400">None identified</div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* 3. EQUITY */}
              <div className="border-t pt-6">
                <h3 className="text-xs uppercase tracking-wide text-gray-500 mb-4 font-semibold">EQUITY</h3>

                <div className="grid grid-cols-3 gap-4">
                  {compareProducts.map((product, idx) => (
                    <div key={idx} className="bg-[#f8f8f8] p-4">
                      {/* Professional Reviews */}
                      <div className="pb-3 border-b border-gray-200">
                        <div className="text-xs text-gray-500 uppercase mb-2 font-semibold">Professional Reviews:</div>
                        <div className="space-y-2">
                          {product.professional_reviews && product.professional_reviews.length > 0 ? (
                            product.professional_reviews.slice(0, 3).map((review, rIdx) => {
                              const source = findReviewSource(review, product)
                              return (
                                <div key={rIdx} className="border-l-4 border-blue-500 pl-3 py-2">
                                  <div className="text-xs text-gray-700 leading-relaxed">{review}</div>
                                  {source && (
                                    <a
                                      href={source.url}
                                      target="_blank"
                                      rel="noopener noreferrer"
                                      className="text-xs text-blue-600 hover:text-blue-800 hover:underline mt-1 inline-block"
                                    >
                                      Source: {source.name} →
                                    </a>
                                  )}
                                </div>
                              )
                            })
                          ) : (
                            <div className="text-xs text-gray-400">No reviews available</div>
                          )}
                        </div>
                      </div>

                      {/* Best For */}
                      <div className="py-3">
                        <div className="text-xs text-gray-500 uppercase mb-1 font-semibold">✓ Best For:</div>
                        <p className="text-xs text-gray-700 leading-relaxed">
                          {product.best_for || 'Not specified'}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* 4. PRICE */}
              <div className="border-t pt-6 pb-6">
                <h3 className="text-xs uppercase tracking-wide text-gray-500 mb-4 font-semibold">PRICE</h3>

                <div className="grid grid-cols-3 gap-4">
                  {compareProducts.map((product, idx) => (
                    <div key={idx} className="bg-[#f8f8f8] p-4">
                      {/* Value Breakdown */}
                      <div className="pb-3 border-b border-gray-200">
                        <div className="text-xs text-gray-500 uppercase mb-2 font-semibold">Value Breakdown:</div>
                        {product.value_metrics && (
                          <div className="space-y-2">
                            {product.quality_data?.score && (
                              <div className="flex justify-between">
                                <span className="text-xs text-gray-500">Value Score:</span>
                                <span className="font-bold text-gray-900 text-base">{(product.quality_data.score / 10).toFixed(1)}/10</span>
                              </div>
                            )}
                            <div className="flex justify-between">
                              <span className="text-xs text-gray-500">Retail Price:</span>
                              <span className="font-bold text-gray-900 text-base">${product.value_metrics.upfront_price}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-xs text-gray-500">Expected Lifespan:</span>
                              <span className="font-medium text-gray-700">{product.value_metrics.expected_lifespan_years}+ years</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-xs text-gray-500">Cost per Year:</span>
                              <span className="font-medium text-green-600">${product.value_metrics.cost_per_year.toFixed(2)}</span>
                            </div>
                          </div>
                        )}
                      </div>

                      {/* Purchase Links */}
                      <div className="py-3">
                        <div className="text-xs text-gray-500 uppercase mb-2 font-semibold">Where to Buy:</div>
                        {product.purchase_links && product.purchase_links.length > 0 ? (
                          <a
                            href={product.purchase_links[0].url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="block w-full py-2 px-4 bg-black text-white text-center text-sm font-medium rounded-lg hover:bg-gray-800 transition-colors"
                          >
                            Buy Now
                          </a>
                        ) : (
                          <div className="text-xs text-gray-400 text-center p-3 border-2 border-dashed border-gray-200 rounded-lg">
                            No purchase link
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
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
        )}
      </div>

      {/* Product Detail Modal */}
      {selectedProductForModal && (
        <ProductDetailModal
          product={selectedProductForModal}
          onClose={() => setSelectedProductForModal(null)}
        />
      )}
    </main>
  )
}
