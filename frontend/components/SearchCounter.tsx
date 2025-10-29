'use client'

import type { RealSearchMetrics } from '@/types'

interface SearchCounterProps {
  metrics?: RealSearchMetrics | null
  query?: string
}

export default function SearchCounter({ metrics, query = 'products' }: SearchCounterProps) {
  if (!metrics) {
    return null
  }

  return (
    <div className="max-w-[1400px] mx-auto px-10 py-6 mt-16 flex items-center gap-6 bg-gray-50 border-t border-b border-gray-200">
      {/* Pickaxe icon */}
      <span className="text-2xl">⛏️</span>

      {/* Real Search Metrics */}
      <div className="flex flex-col gap-1">
        <span className="text-xs uppercase tracking-wide text-gray-700">
          Kenny analyzed{' '}
          <span className="font-bold text-black">
            {metrics.unique_sources} sources
          </span>{' '}
          from{' '}
          <span className="font-bold text-black">
            {metrics.search_queries_executed} searches
          </span>{' '}
          to find you the best {query}
        </span>

        {/* Breakdown */}
        <div className="flex items-center gap-4 text-[10px] text-gray-500">
          {metrics.reddit_threads > 0 && (
            <span>
              📱 {metrics.reddit_threads} Reddit {metrics.reddit_threads === 1 ? 'thread' : 'threads'}
            </span>
          )}
          {metrics.expert_reviews > 0 && (
            <span>
              ⭐ {metrics.expert_reviews} expert {metrics.expert_reviews === 1 ? 'review' : 'reviews'}
            </span>
          )}
        </div>
      </div>
    </div>
  )
}
