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

export default function HomePageContent() {
  const [results, setResults] = useState<SearchResponse | null>(null)
  const [compareProducts, setCompareProducts] = useState<Product[]>([])
  const [currentQuery, setCurrentQuery] = useState<string>('')
  const [currentCategory, setCurrentCategory] = useState<string>('all')

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
    // Simple toggle for characteristic selection (used for filtering products)
    // No longer syncs with personalization filters - they are separate
    const isCurrentlySelected = selectedCharacteristics.includes(characteristic)
    setSelectedCharacteristics(prev =>
      isCurrentlySelected ? [] : [characteristic]
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

      {/* Characteristics Section */}
      {!searchMutation.isPending && results && results.aggregated_characteristics && results.aggregated_characteristics.length > 0 && (
        <CharacteristicsSection
          query={currentQuery}
          aggregatedCharacteristics={results.aggregated_characteristics}
          selectedCharacteristics={selectedCharacteristics}
          onCharacteristicClick={handleCharacteristicClick}
        />
      )}

      {/* Search Metrics */}
      {!searchMutation.isPending && results && (
        <div className="max-w-[1400px] mx-auto px-10 pb-5">
          <SearchMetrics
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
                  👆 Click to select up to 3 products to compare
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

            {/* 3-Column Product Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mb-12">
              {compareProducts.map((product, idx) => {
                const tierColors = {
                  good: 'bg-[#dbe9cc] text-[#3d5a00]',
                  better: 'bg-[#fce7b8] text-[#8b5a00]',
                  best: 'bg-[#ffe4e6] text-[#9f1239]'
                }
                const tierLabel = product.tier.charAt(0).toUpperCase() + product.tier.slice(1)
                const isKennysPick = kennysPick?.name === product.name

                return (
                  <div key={idx} className="relative text-center bg-[#f8f8f8] p-5">
                    <span className={`absolute top-3 left-3 text-[9px] px-2 py-1 uppercase tracking-wide font-semibold ${tierColors[product.tier]}`}>
                      {tierLabel}
                    </span>

                    {isKennysPick && (
                      <span className="absolute top-3 right-3 bg-black text-white px-2 py-1 text-[10px] uppercase tracking-wide">
                        💎 Kenny's Pick
                      </span>
                    )}

                    <h3 className="font-semibold text-[16px] uppercase tracking-wide mt-8 mb-2">
                      {product.name}
                    </h3>

                    <p className="text-[12px] text-[#79786c] mb-5 min-h-[40px]">
                      {product.why_its_a_gem || product.best_for || 'High-quality option'}
                    </p>

                    <p className="text-[20px] font-bold mb-2">
                      ${product.value_metrics.upfront_price}
                    </p>

                    <p className="text-[11px] text-[#79786c] mb-5">
                      ${product.value_metrics.cost_per_year}/year • {product.value_metrics.expected_lifespan_years}+ year lifespan
                    </p>
                  </div>
                )
              })}
            </div>

            {/* Comparison Rows */}
            <div className="mt-12 bg-white space-y-6">
              {/* Characteristics Comparison */}
              <div className="border-t pt-6">
                <h3 className="text-xs uppercase tracking-wide text-gray-500 mb-4 font-semibold">Key Characteristics</h3>
                <div className="grid grid-cols-3 gap-4">
                  {compareProducts.map((product, idx) => (
                    <div key={idx} className="space-y-1">
                      {product.characteristics && product.characteristics.length > 0 ? (
                        product.characteristics.slice(0, 5).map((char, charIdx) => (
                          <div key={charIdx} className="text-xs text-gray-700">
                            • {char}
                          </div>
                        ))
                      ) : (
                        <p className="text-xs text-gray-400">No characteristics listed</p>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Materials Comparison */}
              <div className="border-t pt-6">
                <h3 className="text-xs uppercase tracking-wide text-gray-500 mb-4 font-semibold">Materials</h3>
                <div className="grid grid-cols-3 gap-4">
                  {compareProducts.map((product, idx) => (
                    <div key={idx}>
                      {product.materials && product.materials.length > 0 ? (
                        <div className="space-y-1">
                          {product.materials.map((mat, matIdx) => (
                            <div key={matIdx} className="text-xs text-gray-700">• {mat}</div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-xs text-gray-400">Not specified</p>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Durability Score Comparison */}
              <div className="border-t pt-6">
                <h3 className="text-xs uppercase tracking-wide text-gray-500 mb-4 font-semibold">Durability</h3>
                <div className="grid grid-cols-3 gap-4">
                  {compareProducts.map((product, idx) => (
                    <div key={idx}>
                      {product.durability_data ? (
                        <div className="space-y-3">
                          {/* Main Score */}
                          <div className="text-center pb-3 border-b">
                            <div className="text-3xl font-bold mb-1">
                              {product.durability_data.score}/100
                            </div>
                            <div className="text-xs text-gray-500">
                              {product.durability_data.score >= 90 ? 'Excellent' :
                               product.durability_data.score >= 80 ? 'Very Good' :
                               product.durability_data.score >= 70 ? 'Good' : 'Fair'}
                            </div>
                          </div>

                          {/* Key Metrics */}
                          <div className="space-y-2 text-xs">
                            <div className="flex justify-between">
                              <span className="text-gray-500">Avg Lifespan:</span>
                              <span className="font-medium">{product.durability_data.average_lifespan_years} years</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-500">Working after 5y:</span>
                              <span className="font-medium">{product.durability_data.still_working_after_5years_percent}%</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-500">User Reports:</span>
                              <span className="font-medium">{product.durability_data.total_user_reports}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-500">Repairability:</span>
                              <span className="font-medium">{product.durability_data.repairability_score}/100</span>
                            </div>
                          </div>

                          {/* Material Quality Indicators */}
                          {product.durability_data.material_quality_indicators &&
                           product.durability_data.material_quality_indicators.length > 0 && (
                            <div className="pt-2 border-t">
                              <div className="text-xs text-gray-500 mb-1">Quality:</div>
                              {product.durability_data.material_quality_indicators.map((indicator, i) => (
                                <div key={i} className="text-xs">• {indicator}</div>
                              ))}
                            </div>
                          )}

                          {/* Common Failure Points */}
                          {product.durability_data.common_failure_points &&
                           product.durability_data.common_failure_points.length > 0 && (
                            <div className="pt-2 border-t">
                              <div className="text-xs text-gray-500 mb-1">Failure Points:</div>
                              {product.durability_data.common_failure_points.map((point, i) => (
                                <div key={i} className="text-xs text-red-600">• {point}</div>
                              ))}
                            </div>
                          )}
                        </div>
                      ) : (
                        <p className="text-xs text-gray-400">No durability data</p>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Best For Comparison */}
              <div className="border-t pt-6">
                <h3 className="text-xs uppercase tracking-wide text-gray-500 mb-4 font-semibold">Best For</h3>
                <div className="grid grid-cols-3 gap-4">
                  {compareProducts.map((product, idx) => (
                    <div key={idx}>
                      <p className="text-xs text-gray-700">{product.best_for || 'General use'}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Trade-offs Comparison */}
              <div className="border-t pt-6">
                <h3 className="text-xs uppercase tracking-wide text-gray-500 mb-4 font-semibold">Trade-offs</h3>
                <div className="grid grid-cols-3 gap-4">
                  {compareProducts.map((product, idx) => (
                    <div key={idx}>
                      {product.trade_offs && product.trade_offs.length > 0 ? (
                        <div className="space-y-1">
                          {(Array.isArray(product.trade_offs) ? product.trade_offs : [product.trade_offs]).map((tradeoff, tIdx) => (
                            <div key={tIdx} className="text-xs text-gray-600">• {tradeoff}</div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-xs text-gray-400">None noted</p>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Hassles of Ownership */}
              <div className="border-t pt-6">
                <h3 className="text-xs uppercase tracking-wide text-gray-500 mb-4 font-semibold">Daily Hassles</h3>
                <div className="grid grid-cols-3 gap-4">
                  {compareProducts.map((product, idx) => (
                    <div key={idx}>
                      {product.practical_metrics ? (
                        <div className="space-y-3">
                          {/* Cleaning */}
                          <div>
                            <div className="flex items-center justify-between mb-1">
                              <div className="text-xs font-semibold text-gray-700">🧼 Cleaning</div>
                              <div className="text-xs font-bold text-gray-900">
                                {product.practical_metrics.cleaning_time_minutes
                                  ? `${product.practical_metrics.cleaning_time_minutes} min`
                                  : 'Standard'}
                              </div>
                            </div>
                            <div className="text-xs text-gray-600 leading-relaxed">
                              {product.practical_metrics.cleaning_details || 'Hand wash with warm water, scrub gently, dry immediately'}
                            </div>
                          </div>

                          {/* Setup */}
                          <div>
                            <div className="flex items-center justify-between mb-1">
                              <div className="text-xs font-semibold text-gray-700">⚙️ Setup</div>
                              <div className="text-xs font-bold text-gray-900">
                                {product.practical_metrics.setup_time || 'N/A'}
                              </div>
                            </div>
                            <div className="text-xs text-gray-600 leading-relaxed">
                              {product.practical_metrics.setup_details || 'No special setup required'}
                            </div>
                          </div>

                          {/* Learning Curve */}
                          <div>
                            <div className="flex items-center justify-between mb-1">
                              <div className="text-xs font-semibold text-gray-700">📚 Learning Curve</div>
                              <div className="text-xs font-bold text-gray-900">
                                {product.practical_metrics.learning_curve || 'N/A'}
                              </div>
                            </div>
                            <div className="text-xs text-gray-600 leading-relaxed">
                              {product.practical_metrics.learning_details || 'Easy to start using right away'}
                            </div>
                          </div>

                          {/* Maintenance */}
                          <div>
                            <div className="flex items-center justify-between mb-1">
                              <div className="text-xs font-semibold text-gray-700">🔧 Maintenance</div>
                              <div className="text-xs font-bold text-gray-900">
                                {product.practical_metrics.maintenance_level || product.maintenance_level || 'N/A'}
                              </div>
                            </div>
                            <div className="text-xs text-gray-600 leading-relaxed">
                              {product.practical_metrics.maintenance_details ||
                               (product.maintenance_level && product.maintenance_level.toLowerCase().includes('moderate')
                                 ? 'Hand wash, dry immediately, apply light oil coating after each use'
                                 : 'Regular care required to maintain performance')}
                            </div>
                          </div>
                        </div>
                      ) : (
                        <p className="text-xs text-gray-400">No practical data available</p>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Lifespan Comparison */}
              <div className="border-t pt-6">
                <h3 className="text-xs uppercase tracking-wide text-gray-500 mb-4 font-semibold">Expected Lifespan</h3>
                <div className="grid grid-cols-3 gap-4">
                  {compareProducts.map((product, idx) => (
                    <div key={idx} className="text-center">
                      <div className="text-2xl font-bold text-gray-900 mb-1">
                        {product.value_metrics?.expected_lifespan_years
                          ? `${product.value_metrics.expected_lifespan_years} years`
                          : 'N/A'}
                      </div>
                      {product.durability_data && product.durability_data.total_user_reports > 0 && (
                        <div className="text-[10px] text-gray-500">
                          Based on {product.durability_data.total_user_reports} user reports
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Value Analysis */}
              <div className="border-t pt-6">
                <h3 className="text-xs uppercase tracking-wide text-gray-500 mb-4 font-semibold">Value Analysis</h3>
                <div className="grid grid-cols-3 gap-4">
                  {compareProducts.map((product, idx) => (
                    <div key={idx}>
                      <div className="space-y-3">
                        <div className="flex justify-between text-xs">
                          <span className="text-gray-500">Price:</span>
                          <span className="font-bold text-gray-900">${product.value_metrics?.upfront_price || 'N/A'}</span>
                        </div>
                        {product.value_metrics && (
                          <>
                            <div className="flex justify-between text-xs">
                              <span className="text-gray-500">Cost/year:</span>
                              <span className="font-medium text-green-600">${product.value_metrics.cost_per_year.toFixed(2)}</span>
                            </div>
                            <div className="flex justify-between text-xs">
                              <span className="text-gray-500">Cost/day:</span>
                              <span className="font-medium text-gray-600">${product.value_metrics.cost_per_day.toFixed(2)}</span>
                            </div>
                          </>
                        )}
                        <div className="pt-2 border-t">
                          <div className="text-xs text-gray-700 leading-relaxed">
                            {product.why_its_a_gem}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* What Makes It Unique */}
              <div className="border-t pt-6">
                <h3 className="text-xs uppercase tracking-wide text-gray-500 mb-4 font-semibold">What Makes It Unique</h3>
                <div className="grid grid-cols-3 gap-4">
                  {compareProducts.map((product, idx) => {
                    // Generate unique differentiators by comparing to other products
                    const otherProducts = compareProducts.filter((_, i) => i !== idx);
                    const uniqueChars = product.characteristics?.filter(char =>
                      !otherProducts.some(other => other.characteristics?.includes(char))
                    ) || [];

                    return (
                      <div key={idx}>
                        {uniqueChars.length > 0 ? (
                          <div className="space-y-1">
                            {uniqueChars.slice(0, 5).map((char, i) => (
                              <div key={i} className="text-xs text-gray-700">• {char}</div>
                            ))}
                          </div>
                        ) : (
                          <div className="text-xs text-gray-400">
                            Shares characteristics with other options
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* What People Are Saying - Grid Row */}
              <div className="border-t pt-6">
                <h3 className="text-xs uppercase tracking-wide text-gray-500 mb-4 font-semibold">What People Are Saying</h3>
                <div className="grid grid-cols-3 gap-4">
                  {compareProducts.map((product, idx) => {
                    // Generate review summaries from product data
                    const reviewSummaries = [
                      {
                        type: 'Why It\'s Great',
                        content: product.why_its_a_gem,
                        icon: '💎'
                      },
                      {
                        type: 'Key Features',
                        content: Array.isArray(product.key_features)
                          ? product.key_features[0]
                          : product.key_features,
                        icon: '✨'
                      },
                      {
                        type: 'Best For',
                        content: product.best_for,
                        icon: '👥'
                      }
                    ].filter(item => item.content);

                    return (
                      <details key={idx} className="group">
                        <summary className="cursor-pointer list-none">
                          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                            <span className="text-xs font-medium">Read reviews summary</span>
                            <svg className="w-4 h-4 text-gray-400 group-open:rotate-180 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                            </svg>
                          </div>
                        </summary>

                        <div className="mt-4 space-y-3">
                          {reviewSummaries.map((review, reviewIdx) => (
                            <div key={reviewIdx} className="p-3 bg-gray-50 rounded-lg">
                              <div className="flex items-start gap-2">
                                <div className="flex-shrink-0 text-lg">
                                  {review.icon}
                                </div>
                                <div className="flex-1">
                                  <div className="text-[10px] font-semibold text-gray-500 uppercase mb-1">
                                    {review.type}
                                  </div>
                                  <div className="text-xs text-gray-700 leading-relaxed">
                                    "{review.content}"
                                  </div>
                                </div>
                              </div>
                            </div>
                          ))}

                          {/* Sources Citation */}
                          <div className="pt-3 mt-3 border-t border-gray-200">
                            <div className="text-[10px] text-gray-500 mb-2 font-semibold">
                              Sources analyzed:
                            </div>
                            <div className="space-y-1">
                              {/* Prioritize durability data sources, fall back to web sources */}
                              {(product.durability_data?.data_sources && product.durability_data.data_sources.length > 0
                                ? product.durability_data.data_sources
                                : product.web_sources || []
                              ).slice(0, 3).map((source, i) => {
                                try {
                                  const url = typeof source === 'string' ? source : source.url;
                                  const hostname = new URL(url).hostname.replace('www.', '');
                                  return (
                                    <div key={i} className="text-[10px] text-blue-600">
                                      <a href={url} target="_blank" rel="noopener noreferrer" className="hover:underline">
                                        • {hostname}
                                      </a>
                                    </div>
                                  );
                                } catch (e) {
                                  const displaySource = typeof source === 'string' ? source : source.url || 'Unknown source';
                                  return (
                                    <div key={i} className="text-[10px] text-gray-500">
                                      • {displaySource}
                                    </div>
                                  );
                                }
                              })}
                            </div>
                          </div>
                        </div>
                      </details>
                    );
                  })}
                </div>
              </div>

              {/* Buy - Grid Row */}
              <div className="border-t pt-6 pb-6 overflow-visible">
                <h3 className="text-xs uppercase tracking-wide text-gray-500 mb-4 font-semibold">Buy</h3>
                <div className="grid grid-cols-3 gap-4 overflow-visible">
                  {compareProducts.map((product, idx) => {
                    const getDestination = () => {
                      if (product.purchase_links && product.purchase_links.length > 0) {
                        try {
                          return new URL(product.purchase_links[0].url).hostname.replace('www.', '');
                        } catch {
                          return product.brand;
                        }
                      } else if (product.web_sources && product.web_sources.length > 0) {
                        try {
                          const url = typeof product.web_sources[0] === 'string' ? product.web_sources[0] : product.web_sources[0].url;
                          return new URL(url).hostname.replace('www.', '');
                        } catch {
                          return 'Website';
                        }
                      }
                      return null;
                    };

                    const destination = getDestination();
                    const buyUrl = product.purchase_links && product.purchase_links.length > 0
                      ? product.purchase_links[0].url
                      : product.web_sources && product.web_sources.length > 0
                        ? (typeof product.web_sources[0] === 'string' ? product.web_sources[0] : product.web_sources[0].url)
                        : null;

                    return (
                      <div key={idx} className="relative overflow-visible">
                        {buyUrl ? (
                          <div className="overflow-visible">
                            <a
                              href={buyUrl}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="peer group relative block w-full py-3 px-4 bg-black text-white text-center text-sm font-medium rounded-lg hover:bg-gray-800 transition-colors"
                            >
                              Buy
                            </a>
                            {/* Tooltip - shows on hover */}
                            {destination && (
                              <div className="invisible peer-hover:visible absolute -top-10 left-1/2 -translate-x-1/2 bg-gray-900 text-white text-xs px-3 py-1.5 rounded shadow-lg whitespace-nowrap z-[100]">
                                {destination}
                                {/* Arrow */}
                                <div className="absolute top-full left-1/2 -translate-x-1/2 -mt-px w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900"></div>
                              </div>
                            )}
                          </div>
                        ) : (
                          <div className="text-xs text-gray-400 text-center p-4 border-2 border-dashed border-gray-200 rounded-lg">
                            No purchase link
                          </div>
                        )}
                      </div>
                    );
                  })}
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
    </main>
  )
}
