export default function LoadingState() {
  return (
    <div className="w-full max-w-6xl mx-auto py-12">
      <div className="text-center mb-8">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
        <h3 className="text-xl font-semibold text-gray-900 mb-2">
          🔍 Researching the Web
        </h3>
        <p className="text-gray-600">
          Searching Reddit, review sites, and kitchen forums for the best recommendations...
        </p>
      </div>

      {/* Loading Steps */}
      <div className="max-w-md mx-auto space-y-3">
        <LoadingStep text="Searching r/BuyItForLife, r/Cooking, r/AskCulinary..." />
        <LoadingStep text="Checking professional review sites..." delay={1000} />
        <LoadingStep text="Finding hidden gems from niche manufacturers..." delay={2000} />
        <LoadingStep text="Analyzing findings and calculating value metrics..." delay={3000} />
      </div>

      <p className="text-center text-sm text-gray-500 mt-8">
        This usually takes 10-30 seconds
      </p>
    </div>
  )
}

function LoadingStep({ text, delay = 0 }: { text: string; delay?: number }) {
  return (
    <div
      className="flex items-center gap-3 text-gray-700 animate-pulse"
      style={{ animationDelay: `${delay}ms` }}
    >
      <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
      <span className="text-sm">{text}</span>
    </div>
  )
}
