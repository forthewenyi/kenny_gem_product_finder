'use client'

import { useState } from 'react'
import { Product } from '@/types'

interface ProductCardProps {
  product: Product
  onClick?: () => void
  comparisonMode?: boolean
  isSelected?: boolean
  selectionNumber?: number // 1, 2, or 3
  isKennysPick?: boolean
  animationDelay?: number // For staggered animation
}

export default function ProductCard({
  product,
  onClick,
  comparisonMode = false,
  isSelected = false,
  selectionNumber,
  isKennysPick = false,
  animationDelay = 0
}: ProductCardProps) {
  const [isHovering, setIsHovering] = useState(false)

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

  // Generate star rating from durability score
  const getStars = (score: number) => {
    const fullStars = Math.floor((score / 100) * 5)
    const hasHalfStar = (score / 100) * 5 - fullStars >= 0.5
    let stars = '★'.repeat(fullStars)
    if (hasHalfStar) stars += '☆'
    const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0)
    stars += '☆'.repeat(emptyStars)
    return stars
  }

  const durabilityScore = product.durability_data?.score || 0

  return (
    <div
      className={`bg-white flex flex-col cursor-pointer relative transition-all animate-fadeInUp ${
        isSelected ? 'outline outline-3 outline-black outline-offset-[-3px]' : ''
      }`}
      style={{ animationDelay: `${animationDelay * 50}ms` }}
      onClick={onClick}
      onMouseEnter={() => setIsHovering(true)}
      onMouseLeave={() => setIsHovering(false)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault()
          onClick?.()
        }
      }}
      aria-label={`${product.name} by ${product.brand}, ${product.tier} tier, $${product.value_metrics.upfront_price}`}
    >
      {/* Selection Indicator - Numbered Circle */}
      {isSelected && selectionNumber && (
        <div className="absolute top-3 right-3 bg-black text-white w-7 h-7 rounded-full flex items-center justify-center text-base font-bold z-20">
          {selectionNumber}
        </div>
      )}

      {/* Kenny's Pick Badge */}
      {isKennysPick && (
        <div className="absolute top-3 left-3 bg-black text-white px-2.5 py-1 text-[10px] uppercase tracking-wide flex items-center gap-1 z-10">
          💎 Kenny's Pick
        </div>
      )}

      {/* Image Container */}
      <div className="relative w-full bg-[#f8f8f8] overflow-hidden" style={{ paddingBottom: '118.9%' }}>
        {/* Primary Image */}
        <img
          src="https://images.unsplash.com/photo-1556909172-54557c7e4fb7?w=800&auto=format&fit=crop"
          alt={product.name}
          className="absolute top-0 left-0 w-full h-full object-cover transition-opacity duration-300"
          style={{ opacity: isHovering ? 0 : 1 }}
        />

        {/* Secondary Image - Shows on Hover */}
        <img
          src="https://images.unsplash.com/photo-1585515320310-259814833e62?w=800&auto=format&fit=crop"
          alt={`${product.name} detail`}
          className="absolute top-0 left-0 w-full h-full object-cover transition-opacity duration-300"
          style={{ opacity: isHovering ? 1 : 0 }}
        />

        {/* "Select to Compare" Button - Shows on Hover */}
        {comparisonMode && (
          <button
            className="absolute bottom-3 left-1/2 transform -translate-x-1/2 bg-[#f8f8f8] border border-[#e5e5e5] px-3.5 py-1.5 text-[11px] uppercase tracking-wide transition-opacity duration-300 hover:bg-black hover:text-white hover:border-black"
            style={{ opacity: isHovering ? 1 : 0 }}
            onClick={(e) => {
              e.stopPropagation()
              onClick?.()
            }}
          >
            Select to Compare
          </button>
        )}
      </div>

      {/* Product Info */}
      <div className="bg-[#f8f8f8] p-3 flex flex-col gap-1.5">
        {/* Product Name */}
        <div className="text-[11px] uppercase tracking-wide font-normal text-[#79786c]">
          {product.name}
        </div>

        {/* Pricing */}
        <div className="flex items-center gap-1.5 text-[11px]">
          <span className="font-semibold text-black">${product.value_metrics.upfront_price}</span>
          <span className="text-[#79786c] text-[10px]">• ${product.value_metrics.cost_per_year}/year</span>
        </div>

        {/* Durability */}
        <div className="flex items-center gap-1.5 text-[10px] text-[#79786c]">
          <span className="text-[#fbbf24] text-[11px]">{getStars(durabilityScore)}</span>
          <span>Durability: <span className="text-black font-semibold">{(durabilityScore / 10).toFixed(1)}</span></span>
        </div>

        {/* Tier Badge */}
        <span className={`inline-block text-[9px] px-2 py-0.5 uppercase tracking-wide font-semibold mt-1 ${getTierClass(product.tier)}`}>
          {product.tier}
        </span>
      </div>
    </div>
  )
}
