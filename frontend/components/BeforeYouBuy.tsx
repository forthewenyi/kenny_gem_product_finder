import { BeforeYouBuy as BeforeYouBuyType, AlternativeSolution } from '@/types'

interface BeforeYouBuyProps {
  data: BeforeYouBuyType
}

export default function BeforeYouBuy({ data }: BeforeYouBuyProps) {
  return (
    <div className="mb-8 bg-gradient-to-r from-blue-50 to-green-50 rounded-xl p-8 border-2 border-blue-200">
      {/* Header */}
      <div className="text-center mb-6">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">
          {data.title}
        </h2>
        <p className="text-lg text-gray-600">
          {data.subtitle}
        </p>
      </div>

      {/* Educational Insight */}
      <div className="mb-6 bg-blue-100 rounded-lg p-4">
        <p className="text-sm text-blue-800">
          💡 {data.educational_insight}
        </p>
      </div>

      {/* Alternatives */}
      <div className="space-y-6">
        {data.alternatives.map((alt, index) => (
          <AlternativeCard key={index} alternative={alt} index={index} />
        ))}
      </div>

      {/* Still Want to Buy CTA */}
      <div className="mt-6 text-center border-t-2 border-blue-200 pt-6">
        <p className="text-sm text-gray-600 mb-3">
          Still want to buy? Scroll down for the best products that last.
        </p>
        <div className="text-2xl">👇</div>
      </div>
    </div>
  )
}

interface AlternativeCardProps {
  alternative: AlternativeSolution
  index: number
}

function AlternativeCard({ alternative, index }: AlternativeCardProps) {
  return (
    <div className="bg-white rounded-lg p-6 shadow-md">
      {/* Problem Statement */}
      <div className="mb-4">
        <h3 className="text-lg font-bold text-gray-900 mb-2">
          Problem: {alternative.problem}
        </h3>
      </div>

      {/* Two Column Comparison */}
      <div className="grid md:grid-cols-2 gap-6 mb-4">
        {/* What People Usually Buy (Left - Red tint) */}
        <div className="bg-red-50 rounded-lg p-4 border-2 border-red-200">
          <div className="flex items-center gap-2 mb-3">
            <span className="text-2xl">❌</span>
            <h4 className="font-bold text-red-900">Typical Solution</h4>
          </div>

          <div className="mb-3">
            <p className="font-semibold text-red-800 mb-1">
              {alternative.consumer_solution}
            </p>
            <p className="text-lg font-bold text-red-900">
              ${alternative.consumer_cost}
            </p>
          </div>

          <div>
            <p className="text-xs font-semibold text-red-700 mb-2">Issues:</p>
            <ul className="space-y-1">
              {alternative.consumer_issues.map((issue, i) => (
                <li key={i} className="text-sm text-red-700 flex items-start">
                  <span className="mr-2">•</span>
                  <span>{issue}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Your Better Solution (Right - Green tint) */}
        <div className="bg-green-50 rounded-lg p-4 border-2 border-green-300">
          <div className="flex items-center gap-2 mb-3">
            <span className="text-2xl">✅</span>
            <h4 className="font-bold text-green-900">Better Solution</h4>
          </div>

          <div className="mb-3">
            <p className="font-semibold text-green-800 mb-1">
              {alternative.your_solution}
            </p>
            <p className="text-lg font-bold text-green-900">
              ${alternative.your_cost}
            </p>
          </div>

          <div className="mb-3">
            <p className="text-sm font-semibold text-green-700">
              💰 Saves ${alternative.savings_per_year}/year
            </p>
          </div>

          <div className="bg-green-100 rounded p-2">
            <p className="text-sm text-green-800">
              <strong>Why better:</strong> {alternative.why_better}
            </p>
          </div>
        </div>
      </div>

      {/* How To Instructions */}
      <div className="bg-gray-50 rounded-lg p-4 mb-3">
        <h5 className="text-sm font-bold text-gray-700 mb-2">
          📋 How to do it:
        </h5>
        <p className="text-sm text-gray-700 whitespace-pre-line">
          {alternative.how_to}
        </p>
      </div>

      {/* When to Buy Instead */}
      {alternative.when_to_buy_instead && (
        <div className="bg-yellow-50 rounded-lg p-3 border border-yellow-200">
          <p className="text-xs text-yellow-800">
            <strong>⚠️ When buying makes sense:</strong> {alternative.when_to_buy_instead}
          </p>
        </div>
      )}
    </div>
  )
}
