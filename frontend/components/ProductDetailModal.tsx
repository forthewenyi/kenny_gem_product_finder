'use client'

import { Product } from '@/types'

interface ProductDetailModalProps {
  product: Product
  onClose: () => void
}

export default function ProductDetailModal({ product, onClose }: ProductDetailModalProps) {
  // Helper function to find source URL for a review
  const findReviewSource = (reviewText: string) => {
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

  // Get tier colors
  const getTierClass = (tier: string) => {
    switch (tier) {
      case 'good':
        return 'bg-[#dbe9cc] text-[#3d5a00]'
      case 'better':
        return 'bg-[#fce7b8] text-[#8b5a00]'
      case 'best':
        return 'bg-[#ffe4e6] text-[#9f1239]'
      default:
        return 'bg-gray-200 text-gray-700'
    }
  }

  // Generate star rating from value score (quality_data.score is actually the VALUE score)
  const getStars = (score: number) => {
    const starsOutOf5 = (score / 100) * 5
    // Round to nearest full star (>= 0.5 rounds up)
    const fullStars = Math.round(starsOutOf5)
    let stars = '★'.repeat(fullStars)
    const emptyStars = 5 - fullStars
    stars += '☆'.repeat(emptyStars)
    return stars
  }

  const valueScore = product.quality_data?.score || 0

  // Helper to convert text to title case
  const toTitleCase = (str: string) => {
    return str.split(' ').map(word =>
      word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
    ).join(' ')
  }

  return (
    <>
      {/* Dark Overlay */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 z-50"
        onClick={onClose}
      />

      {/* Modal Content */}
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none">
        <div
          className="bg-white max-w-4xl w-full max-h-[90vh] overflow-y-auto pointer-events-auto"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="sticky top-0 bg-white border-b border-gray-200 p-6 flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <h2 className="text-xl font-bold text-black">{product.name}</h2>
                <span className={`inline-block text-xs px-2 py-1 uppercase tracking-wide font-semibold ${getTierClass(product.tier)}`}>
                  {product.tier}
                </span>
              </div>
              <p className="text-sm text-gray-600">{product.brand} • {toTitleCase(product.category)}</p>

              {/* Value Stars with Score */}
              {valueScore > 0 && (
                <div className="flex items-center gap-2 mt-2">
                  <span className="text-yellow-500 text-lg">{getStars(valueScore)}</span>
                  <span className="text-sm font-medium text-gray-600">Value: {(valueScore / 10).toFixed(1)}</span>
                </div>
              )}
            </div>

            {/* Close Button */}
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-black text-2xl leading-none ml-4"
              aria-label="Close modal"
            >
              ×
            </button>
          </div>

          {/* Content */}
          <div className="p-6 space-y-6">
            {/* Product Image */}
            {product.image_url ? (
              <div className="relative w-full h-96 bg-gray-50 rounded-lg overflow-hidden border border-gray-200">
                <img
                  src={product.image_url}
                  alt={product.name}
                  className="w-full h-full object-contain p-8"
                  onError={(e) => {
                    // Fallback to placeholder if image fails to load
                    e.currentTarget.style.display = 'none'
                    const parent = e.currentTarget.parentElement
                    if (parent) {
                      parent.classList.add('flex', 'items-center', 'justify-center')
                      parent.innerHTML = `
                        <div class="flex flex-col items-center justify-center gap-4 text-gray-400">
                          <svg class="w-24 h-24" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                          </svg>
                          <div class="text-center">
                            <p class="text-sm font-medium text-gray-600">${product.brand}</p>
                            <p class="text-xs text-gray-500 mt-1">Image not available</p>
                          </div>
                        </div>
                      `
                    }
                  }}
                />
              </div>
            ) : (
              /* Placeholder when no image URL available */
              <div className="relative w-full h-96 bg-gray-50 rounded-lg border border-gray-200 flex flex-col items-center justify-center gap-4 text-gray-400">
                <svg className="w-24 h-24" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <div className="text-center">
                  <p className="text-sm font-medium text-gray-600">{product.brand}</p>
                  <p className="text-xs text-gray-500 mt-1">Image not available</p>
                </div>
              </div>
            )}

            {/* 1. PRODUCT */}
            <section className="border-t-4 border-gray-800 pt-4">
              <h2 className="text-sm font-bold uppercase tracking-wide mb-4 text-gray-800">
                PRODUCT
              </h2>

              {/* Materials */}
              {product.materials.length > 0 && (
                <div className="mb-4">
                  <h3 className="text-xs font-bold uppercase tracking-wide mb-2 text-gray-700">Materials</h3>
                  <p className="text-sm text-gray-800">
                    {product.materials.map(m => toTitleCase(m)).join(', ')}
                  </p>
                </div>
              )}

              {/* Key Features */}
              <div className="mb-4">
                <h3 className="text-xs font-bold uppercase tracking-wide mb-2 text-gray-700">Key Features</h3>
                <ul className="space-y-2">
                  {product.key_features.map((feature, idx) => (
                    <li key={idx} className="text-sm text-gray-700 pl-4 relative before:content-['•'] before:absolute before:left-0 before:text-black before:font-bold">
                      {feature}
                    </li>
                  ))}
                </ul>
              </div>

              {/* Why It's a Gem */}
              <div className="bg-yellow-50 border border-yellow-200 p-4 mb-4">
                <h3 className="text-xs font-bold uppercase tracking-wide mb-2 text-yellow-900 flex items-center gap-2">
                  <span>💎</span>
                  Why It's a Gem
                </h3>
                <p className="text-sm text-gray-800 leading-relaxed">{product.why_its_a_gem}</p>
              </div>

              {/* Key Differentiator */}
              {product.key_differentiator && (
                <div className="bg-blue-50 border border-blue-200 p-4 mb-4">
                  <h3 className="text-xs font-bold uppercase tracking-wide mb-2 text-blue-900 flex items-center gap-2">
                    <span>⭐</span>
                    What Sets It Apart
                  </h3>
                  <p className="text-sm text-gray-800 leading-relaxed">{product.key_differentiator}</p>
                </div>
              )}

              {/* Quality & Durability */}
              {product.quality_data && (
                <div>
                  <h3 className="text-xs font-bold uppercase tracking-wide mb-3 text-gray-700">Quality & Durability</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                    <div className="bg-gray-50 p-3 border border-gray-200">
                      <div className="text-xs text-gray-500 uppercase tracking-wide mb-1">Expected Lifespan</div>
                      <div className="text-2xl font-bold">{product.value_metrics.expected_lifespan_years}<span className="text-sm"> yrs</span></div>
                    </div>
                    <div className="bg-gray-50 p-3 border border-gray-200">
                      <div className="text-xs text-gray-500 uppercase tracking-wide mb-1">Still Working After 5 Years</div>
                      <div className="text-2xl font-bold">{product.quality_data.still_working_after_5years_percent}%</div>
                    </div>
                    <div className="bg-gray-50 p-3 border border-gray-200">
                      <div className="text-xs text-gray-500 uppercase tracking-wide mb-1">Repairability</div>
                      <div className="text-2xl font-bold">{(product.quality_data.repairability_score / 10).toFixed(1)}/10</div>
                      <div className="text-xs text-gray-500 mt-1">How easy to fix if broken</div>
                    </div>
                  </div>

                  {product.quality_data.common_failure_points.length > 0 && (
                    <div className="mb-3">
                      <div className="text-xs font-bold uppercase tracking-wide text-gray-600 mb-2">Common Failure Points</div>
                      <ul className="space-y-1">
                        {product.quality_data.common_failure_points.map((point, idx) => (
                          <li key={idx} className="text-sm text-gray-700 leading-relaxed pl-3 relative before:content-['•'] before:absolute before:left-0">
                            {point}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {product.quality_data.total_user_reports > 0 && (
                    <div className="text-xs text-gray-500 italic">
                      Based on {product.quality_data.total_user_reports.toLocaleString()} user reports
                    </div>
                  )}
                </div>
              )}
            </section>

            {/* 2. SERVICE */}
            <section className="border-t-4 border-gray-800 pt-4">
              <h2 className="text-sm font-bold uppercase tracking-wide mb-4 text-gray-800">
                SERVICE
              </h2>

              {/* Practical Day-to-Day Use */}
              {product.practical_metrics && (
                <div className="mb-4">
                  <h3 className="text-xs font-bold uppercase tracking-wide mb-3 text-gray-700">Practical Day-to-Day Use</h3>
                  <div className="divide-y divide-gray-200">
                    {/* Learning Curve */}
                    <div className="py-3">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-bold uppercase tracking-wide text-gray-600">Learning Curve</span>
                        <span className="text-sm text-gray-900 font-medium">{product.practical_metrics.learning_curve}</span>
                      </div>
                      {product.practical_metrics.learning_details && (
                        <p className="text-sm text-gray-700 leading-relaxed">{product.practical_metrics.learning_details}</p>
                      )}
                    </div>

                    {/* Cleaning - Keep gray box as it's important */}
                    <div className="py-3">
                      <div className="bg-gray-50 p-3 border border-gray-200">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-xs font-bold uppercase tracking-wide text-gray-600">Cleaning</span>
                          {product.practical_metrics.cleaning_time_minutes && (
                            <span className="text-sm text-gray-900 font-medium">{product.practical_metrics.cleaning_time_minutes} min</span>
                          )}
                        </div>
                        <p className="text-sm text-gray-700 leading-relaxed">{product.practical_metrics.cleaning_details}</p>
                        <div className="flex gap-2 mt-2">
                          {product.practical_metrics.dishwasher_safe && (
                            <span className="text-xs bg-green-100 text-green-800 px-2 py-1 uppercase tracking-wide font-medium">Dishwasher Safe</span>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Maintenance */}
                    <div className="py-3">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-bold uppercase tracking-wide text-gray-600">Maintenance</span>
                        <span className="text-sm text-gray-900 font-medium">{product.practical_metrics.maintenance_level}</span>
                      </div>
                      {product.practical_metrics.maintenance_details && (
                        <p className="text-sm text-gray-700 leading-relaxed">{product.practical_metrics.maintenance_details}</p>
                      )}
                    </div>

                    {/* Setup */}
                    <div className="py-3">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-bold uppercase tracking-wide text-gray-600">Setup Time</span>
                        <span className="text-sm text-gray-900 font-medium">{product.practical_metrics.setup_time}</span>
                      </div>
                      {product.practical_metrics.setup_details && (
                        <p className="text-sm text-gray-700 leading-relaxed">{product.practical_metrics.setup_details}</p>
                      )}
                    </div>

                    {/* Weight & Handling */}
                    {product.practical_metrics.weight_lbs && (
                      <div className="py-3">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-xs font-bold uppercase tracking-wide text-gray-600">Weight</span>
                          <span className="text-sm text-gray-900 font-medium">{product.practical_metrics.weight_lbs} lbs</span>
                        </div>
                        {product.practical_metrics.weight_notes && (
                          <p className="text-sm text-gray-700 leading-relaxed">{product.practical_metrics.weight_notes}</p>
                        )}
                      </div>
                    )}

                    {/* Oven Safe */}
                    {product.practical_metrics.oven_safe && (
                      <div className="py-3">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-bold uppercase tracking-wide text-gray-600">Oven Safe</span>
                          <span className="text-sm text-gray-900 font-medium">
                            {product.practical_metrics.oven_max_temp ? `Up to ${product.practical_metrics.oven_max_temp}°F` : 'Yes'}
                          </span>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Drawbacks */}
              {product.drawbacks && product.drawbacks.length > 0 && (
                <div className="bg-orange-50 border border-orange-200 p-4">
                  <h3 className="text-xs font-bold uppercase tracking-wide mb-2 text-orange-900">Honest Drawbacks</h3>
                  <ul className="space-y-1">
                    {product.drawbacks.map((drawback, idx) => (
                      <li key={idx} className="text-sm text-gray-800 leading-relaxed pl-4 relative before:content-['⚠'] before:absolute before:left-0">
                        {drawback}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </section>

            {/* 3. EQUITY */}
            <section className="border-t-4 border-gray-800 pt-4">
              <h2 className="text-sm font-bold uppercase tracking-wide mb-4 text-gray-800">
                EQUITY
              </h2>

              {/* Professional Reviews */}
              {product.professional_reviews.length > 0 && (
                <div className="mb-4">
                  <h3 className="text-xs font-bold uppercase tracking-wide mb-2 text-gray-700">Professional Reviews</h3>
                  <ul className="space-y-3">
                    {product.professional_reviews.slice(0, 3).map((review, idx) => {
                      const source = findReviewSource(review)
                      return (
                        <li key={idx} className="border-l-4 border-blue-500 pl-4 py-2">
                          <div className="text-sm text-gray-700 leading-relaxed">
                            {review}
                          </div>
                          {source && (
                            <div className="mt-2">
                              <a
                                href={source.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-xs text-blue-600 hover:text-blue-800 hover:underline"
                              >
                                Source: {source.name} →
                              </a>
                            </div>
                          )}
                        </li>
                      )
                    })}
                  </ul>
                </div>
              )}

              {/* Best For */}
              <div className="bg-blue-50 border border-blue-200 p-4 mb-4">
                <h3 className="text-xs font-bold uppercase tracking-wide mb-2 text-blue-900">Best For</h3>
                <p className="text-sm text-gray-800 leading-relaxed">{product.best_for}</p>
              </div>

              {/* Web Sources (filter out purchase links) */}
              {(() => {
                // Filter out purchase/retail links
                const purchaseKeywords = ['amazon', 'walmart', 'target', 'wayfair', 'buy', 'shop', 'cart', 'checkout', 'purchase']
                const informationalSources = product.web_sources.filter(source =>
                  !purchaseKeywords.some(keyword => source.url.toLowerCase().includes(keyword))
                )

                return informationalSources.length > 0 && (
                  <div>
                    <h3 className="text-xs font-bold uppercase tracking-wide mb-2 text-gray-700">
                      Web Sources ({informationalSources.length})
                    </h3>
                    <div className="space-y-2">
                      {informationalSources.slice(0, 5).map((source, idx) => (
                        <a
                          key={idx}
                          href={source.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="block bg-gray-50 p-3 border border-gray-200 hover:border-black transition-colors"
                        >
                          <div className="text-sm font-semibold text-black mb-1">{source.title}</div>
                          <div className="text-xs text-gray-600 line-clamp-2 leading-relaxed">{source.snippet}</div>
                        </a>
                      ))}
                    </div>
                  </div>
                )
              })()}

              {/* Reddit Mentions */}
              {product.reddit_mentions && product.reddit_mentions > 0 && (
                <div className="text-xs text-gray-500 mt-3">
                  Mentioned in {product.reddit_mentions} Reddit discussions
                </div>
              )}
            </section>

            {/* 4. PRICE */}
            <section className="border-t-4 border-gray-800 pt-4">
              <h2 className="text-sm font-bold uppercase tracking-wide mb-4 text-gray-800">
                PRICE
              </h2>

              {/* Value Breakdown */}
              <div className="mb-4">
                <h3 className="text-xs font-bold uppercase tracking-wide mb-3 text-gray-700">Value Breakdown</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {valueScore > 0 && (
                    <div className="bg-gray-50 p-3 border border-gray-200">
                      <div className="text-xs text-gray-500 uppercase tracking-wide mb-1">Value Score</div>
                      <div className="text-2xl font-bold">{(valueScore / 10).toFixed(1)}/10</div>
                    </div>
                  )}
                  <div className="bg-gray-50 p-3 border border-gray-200">
                    <div className="text-xs text-gray-500 uppercase tracking-wide mb-1">Retail Price</div>
                    <div className="text-2xl font-bold">${product.value_metrics.upfront_price}</div>
                  </div>
                  <div className="bg-gray-50 p-3 border border-gray-200">
                    <div className="text-xs text-gray-500 uppercase tracking-wide mb-1">Expected Lifespan</div>
                    <div className="text-2xl font-bold">{product.value_metrics.expected_lifespan_years}<span className="text-sm"> yrs</span></div>
                  </div>
                  <div className="bg-gray-50 p-3 border border-gray-200">
                    <div className="text-xs text-gray-500 uppercase tracking-wide mb-1">Cost Per Year</div>
                    <div className="text-2xl font-bold">${product.value_metrics.cost_per_year}</div>
                  </div>
                </div>
              </div>

              {/* Where to Buy */}
              {product.purchase_links.length > 0 && (
                <div>
                  <h3 className="text-xs font-bold uppercase tracking-wide mb-3 text-gray-700">Where to Buy</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {(() => {
                      // Prioritize: brand website first, then others, Amazon last
                      const sortedLinks = [...product.purchase_links].sort((a, b) => {
                        const aIsAmazon = a.name.toLowerCase().includes('amazon')
                        const bIsAmazon = b.name.toLowerCase().includes('amazon')
                        const aIsBrand = !aIsAmazon && !a.name.toLowerCase().match(/(walmart|target|wayfair)/)
                        const bIsBrand = !bIsAmazon && !b.name.toLowerCase().match(/(walmart|target|wayfair)/)

                        // Brand sites first
                        if (aIsBrand && !bIsBrand) return -1
                        if (!aIsBrand && bIsBrand) return 1

                        // Amazon last
                        if (aIsAmazon && !bIsAmazon) return 1
                        if (!aIsAmazon && bIsAmazon) return -1

                        return 0
                      })

                      return sortedLinks.map((link, idx) => {
                        const isAmazon = link.name.toLowerCase().includes('amazon')
                        const isBrand = !isAmazon && !link.name.toLowerCase().match(/(walmart|target|wayfair)/)

                        return (
                          <a
                            key={idx}
                            href={link.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className={`px-4 py-3 text-sm uppercase tracking-wide text-center transition-colors ${
                              isBrand
                                ? 'bg-white text-black border-2 border-black hover:bg-black hover:text-white font-semibold'
                                : 'bg-black text-white hover:bg-gray-800'
                            }`}
                          >
                            Buy from {link.name}
                          </a>
                        )
                      })
                    })()}
                  </div>
                </div>
              )}
            </section>

            {/* Environmental Warnings (Standalone at end) */}
            {product.environmental_warnings && product.environmental_warnings.length > 0 && (
              <section className="bg-red-50 border border-red-200 p-4">
                <h3 className="text-xs font-bold uppercase tracking-wide mb-3 text-red-900 flex items-center gap-2">
                  <span>⚠️</span>
                  Environmental Warnings
                </h3>
                <ul className="space-y-2">
                  {product.environmental_warnings.map((warning, idx) => (
                    <li key={idx} className="text-sm text-gray-800">
                      <div className="flex gap-2">
                        <span>⚠️</span>
                        <div className="flex-1 leading-relaxed">{warning}</div>
                      </div>
                    </li>
                  ))}
                </ul>
              </section>
            )}
          </div>
        </div>
      </div>
    </>
  )
}
