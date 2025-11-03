'use client'

import { useState } from 'react'

interface SearchQuery {
  phase: string
  query: string
}

interface SearchMetricsProps {
  searchQueries?: SearchQuery[]
  totalSourcesAnalyzed?: number
  queriesGenerated?: number
  sourcesByPhase?: {
    context_discovery?: number
    material_science?: number
    product_identification?: number
    frustration_research?: number
    value_synthesis?: number
  }
  totalProductsResearched?: number
  totalProductsDisplayed?: number
  fromCache?: boolean
}

export default function SearchMetrics({
  searchQueries = [],
  totalSourcesAnalyzed = 0,
  queriesGenerated = 0,
  sourcesByPhase = {},
  totalProductsResearched = 0,
  totalProductsDisplayed = 9,
  fromCache = false
}: SearchMetricsProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  // Show even if no queries (for cached results)
  const hasMetrics = totalSourcesAnalyzed > 0 || queriesGenerated > 0 || totalProductsResearched > 0

  if (!hasMetrics) {
    return null
  }

  return (
    <div className="border border-gray-300 bg-gray-50 p-4 mb-6">
      {/* Header - Always Visible */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between text-left"
        aria-expanded={isExpanded}
      >
        <div className="flex items-center gap-3">
          <span className="text-xl">🔍</span>
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wide">
              Search Transparency {fromCache && <span className="text-[10px] text-gray-500 normal-case">(Cached)</span>}
            </h3>
            <p className="text-[11px] text-gray-600 mt-0.5">
              Kenny analyzed <strong>{totalSourcesAnalyzed.toLocaleString()}</strong> sources from <strong>{queriesGenerated}</strong> searches
              {totalProductsResearched > 0 && (
                <> • Researched <strong>{totalProductsResearched}</strong> products, showing best {totalProductsDisplayed}</>
              )}
            </p>
          </div>
        </div>
        <span className="text-xl text-gray-500">
          {isExpanded ? '−' : '+'}
        </span>
      </button>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="mt-4 space-y-4">
          {/* Summary Stats */}
          <div className="grid grid-cols-4 gap-3 text-[11px]">
            <div className="bg-white p-3 border border-gray-200">
              <div className="text-gray-500 uppercase tracking-wide mb-1 text-[10px]">Research Queries</div>
              <div className="text-2xl font-bold">{queriesGenerated}</div>
            </div>
            <div className="bg-white p-3 border border-gray-200">
              <div className="text-gray-500 uppercase tracking-wide mb-1 text-[10px]">Sources Analyzed</div>
              <div className="text-2xl font-bold">{totalSourcesAnalyzed.toLocaleString()}</div>
            </div>
            <div className="bg-white p-3 border border-gray-200">
              <div className="text-gray-500 uppercase tracking-wide mb-1 text-[10px]">Products Researched</div>
              <div className="text-2xl font-bold">{totalProductsResearched || '20+'}</div>
            </div>
            <div className="bg-white p-3 border border-gray-200">
              <div className="text-gray-500 uppercase tracking-wide mb-1 text-[10px]">Best Shown</div>
              <div className="text-2xl font-bold">{totalProductsDisplayed}</div>
            </div>
          </div>

          {/* Queries by Phase */}
          <div className="space-y-3">
            <h4 className="text-[11px] font-bold uppercase tracking-wide text-gray-700">
              Research Queries Executed:
            </h4>

            {Object.entries(
              searchQueries.reduce((acc, { phase, query }) => {
                if (!acc[phase]) acc[phase] = []
                acc[phase].push(query)
                return acc
              }, {} as Record<string, string[]>)
            ).map(([phase, queries]) => (
              <div key={phase} className="bg-white p-3 border border-gray-200">
                <div className="flex items-center justify-between mb-2">
                  <h5 className="text-[10px] font-bold uppercase tracking-wider text-gray-600">
                    {phase}
                  </h5>
                  <span className="text-[10px] text-gray-500">
                    {sourcesByPhase[phase.toLowerCase().replace(/ /g, '_')] || 0} sources found
                  </span>
                </div>
                <ul className="space-y-1">
                  {queries.map((query, idx) => (
                    <li
                      key={idx}
                      className="text-[11px] text-gray-700 pl-3 relative before:content-['•'] before:absolute before:left-0"
                    >
                      {query}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>

          {/* Explanation */}
          <div className="text-[10px] text-gray-500 italic pt-2 border-t border-gray-200">
            Kenny uses AI to generate contextual research queries based on your search.
            These queries help find real user experiences, expert reviews, and product comparisons
            to give you honest recommendations.
          </div>
        </div>
      )}
    </div>
  )
}
