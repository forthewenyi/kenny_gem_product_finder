import { Product } from '@/types'
import TierBadge from './TierBadge'
import DurabilityScore from './DurabilityScore'

interface ProductCardProps {
  product: Product
  onClick?: () => void
  comparisonMode?: boolean
  isSelected?: boolean
}

export default function ProductCard({ product, onClick, comparisonMode = false, isSelected = false }: ProductCardProps) {
  return (
    <div
      onClick={onClick}
      className={`border-2 rounded-lg p-6 hover:shadow-lg transition-all cursor-pointer bg-white relative ${
        isSelected
          ? 'border-blue-500 ring-2 ring-blue-200 shadow-lg'
          : 'border-gray-200'
      } ${comparisonMode ? 'hover:border-blue-300' : ''}`}
    >
      {/* Comparison Mode Indicator */}
      {comparisonMode && (
        <div className="absolute top-2 right-2">
          <div
            className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${
              isSelected
                ? 'bg-blue-600 border-blue-600'
                : 'bg-white border-gray-300'
            }`}
          >
            {isSelected && (
              <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
            )}
          </div>
        </div>
      )}
      {/* Tier Badge */}
      <div className="mb-3 flex items-start justify-between">
        <TierBadge tier={product.tier} />
        {/* Durability Score Badge */}
        {product.durability_data && (
          <DurabilityScore data={product.durability_data} size="sm" />
        )}
      </div>

      {/* Product Name and Brand */}
      <h3 className="text-xl font-bold text-gray-900 mb-1">{product.name}</h3>
      <p className="text-sm text-gray-600 mb-4">{product.brand}</p>

      {/* Value Metrics - The Star of the Show! */}
      <div className="bg-blue-50 rounded-lg p-4 mb-4">
        <div className="text-2xl font-bold text-blue-900 mb-2">
          ${product.value_metrics.upfront_price}
        </div>
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div>
            <div className="text-gray-600">Lifespan</div>
            <div className="font-semibold text-gray-900">
              {product.value_metrics.expected_lifespan_years} years
            </div>
          </div>
          <div>
            <div className="text-gray-600">Cost/Year</div>
            <div className="font-semibold text-gray-900">
              ${product.value_metrics.cost_per_year}
            </div>
          </div>
        </div>
        <div className="mt-2 text-xs text-gray-500">
          Just ${product.value_metrics.cost_per_day}/day
        </div>
      </div>

      {/* Why It's a Gem */}
      <div className="mb-4">
        <div className="text-xs font-semibold text-gray-500 uppercase mb-1">
          Why it's a gem
        </div>
        <p className="text-sm text-gray-700 line-clamp-2">
          {product.why_its_a_gem}
        </p>
      </div>

      {/* Key Features */}
      <div className="mb-4">
        <ul className="space-y-1">
          {product.key_features.slice(0, 3).map((feature, idx) => (
            <li key={idx} className="text-sm text-gray-700 flex items-start">
              <span className="text-green-500 mr-2">✓</span>
              <span>{feature}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Best For */}
      <div className="text-sm text-gray-600 italic mb-4">
        Best for: {product.best_for}
      </div>

      {/* Durability Section */}
      {product.durability_data && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <span className="text-2xl font-bold text-gray-900">
                {product.durability_data.score}
              </span>
              <div className="text-left">
                <div className="text-xs font-semibold text-gray-500 uppercase">
                  Durability Score
                </div>
                <div className="text-xs text-gray-500">
                  out of 100
                </div>
              </div>
            </div>
          </div>

          <div className="space-y-2 mb-3">
            <p className="text-sm text-gray-700">
              📊 {product.durability_data.still_working_after_5years_percent}% still working after 5+ years
            </p>
            <p className="text-sm text-gray-700">
              ⏱️ Average lifespan: {product.durability_data.average_lifespan_years} years
            </p>
            <p className="text-sm text-gray-700">
              👥 Based on {product.durability_data.total_user_reports} user reports
            </p>
          </div>

          {product.durability_data.common_failure_points &&
           product.durability_data.common_failure_points.length > 0 && (
            <div className="mt-3 bg-orange-50 rounded-lg p-3">
              <p className="text-xs font-semibold text-orange-800 mb-2">
                Common issues reported:
              </p>
              <ul className="space-y-1">
                {product.durability_data.common_failure_points.slice(0, 3).map((issue, idx) => (
                  <li key={idx} className="text-xs text-orange-700 flex items-start">
                    <span className="mr-2">⚠️</span>
                    <span>{issue}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Trade-offs */}
      {product.trade_offs && product.trade_offs.length > 0 && (
        <div className="mt-3 pt-3 border-t border-gray-200">
          <div className="text-xs text-gray-500">
            ⚠️ {product.trade_offs[0]}
          </div>
        </div>
      )}
    </div>
  )
}
