import { Product } from '@/types'
import TierBadge from './TierBadge'

interface ProductCardProps {
  product: Product
  onClick?: () => void
}

export default function ProductCard({ product, onClick }: ProductCardProps) {
  return (
    <div
      onClick={onClick}
      className="border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow cursor-pointer bg-white"
    >
      {/* Tier Badge */}
      <div className="mb-3">
        <TierBadge tier={product.tier} />
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
      <div className="text-sm text-gray-600 italic">
        Best for: {product.best_for}
      </div>

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
