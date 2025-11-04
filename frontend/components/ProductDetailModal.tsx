'use client'

import { Product } from '@/types'

interface ProductDetailModalProps {
  product: Product
  onClose: () => void
}

export default function ProductDetailModal({ product, onClose }: ProductDetailModalProps) {
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

  // Generate star rating from quality score
  const getStars = (score: number) => {
    const fullStars = Math.floor((score / 100) * 5)
    const hasHalfStar = (score / 100) * 5 - fullStars >= 0.5
    let stars = '★'.repeat(fullStars)
    if (hasHalfStar) stars += '☆'
    const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0)
    stars += '☆'.repeat(emptyStars)
    return stars
  }

  const qualityScore = product.quality_data?.score || 0

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
                <span className={`inline-block text-[10px] px-2 py-1 uppercase tracking-wide font-semibold ${getTierClass(product.tier)}`}>
                  {product.tier}
                </span>
              </div>
              <p className="text-sm text-gray-600">{product.brand} • {product.category}</p>

              {/* Quality Stars */}
              {qualityScore > 0 && (
                <div className="flex items-center gap-2 mt-2">
                  <span className="text-[#fbbf24] text-base">{getStars(qualityScore)}</span>
                  <span className="text-xs text-gray-600">
                    Quality: <span className="text-black font-semibold">{(qualityScore / 10).toFixed(1)}/10</span>
                  </span>
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
            {/* Value Breakdown */}
            <section>
              <h3 className="text-xs font-bold uppercase tracking-wide mb-3 text-gray-700">Value Breakdown</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-gray-50 p-3 border border-gray-200">
                  <div className="text-[10px] text-gray-500 uppercase tracking-wide mb-1">Upfront Price</div>
                  <div className="text-2xl font-bold">${product.value_metrics.upfront_price}</div>
                </div>
                <div className="bg-gray-50 p-3 border border-gray-200">
                  <div className="text-[10px] text-gray-500 uppercase tracking-wide mb-1">Expected Lifespan</div>
                  <div className="text-2xl font-bold">{product.value_metrics.expected_lifespan_years}<span className="text-sm"> yrs</span></div>
                </div>
                <div className="bg-gray-50 p-3 border border-gray-200">
                  <div className="text-[10px] text-gray-500 uppercase tracking-wide mb-1">Cost Per Year</div>
                  <div className="text-2xl font-bold">${product.value_metrics.cost_per_year}</div>
                </div>
                <div className="bg-gray-50 p-3 border border-gray-200">
                  <div className="text-[10px] text-gray-500 uppercase tracking-wide mb-1">Cost Per Day</div>
                  <div className="text-2xl font-bold">${product.value_metrics.cost_per_day}</div>
                </div>
              </div>
            </section>

            {/* Why It's a Gem */}
            <section className="bg-yellow-50 border border-yellow-200 p-4">
              <h3 className="text-xs font-bold uppercase tracking-wide mb-2 text-yellow-900 flex items-center gap-2">
                <span>💎</span>
                Why It's a Gem
              </h3>
              <p className="text-sm text-gray-800 leading-relaxed">{product.why_its_a_gem}</p>
            </section>

            {/* Quality & Durability */}
            {product.quality_data && (
              <section>
                <h3 className="text-xs font-bold uppercase tracking-wide mb-3 text-gray-700">Quality & Durability</h3>
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div className="bg-gray-50 p-3 border border-gray-200">
                    <div className="text-[10px] text-gray-500 uppercase tracking-wide mb-1">Quality Score</div>
                    <div className="text-2xl font-bold">{product.quality_data.score}/100</div>
                  </div>
                  <div className="bg-gray-50 p-3 border border-gray-200">
                    <div className="text-[10px] text-gray-500 uppercase tracking-wide mb-1">Avg Lifespan</div>
                    <div className="text-2xl font-bold">{product.quality_data.average_lifespan_years}<span className="text-sm"> yrs</span></div>
                  </div>
                  <div className="bg-gray-50 p-3 border border-gray-200">
                    <div className="text-[10px] text-gray-500 uppercase tracking-wide mb-1">Still Working After 5 Years</div>
                    <div className="text-2xl font-bold">{product.quality_data.still_working_after_5years_percent}%</div>
                  </div>
                  <div className="bg-gray-50 p-3 border border-gray-200">
                    <div className="text-[10px] text-gray-500 uppercase tracking-wide mb-1">Repairability</div>
                    <div className="text-2xl font-bold">{product.quality_data.repairability_score}/100</div>
                  </div>
                </div>

                {product.quality_data.common_failure_points.length > 0 && (
                  <div className="mb-3">
                    <div className="text-[10px] font-bold uppercase tracking-wide text-gray-600 mb-2">Common Failure Points</div>
                    <ul className="space-y-1">
                      {product.quality_data.common_failure_points.map((point, idx) => (
                        <li key={idx} className="text-xs text-gray-700 pl-3 relative before:content-['•'] before:absolute before:left-0">
                          {point}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {product.quality_data.material_quality_indicators.length > 0 && (
                  <div className="mb-3">
                    <div className="text-[10px] font-bold uppercase tracking-wide text-gray-600 mb-2">Material Quality Indicators</div>
                    <ul className="space-y-1">
                      {product.quality_data.material_quality_indicators.map((indicator, idx) => (
                        <li key={idx} className="text-xs text-gray-700 pl-3 relative before:content-['✓'] before:absolute before:left-0 before:text-green-600">
                          {indicator}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {product.quality_data.total_user_reports > 0 && (
                  <div className="text-[10px] text-gray-500 italic">
                    Based on {product.quality_data.total_user_reports.toLocaleString()} user reports
                  </div>
                )}
              </section>
            )}

            {/* Practical Day-to-Day Use */}
            {product.practical_metrics && (
              <section>
                <h3 className="text-xs font-bold uppercase tracking-wide mb-3 text-gray-700">Practical Day-to-Day Use</h3>
                <div className="space-y-3">
                  {/* Cleaning */}
                  <div className="bg-gray-50 p-3 border border-gray-200">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-[10px] font-bold uppercase tracking-wide text-gray-600">Cleaning</span>
                      {product.practical_metrics.cleaning_time_minutes && (
                        <span className="text-xs text-gray-600">{product.practical_metrics.cleaning_time_minutes} min</span>
                      )}
                    </div>
                    <p className="text-xs text-gray-700">{product.practical_metrics.cleaning_details}</p>
                    <div className="flex gap-2 mt-2">
                      {product.practical_metrics.dishwasher_safe && (
                        <span className="text-[9px] bg-green-100 text-green-800 px-2 py-0.5 uppercase tracking-wide">Dishwasher Safe</span>
                      )}
                    </div>
                  </div>

                  {/* Setup */}
                  <div className="bg-gray-50 p-3 border border-gray-200">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-[10px] font-bold uppercase tracking-wide text-gray-600">Setup Time</span>
                      <span className="text-xs text-gray-600">{product.practical_metrics.setup_time}</span>
                    </div>
                    {product.practical_metrics.setup_details && (
                      <p className="text-xs text-gray-700">{product.practical_metrics.setup_details}</p>
                    )}
                  </div>

                  {/* Learning Curve */}
                  <div className="bg-gray-50 p-3 border border-gray-200">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-[10px] font-bold uppercase tracking-wide text-gray-600">Learning Curve</span>
                      <span className="text-xs text-gray-600">{product.practical_metrics.learning_curve}</span>
                    </div>
                    {product.practical_metrics.learning_details && (
                      <p className="text-xs text-gray-700">{product.practical_metrics.learning_details}</p>
                    )}
                  </div>

                  {/* Maintenance */}
                  <div className="bg-gray-50 p-3 border border-gray-200">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-[10px] font-bold uppercase tracking-wide text-gray-600">Maintenance</span>
                      <span className="text-xs text-gray-600">{product.practical_metrics.maintenance_level}</span>
                    </div>
                    {product.practical_metrics.maintenance_details && (
                      <p className="text-xs text-gray-700">{product.practical_metrics.maintenance_details}</p>
                    )}
                  </div>

                  {/* Weight & Handling */}
                  {product.practical_metrics.weight_lbs && (
                    <div className="bg-gray-50 p-3 border border-gray-200">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-[10px] font-bold uppercase tracking-wide text-gray-600">Weight</span>
                        <span className="text-xs text-gray-600">{product.practical_metrics.weight_lbs} lbs</span>
                      </div>
                      {product.practical_metrics.weight_notes && (
                        <p className="text-xs text-gray-700">{product.practical_metrics.weight_notes}</p>
                      )}
                    </div>
                  )}

                  {/* Oven Safe */}
                  {product.practical_metrics.oven_safe && (
                    <div className="bg-gray-50 p-3 border border-gray-200">
                      <div className="flex items-center justify-between">
                        <span className="text-[10px] font-bold uppercase tracking-wide text-gray-600">Oven Safe</span>
                        <span className="text-xs text-gray-600">
                          {product.practical_metrics.oven_max_temp ? `Up to ${product.practical_metrics.oven_max_temp}°F` : 'Yes'}
                        </span>
                      </div>
                    </div>
                  )}
                </div>
              </section>
            )}

            {/* Key Features */}
            <section>
              <h3 className="text-xs font-bold uppercase tracking-wide mb-3 text-gray-700">Key Features</h3>
              <ul className="space-y-2">
                {product.key_features.map((feature, idx) => (
                  <li key={idx} className="text-sm text-gray-700 pl-4 relative before:content-['•'] before:absolute before:left-0 before:text-black before:font-bold">
                    {feature}
                  </li>
                ))}
              </ul>
            </section>

            {/* Materials */}
            {product.materials.length > 0 && (
              <section>
                <h3 className="text-xs font-bold uppercase tracking-wide mb-3 text-gray-700">Materials</h3>
                <div className="flex flex-wrap gap-2">
                  {product.materials.map((material, idx) => (
                    <span key={idx} className="text-xs bg-gray-100 text-gray-800 px-3 py-1 border border-gray-200">
                      {material}
                    </span>
                  ))}
                </div>
              </section>
            )}

            {/* Characteristics */}
            {product.characteristics.length > 0 && (
              <section>
                <h3 className="text-xs font-bold uppercase tracking-wide mb-3 text-gray-700">Characteristics</h3>
                <div className="flex flex-wrap gap-2">
                  {product.characteristics.map((char, idx) => (
                    <span key={idx} className="text-xs bg-blue-50 text-blue-800 px-3 py-1 border border-blue-200">
                      {char}
                    </span>
                  ))}
                </div>
              </section>
            )}

            {/* Best For */}
            <section className="bg-blue-50 border border-blue-200 p-4">
              <h3 className="text-xs font-bold uppercase tracking-wide mb-2 text-blue-900">Best For</h3>
              <p className="text-sm text-gray-800">{product.best_for}</p>
            </section>

            {/* Trade-offs */}
            {product.trade_offs && product.trade_offs.length > 0 && (
              <section className="bg-orange-50 border border-orange-200 p-4">
                <h3 className="text-xs font-bold uppercase tracking-wide mb-2 text-orange-900">Honest Trade-offs</h3>
                <ul className="space-y-1">
                  {product.trade_offs.map((tradeOff, idx) => (
                    <li key={idx} className="text-sm text-gray-800 pl-4 relative before:content-['⚠'] before:absolute before:left-0">
                      {tradeOff}
                    </li>
                  ))}
                </ul>
              </section>
            )}

            {/* Environmental Warnings */}
            {product.environmental_warnings && product.environmental_warnings.length > 0 && (
              <section className="bg-red-50 border border-red-200 p-4">
                <h3 className="text-xs font-bold uppercase tracking-wide mb-2 text-red-900">Environmental Warnings</h3>
                <ul className="space-y-1">
                  {product.environmental_warnings.map((warning, idx) => (
                    <li key={idx} className="text-sm text-gray-800 pl-4 relative before:content-['⚠️'] before:absolute before:left-0">
                      {warning}
                    </li>
                  ))}
                </ul>
              </section>
            )}

            {/* Sources & Research */}
            <section>
              <h3 className="text-xs font-bold uppercase tracking-wide mb-3 text-gray-700">Sources & Research</h3>

              {/* Web Sources */}
              {product.web_sources.length > 0 && (
                <div className="mb-4">
                  <div className="text-[10px] font-bold uppercase tracking-wide text-gray-600 mb-2">
                    Web Sources ({product.web_sources.length})
                  </div>
                  <div className="space-y-2">
                    {product.web_sources.slice(0, 5).map((source, idx) => (
                      <a
                        key={idx}
                        href={source.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="block bg-gray-50 p-3 border border-gray-200 hover:border-black transition-colors"
                      >
                        <div className="text-xs font-semibold text-black mb-1">{source.title}</div>
                        <div className="text-[10px] text-gray-600 line-clamp-2">{source.snippet}</div>
                        <div className="text-[9px] text-gray-400 mt-1">{source.url}</div>
                      </a>
                    ))}
                  </div>
                </div>
              )}

              {/* Professional Reviews */}
              {product.professional_reviews.length > 0 && (
                <div className="mb-4">
                  <div className="text-[10px] font-bold uppercase tracking-wide text-gray-600 mb-2">
                    Professional Reviews ({product.professional_reviews.length})
                  </div>
                  <ul className="space-y-1">
                    {product.professional_reviews.map((review, idx) => (
                      <li key={idx} className="text-xs text-gray-700 pl-3 relative before:content-['•'] before:absolute before:left-0">
                        {review}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Reddit Mentions */}
              {product.reddit_mentions && product.reddit_mentions > 0 && (
                <div className="text-[10px] text-gray-500">
                  Mentioned in {product.reddit_mentions} Reddit discussions
                </div>
              )}
            </section>

            {/* Where to Buy */}
            {product.purchase_links.length > 0 && (
              <section>
                <h3 className="text-xs font-bold uppercase tracking-wide mb-3 text-gray-700">Where to Buy</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {product.purchase_links.map((link, idx) => (
                    <a
                      key={idx}
                      href={link.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="bg-black text-white px-4 py-3 text-sm uppercase tracking-wide text-center hover:bg-gray-800 transition-colors"
                    >
                      Buy from {link.name}
                    </a>
                  ))}
                </div>
              </section>
            )}
          </div>
        </div>
      </div>
    </>
  )
}
