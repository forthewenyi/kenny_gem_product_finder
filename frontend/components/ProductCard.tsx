'use client'

import { useState } from 'react'
import { Product } from '@/types'
import TierBadge from './TierBadge'

interface ProductCardProps {
  product: Product
  onClick?: () => void
  comparisonMode?: boolean
  isSelected?: boolean
}

export default function ProductCard({ product, onClick, comparisonMode = false, isSelected = false }: ProductCardProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  // Helper function to get gradient color based on durability score
  const getScoreGradient = (score: number) => {
    if (score >= 80) return 'from-green-50 to-green-100'
    if (score >= 60) return 'from-blue-50 to-blue-100'
    return 'from-yellow-50 to-yellow-100'
  }

  // Helper function to get progress ring color
  const getProgressColor = (score: number) => {
    if (score >= 80) return '#10b981' // green-500
    if (score >= 60) return '#3b82f6' // blue-500
    return '#eab308' // yellow-500
  }

  // Truncate key insight to max 80 chars
  const getKeyInsight = (text: string) => {
    if (text.length <= 80) return text
    return text.slice(0, 77) + '...'
  }

  // Calculate circle progress
  const score = product.durability_data?.score || 0
  const circumference = 2 * Math.PI * 36 // radius = 36
  const strokeDashoffset = circumference - (score / 100) * circumference

  return (
    <div
      onClick={onClick}
      className={`border rounded-xl p-8 hover:shadow-xl transition-all duration-300 cursor-pointer bg-white relative ${
        isSelected
          ? 'border-blue-500 ring-2 ring-blue-200 shadow-xl'
          : 'border-gray-200'
      } ${comparisonMode ? 'hover:border-blue-300' : ''}`}
    >
      {/* Comparison Mode Indicator */}
      {comparisonMode && (
        <div className="absolute top-3 right-3 z-10">
          <div
            className={`w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all ${
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

      {/* Tier Badge - Top Right Corner */}
      <div className="absolute top-3 left-3">
        <TierBadge tier={product.tier} size="sm" />
      </div>

      {/* HERO ELEMENT - Durability Score */}
      {product.durability_data && (
        <div className="flex flex-col items-center mb-6 mt-8">
          <div className={`relative w-20 h-20 bg-gradient-to-br ${getScoreGradient(score)} rounded-full flex items-center justify-center`}>
            {/* SVG Circular Progress Ring */}
            <svg className="absolute inset-0 w-20 h-20 -rotate-90" viewBox="0 0 80 80">
              <circle
                cx="40"
                cy="40"
                r="36"
                stroke="#e5e7eb"
                strokeWidth="4"
                fill="none"
              />
              <circle
                cx="40"
                cy="40"
                r="36"
                stroke={getProgressColor(score)}
                strokeWidth="4"
                fill="none"
                strokeDasharray={circumference}
                strokeDashoffset={strokeDashoffset}
                strokeLinecap="round"
                className="transition-all duration-500"
              />
            </svg>
            {/* Score Number */}
            <div className="relative z-10 text-center">
              <span className="text-5xl font-bold text-gray-900">{score}</span>
              <span className="text-base text-gray-500">/100</span>
            </div>
          </div>
          <div className="text-xs text-gray-500 mt-2 font-medium">Durability Score</div>
        </div>
      )}

      {/* Product Name • Brand */}
      <h3 className="text-2xl font-semibold text-gray-900 mb-3 text-center">
        {product.name} <span className="text-gray-400">•</span> <span className="text-gray-600">{product.brand}</span>
      </h3>

      {/* Value Summary - Single Line */}
      <div className="text-lg text-gray-700 text-center mb-4">
        ${product.value_metrics.upfront_price} <span className="text-gray-400">•</span> {product.value_metrics.expected_lifespan_years} years <span className="text-gray-400">•</span> ${product.value_metrics.cost_per_year}/year
      </div>

      {/* Key Insight */}
      <p className="text-base text-gray-600 italic text-center mb-4 leading-relaxed">
        {getKeyInsight(product.why_its_a_gem)}
      </p>

      {/* Expandable Details Button */}
      <button
        onClick={(e) => {
          e.stopPropagation()
          setIsExpanded(!isExpanded)
        }}
        className="w-full py-2 text-sm text-blue-600 hover:text-blue-700 font-medium transition-colors flex items-center justify-center gap-1"
      >
        {isExpanded ? 'Hide details ↑' : 'Show details ↓'}
      </button>

      {/* Expandable Details Section */}
      <div
        className={`overflow-hidden transition-all duration-300 ease-in-out ${
          isExpanded ? 'max-h-[1000px] opacity-100 mt-4' : 'max-h-0 opacity-0'
        }`}
      >
        <div className="pt-4 border-t border-gray-200 space-y-4">
          {/* Key Features */}
          {product.key_features && product.key_features.length > 0 && (
            <div>
              <h4 className="text-sm font-semibold text-gray-900 mb-2">Key Features</h4>
              <ul className="space-y-1.5">
                {product.key_features.slice(0, 5).map((feature, idx) => (
                  <li key={idx} className="text-sm text-gray-700 flex items-start">
                    <span className="text-green-500 mr-2 mt-0.5">✓</span>
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Durability Details */}
          {product.durability_data && (
            <div>
              <h4 className="text-sm font-semibold text-gray-900 mb-2">Durability Details</h4>
              <div className="space-y-1.5">
                <p className="text-sm text-gray-700">
                  {product.durability_data.still_working_after_5years_percent}% still working after 5+ years
                </p>
                <p className="text-sm text-gray-700">
                  Average lifespan: {product.durability_data.average_lifespan_years} years
                </p>
                <p className="text-sm text-gray-700">
                  Based on {product.durability_data.total_user_reports} user reports
                </p>
              </div>
            </div>
          )}

          {/* Common Failure Points */}
          {product.durability_data?.common_failure_points &&
           product.durability_data.common_failure_points.length > 0 && (
            <div className="border border-gray-200 rounded-lg p-3">
              <h4 className="text-sm font-semibold text-gray-900 mb-2">Common Issues Reported</h4>
              <ul className="space-y-1">
                {product.durability_data.common_failure_points.slice(0, 3).map((issue, idx) => (
                  <li key={idx} className="text-sm text-gray-700 flex items-start">
                    <span className="mr-2 mt-0.5">⚠️</span>
                    <span>{issue}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Trade-offs */}
          {product.trade_offs && product.trade_offs.length > 0 && (
            <div className="border border-gray-200 rounded-lg p-3">
              <h4 className="text-sm font-semibold text-gray-900 mb-2">Trade-offs</h4>
              <ul className="space-y-1">
                {product.trade_offs.map((tradeoff, idx) => (
                  <li key={idx} className="text-sm text-gray-700 flex items-start">
                    <span className="mr-2 mt-0.5">⚖️</span>
                    <span>{tradeoff}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
