'use client'

import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { searchProducts } from '@/lib/api'
import type { SearchResponse, Product } from '@/types'

import TopBanner from '@/components/TopBanner'
import Header from '@/components/Header'
import PageTitle from '@/components/PageTitle'
import CharacteristicsSection from '@/components/CharacteristicsSection'
import FilterBar from '@/components/FilterBar'
import FilterOptions from '@/components/FilterOptions'
import SearchInterface from '@/components/SearchInterface'
import ProductCard from '@/components/ProductCard'
import SearchCounter from '@/components/SearchCounter'
import TierBadge from '@/components/TierBadge'
import DurabilityScore from '@/components/DurabilityScore'
import SearchMetrics from '@/components/SearchMetrics'

export default function Home() {
  const [results, setResults] = useState<SearchResponse | null>(null)
  const [compareProducts, setCompareProducts] = useState<Product[]>([])
  const [currentQuery, setCurrentQuery] = useState<string>('')
  const [currentCategory, setCurrentCategory] = useState<string>('all')
  const [selectedCharacteristics, setSelectedCharacteristics] = useState<string[]>([])
  const [selectedMaterials, setSelectedMaterials] = useState<string[]>([])
  const [selectedTier, setSelectedTier] = useState<string | undefined>(undefined)

  const searchMutation = useMutation({
    mutationFn: ({ query, maxPrice }: { query: string; maxPrice?: number }) =>
      searchProducts({ query, max_price: maxPrice }),
    onSuccess: (data) => {
      setResults(data)
      setCompareProducts([])
    },
  })

  const handleSearch = (query: string, maxPrice?: number) => {
    setCurrentQuery(query)
    // Reset all filters on new search
    setSelectedCharacteristics([])
    setSelectedMaterials([])
    setSelectedTier(undefined)
    searchMutation.mutate({ query, maxPrice })
  }

  const handleNavigate = (category: string) => {
    setCurrentCategory(category)
    // Don't trigger automatic search - let users select from dropdown
  }

  const handleCharacteristicClick = (characteristic: string) => {
    // Toggle the characteristic - only one active at a time for now
    setSelectedCharacteristics(prev =>
      prev.includes(characteristic) ? [] : [characteristic]
    )
  }

  const handleRemoveCharacteristic = (characteristic: string) => {
    setSelectedCharacteristics(prev => prev.filter(c => c !== characteristic))
  }

  const handleRemoveMaterial = (material: string) => {
    setSelectedMaterials(prev => prev.filter(m => m !== material))
  }

  const handleRemoveTier = () => {
    setSelectedTier(undefined)
  }

  const handleMaterialClick = (material: string) => {
    setSelectedMaterials(prev =>
      prev.includes(material) ? prev.filter(m => m !== material) : [...prev, material]
    )
  }

  const handleTierClick = (tier: string) => {
    setSelectedTier(prev => prev === tier ? undefined : tier)
  }

  const toggleCompare = (product: Product) => {
    if (compareProducts.find(p => p.name === product.name)) {
      setCompareProducts(compareProducts.filter(p => p.name !== product.name))
    } else if (compareProducts.length < 3) {
      const newSelection = [...compareProducts, product]
      setCompareProducts(newSelection)

      // Auto-scroll to comparison when 3 products selected
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

  // Reorder: Good → Better → Best (matching HTML mockup)
  const allProducts = results
    ? [
        ...results.results.good.map(p => ({ ...p, tier: 'good' as const })),
        ...results.results.better.map(p => ({ ...p, tier: 'better' as const })),
        ...results.results.best.map(p => ({ ...p, tier: 'best' as const })),
      ]
    : []

  // Client-side filtering based on multiple filter types
  // Combines characteristics, materials, and tier filters
  const filteredProducts = allProducts.filter(product => {
    // Filter by characteristics
    if (selectedCharacteristics.length > 0) {
      const characteristics = product.characteristics || []
      const hasCharacteristic = selectedCharacteristics.some(selectedChar =>
        characteristics.includes(selectedChar)
      )
      if (!hasCharacteristic) return false
    }

    // Filter by materials
    if (selectedMaterials.length > 0) {
      const materials = product.materials || []
      const hasMaterial = selectedMaterials.some(selectedMat =>
        materials.some(mat => mat.toLowerCase().includes(selectedMat.toLowerCase()))
      )
      if (!hasMaterial) return false
    }

    // Filter by tier
    if (selectedTier) {
      if (product.tier !== selectedTier.toLowerCase()) return false
    }

    return true
  })

  // Determine Kenny's Pick (best cost-per-year in Better tier)
  const kennysPick = results && results.results.better.length > 0
    ? results.results.better.reduce((best, current) =>
        current.value_metrics.cost_per_year < best.value_metrics.cost_per_year ? current : best
      )
    : null

  // Get selection number for a product (1, 2, or 3)
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

      {/* Search Bar - positioned directly after page title */}
      <div className="max-w-[1400px] mx-auto px-10 pb-5">
        <SearchInterface
          onSearch={handleSearch}
          isLoading={searchMutation.isPending}
        />
      </div>

      {/* Characteristics Section - Shows Real Product Characteristics */}
      {!searchMutation.isPending && results && results.aggregated_characteristics && results.aggregated_characteristics.length > 0 && (
        <CharacteristicsSection
          query={currentQuery}
          aggregatedCharacteristics={results.aggregated_characteristics}
          selectedCharacteristics={selectedCharacteristics}
          onCharacteristicClick={handleCharacteristicClick}
        />
      )}

      {/* Filter Bar - Always Visible */}
      {!searchMutation.isPending && results && (
        <FilterBar
          selectedCharacteristics={selectedCharacteristics}
          onRemoveCharacteristic={handleRemoveCharacteristic}
          selectedMaterials={selectedMaterials}
          onRemoveMaterial={handleRemoveMaterial}
          selectedTier={selectedTier}
          onRemoveTier={handleRemoveTier}
        />
      )}

      {/* Filter Options - Material & Tier Selection */}
      {!searchMutation.isPending && results && allProducts.length > 0 && (
        <FilterOptions
          products={allProducts}
          selectedMaterials={selectedMaterials}
          selectedTier={selectedTier}
          onMaterialClick={handleMaterialClick}
          onTierClick={handleTierClick}
        />
      )}

      {/* Search Metrics - Show what Kenny searched */}
      {!searchMutation.isPending && results && (
        <div className="max-w-[1400px] mx-auto px-10 pb-5">
          <SearchMetrics
            searchQueries={results.search_queries}
            totalSourcesAnalyzed={results.total_sources_analyzed}
            queriesGenerated={results.queries_generated}
            sourcesByPhase={results.sources_by_phase}
          />
        </div>
      )}

      <div className="container mx-auto px-4"  >

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
            {/* Floating Selection Notice - Bottom (Apple Style) */}
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

            {/* Product Grid - Filtered Products */}
            {filteredProducts.length > 0 && (
              <div className="max-w-[1400px] mx-auto px-10 mb-16">
                {/* Grid Instruction */}
                <p className="text-center mb-6 text-[13px] text-[#79786c] uppercase tracking-wide">
                  👆 Click to select up to 3 products to compare
                  {selectedCharacteristics.length > 0 && (
                    <span className="block mt-1 text-[11px]">
                      Showing {filteredProducts.length} of {allProducts.length} products
                    </span>
                  )}
                </p>

                {/* Product Grid - Matches HTML Mockup */}
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

        {/* Search Counter - shows real search metrics */}
        {results && !searchMutation.isPending && allProducts.length > 0 && results.real_search_metrics && (
          <SearchCounter
            metrics={results.real_search_metrics}
            query={currentQuery && currentQuery.trim() ? currentQuery : 'kitchen products'}
          />
        )}

        {/* Results container continued */}
        {results && !searchMutation.isPending && (
          <div className="mt-12">
            {/* Apple-Style Comparison Section */}
            {compareProducts.length >= 2 && (
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
                        {/* Tier Label */}
                        <span className={`absolute top-3 left-3 text-[9px] px-2 py-1 uppercase tracking-wide font-semibold ${tierColors[product.tier]}`}>
                          {tierLabel}
                        </span>

                        {/* Kenny's Pick Badge */}
                        {isKennysPick && (
                          <span className="absolute top-3 right-3 bg-black text-white px-2 py-1 text-[10px] uppercase tracking-wide">
                            💎 Kenny's Pick
                          </span>
                        )}

                        {/* Product Name */}
                        <h3 className="font-semibold text-[16px] uppercase tracking-wide mt-8 mb-2">
                          {product.name}
                        </h3>

                        {/* Description */}
                        <p className="text-[12px] text-[#79786c] mb-5 min-h-[40px]">
                          {product.why_its_a_gem || product.best_for || 'High-quality option'}
                        </p>

                        {/* Price */}
                        <p className="text-[20px] font-bold mb-2">
                          ${product.value_metrics.upfront_price}
                        </p>

                        {/* Cost per year */}
                        <p className="text-[11px] text-[#79786c] mb-5">
                          ${product.value_metrics.cost_per_year}/year • {product.value_metrics.expected_lifespan_years}+ year lifespan
                        </p>
                      </div>
                    )
                  })}
                </div>

                {/* Comparison Rows - Apple Style */}
                <div className="mt-12 bg-white">
                  {/* Cleaning Time Row */}
                  <div className="grid grid-cols-1 md:grid-cols-4 border-b border-[#e5e5e5] py-5">
                    <div className="px-5 flex items-center">
                      <div className="text-[13px] font-semibold uppercase tracking-wide">🧼 Cleaning Time</div>
                    </div>
                    {compareProducts.map((product, idx) => (
                      <div key={idx} className="px-5 py-3 text-center">
                        {product.practical_metrics?.cleaning_time_minutes ? (
                          <>
                            <div className="text-[20px] font-bold mb-1">
                              {product.practical_metrics.cleaning_time_minutes} min
                            </div>
                            {product.practical_metrics.cleaning_details && (
                              <div className="text-[11px] text-[#79786c]">
                                {product.practical_metrics.cleaning_details}
                              </div>
                            )}
                          </>
                        ) : (
                          <div className="text-[13px] text-[#79786c]">Not specified</div>
                        )}
                      </div>
                    ))}
                  </div>

                  {/* Setup Time Row */}
                  <div className="grid grid-cols-1 md:grid-cols-4 border-b border-[#e5e5e5] py-5">
                    <div className="px-5 flex items-center">
                      <div className="text-[13px] font-semibold uppercase tracking-wide">⚙️ Setup Time</div>
                    </div>
                    {compareProducts.map((product, idx) => (
                      <div key={idx} className="px-5 py-3 text-center">
                        <div className="text-[20px] font-bold mb-1">
                          {product.practical_metrics?.setup_time || 'Ready'}
                        </div>
                        {product.practical_metrics?.setup_details && (
                          <div className="text-[11px] text-[#79786c]">
                            {product.practical_metrics.setup_details}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>

                  {/* Learning Curve Row */}
                  <div className="grid grid-cols-1 md:grid-cols-4 border-b border-[#e5e5e5] py-5">
                    <div className="px-5 flex items-center">
                      <div className="text-[13px] font-semibold uppercase tracking-wide">📚 Learning Curve</div>
                    </div>
                    {compareProducts.map((product, idx) => {
                      const learningCurve = product.practical_metrics?.learning_curve || 'Medium'
                      const colorClass =
                        learningCurve === 'Low' ? 'text-green-600' :
                        learningCurve === 'High' ? 'text-orange-600' : 'text-yellow-600'

                      return (
                        <div key={idx} className="px-5 py-3 text-center">
                          <div className={`text-[20px] font-bold mb-1 ${colorClass}`}>
                            {learningCurve}
                          </div>
                          {product.practical_metrics?.learning_details && (
                            <div className="text-[11px] text-[#79786c]">
                              {product.practical_metrics.learning_details}
                            </div>
                          )}
                        </div>
                      )
                    })}
                  </div>

                  {/* Maintenance Row */}
                  <div className="grid grid-cols-1 md:grid-cols-4 border-b border-[#e5e5e5] py-5">
                    <div className="px-5 flex items-center">
                      <div className="text-[13px] font-semibold uppercase tracking-wide">🔧 Maintenance</div>
                    </div>
                    {compareProducts.map((product, idx) => {
                      const maintenance = product.practical_metrics?.maintenance_level || product.maintenance_level || 'Medium'
                      const colorClass =
                        maintenance === 'Low' ? 'text-green-600' :
                        maintenance === 'High' ? 'text-orange-600' : 'text-yellow-600'

                      return (
                        <div key={idx} className="px-5 py-3 text-center">
                          <div className={`text-[20px] font-bold mb-1 ${colorClass}`}>
                            {maintenance}
                          </div>
                          {product.practical_metrics?.maintenance_details && (
                            <div className="text-[11px] text-[#79786c]">
                              {product.practical_metrics.maintenance_details}
                            </div>
                          )}
                        </div>
                      )
                    })}
                  </div>

                  {/* Weight Row */}
                  <div className="grid grid-cols-1 md:grid-cols-4 border-b border-[#e5e5e5] py-5">
                    <div className="px-5 flex items-center">
                      <div className="text-[13px] font-semibold uppercase tracking-wide">⚖️ Weight</div>
                    </div>
                    {compareProducts.map((product, idx) => (
                      <div key={idx} className="px-5 py-3 text-center">
                        {product.practical_metrics?.weight_lbs ? (
                          <>
                            <div className="text-[20px] font-bold mb-1">
                              {product.practical_metrics.weight_lbs} lbs
                            </div>
                            {product.practical_metrics.weight_notes && (
                              <div className="text-[11px] text-[#79786c]">
                                {product.practical_metrics.weight_notes}
                              </div>
                            )}
                          </>
                        ) : (
                          <div className="text-[13px] text-[#79786c]">Not specified</div>
                        )}
                      </div>
                    ))}
                  </div>

                  {/* Dishwasher Safe Row */}
                  <div className="grid grid-cols-1 md:grid-cols-4 border-b border-[#e5e5e5] py-5">
                    <div className="px-5 flex items-center">
                      <div className="text-[13px] font-semibold uppercase tracking-wide">🚿 Dishwasher Safe</div>
                    </div>
                    {compareProducts.map((product, idx) => {
                      const isSafe = product.practical_metrics?.dishwasher_safe
                      return (
                        <div key={idx} className="px-5 py-3 text-center">
                          <div className={`text-[20px] font-bold ${isSafe ? 'text-green-600' : 'text-red-600'}`}>
                            {isSafe ? '✓ Yes' : '✗ No'}
                          </div>
                        </div>
                      )
                    })}
                  </div>

                  {/* Oven Safe Row */}
                  <div className="grid grid-cols-1 md:grid-cols-4 py-5">
                    <div className="px-5 flex items-center">
                      <div className="text-[13px] font-semibold uppercase tracking-wide">🔥 Oven Safe</div>
                    </div>
                    {compareProducts.map((product, idx) => {
                      const isSafe = product.practical_metrics?.oven_safe
                      return (
                        <div key={idx} className="px-5 py-3 text-center">
                          {isSafe ? (
                            <>
                              <div className="text-[20px] font-bold text-green-600 mb-1">
                                ✓ Yes
                              </div>
                              {product.practical_metrics.oven_max_temp && (
                                <div className="text-[11px] text-[#79786c]">
                                  Up to {product.practical_metrics.oven_max_temp}°F
                                </div>
                              )}
                            </>
                          ) : (
                            <div className="text-[20px] font-bold text-red-600">✗ No</div>
                          )}
                        </div>
                      )
                    })}
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
        )}

      </div>
    </main>
  )
}
