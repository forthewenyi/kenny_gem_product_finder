'use client'

import { QualityData } from '@/types'

interface QualityScoreProps {
  data: QualityData
  showBreakdown?: boolean
  size?: 'sm' | 'md' | 'lg'
}

export default function QualityScore({ data, showBreakdown = false, size = 'md' }: QualityScoreProps) {
  // Get letter grade based on score
  const getGrade = (score: number): string => {
    if (score >= 90) return 'A+'
    if (score >= 85) return 'A'
    if (score >= 80) return 'A-'
    if (score >= 75) return 'B+'
    if (score >= 70) return 'B'
    if (score >= 65) return 'B-'
    if (score >= 60) return 'C+'
    if (score >= 55) return 'C'
    return 'C-'
  }

  // Color coding based on score
  const getScoreColor = (total: number) => {
    if (total >= 85) return 'text-green-600 bg-green-50 border-green-200'
    if (total >= 70) return 'text-blue-600 bg-blue-50 border-blue-200'
    if (total >= 55) return 'text-yellow-600 bg-yellow-50 border-yellow-200'
    return 'text-orange-600 bg-orange-50 border-orange-200'
  }

  const getProgressColor = (total: number) => {
    if (total >= 85) return 'bg-green-600'
    if (total >= 70) return 'bg-blue-600'
    if (total >= 55) return 'bg-yellow-600'
    return 'bg-orange-600'
  }

  const sizeClasses = {
    sm: {
      badge: 'text-xs px-2 py-1',
      score: 'text-lg',
      grade: 'text-sm'
    },
    md: {
      badge: 'text-sm px-3 py-1.5',
      score: 'text-2xl',
      grade: 'text-base'
    },
    lg: {
      badge: 'text-base px-4 py-2',
      score: 'text-4xl',
      grade: 'text-xl'
    }
  }

  if (!showBreakdown) {
    // Compact view - badge with score
    return (
      <div className={`inline-flex items-center gap-2 rounded-lg border-2 font-semibold ${getScoreColor(data.score)} ${sizeClasses[size].badge}`}>
        <span className="flex items-center gap-1">
          🏆
        </span>
        <span className={sizeClasses[size].score}>{data.score}</span>
        <span className={`font-bold ${sizeClasses[size].grade}`}>({getGrade(data.score)})</span>
      </div>
    )
  }

  // Full breakdown view
  return (
    <div className="space-y-4">
      {/* Overall Score */}
      <div className={`rounded-xl border-2 p-6 ${getScoreColor(data.score)}`}>
        <div className="flex items-center justify-between mb-3">
          <div>
            <h3 className="text-lg font-bold">Quality Score</h3>
            <p className="text-sm opacity-75">Based on {data.total_user_reports} user reports</p>
          </div>
          <div className="text-right">
            <div className="text-5xl font-bold">{data.score}</div>
            <div className="text-xl font-semibold">Grade {getGrade(data.score)}</div>
          </div>
        </div>

        {/* Progress bar */}
        <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
          <div
            className={`h-full rounded-full transition-all ${getProgressColor(data.score)}`}
            style={{ width: `${data.score}%` }}
          />
        </div>
      </div>

      {/* Component Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Average Lifespan */}
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-semibold text-gray-700">📅 Avg Lifespan</span>
            <span className="text-lg font-bold text-gray-900">{data.average_lifespan_years} yrs</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
            <div
              className="bg-green-500 h-full rounded-full"
              style={{ width: `${Math.min((data.average_lifespan_years / 30) * 100, 100)}%` }}
            />
          </div>
          <p className="text-xs text-gray-600">
            Based on user reports
          </p>
        </div>

        {/* Still Working After 5 Years */}
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-semibold text-gray-700">⚡ Still Working</span>
            <span className="text-lg font-bold text-gray-900">{data.still_working_after_5years_percent}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
            <div
              className="bg-blue-500 h-full rounded-full"
              style={{ width: `${data.still_working_after_5years_percent}%` }}
            />
          </div>
          <p className="text-xs text-gray-600">
            After 5+ years
          </p>
        </div>

        {/* Repairability */}
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-semibold text-gray-700">🔧 Repairability</span>
            <span className="text-lg font-bold text-gray-900">{data.repairability_score}/100</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
            <div
              className="bg-purple-500 h-full rounded-full"
              style={{ width: `${data.repairability_score}%` }}
            />
          </div>
          <p className="text-xs text-gray-600">
            {data.repairability_score >= 75 ? 'Easy to repair' : data.repairability_score >= 50 ? 'Moderately repairable' : 'Difficult to repair'}
          </p>
        </div>

        {/* Material Quality */}
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-semibold text-gray-700">⭐ Materials</span>
            <span className="text-lg font-bold text-gray-900">{data.material_quality_indicators.length}</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
            <div
              className="bg-orange-500 h-full rounded-full"
              style={{ width: `${Math.min((data.material_quality_indicators.length / 3) * 100, 100)}%` }}
            />
          </div>
          <p className="text-xs text-gray-600">
            {data.material_quality_indicators.join(', ') || 'Standard materials'}
          </p>
        </div>
      </div>

      {/* Data Sources */}
      {data.data_sources.length > 0 && (
        <div className="text-xs text-gray-500 pt-2 border-t">
          <p className="font-semibold mb-1">Data Sources:</p>
          <ul className="list-disc list-inside">
            {data.data_sources.map((source, idx) => (
              <li key={idx}>{source}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
