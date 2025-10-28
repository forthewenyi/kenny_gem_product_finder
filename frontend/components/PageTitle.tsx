'use client'

interface PageTitleProps {
  query?: string
  category?: string
}

export default function PageTitle({ query, category }: PageTitleProps) {
  // Generate title based on query or category
  const getTitle = () => {
    if (query && query.trim()) {
      return query.toUpperCase()
    }
    if (category && category !== 'all') {
      return category.toUpperCase()
    }
    return 'KITCHEN PRODUCTS' // Default
  }

  const getDescription = () => {
    if (query && query.trim()) {
      return `Browse all recommended ${query}, ordered by value tier.`
    }
    if (category && category !== 'all') {
      return `Browse all recommended ${category}, ordered by value tier.`
    }
    return 'Browse all recommended kitchen products, ordered by value tier.'
  }

  return (
    <div className="max-w-[1400px] mx-auto px-10 pt-10 pb-5">
      <p className="text-[13px] text-[#79786c] uppercase tracking-wide mb-2">
        Browse All Kitchen Tools
      </p>
      <h1 className="text-4xl font-bold uppercase tracking-wide mb-2">
        {getTitle()}
      </h1>
      <p className="text-xs text-[#79786c] mt-2" style={{ textTransform: 'none', letterSpacing: '0' }}>
        {getDescription()}
      </p>
    </div>
  )
}
