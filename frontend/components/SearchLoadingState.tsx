'use client'

import { useEffect, useState } from 'react'

const loadingMessages = [
  "Searching Reddit, reviews, and kitchen forums...",
  "Analyzing products found so far...",
  "Calculating cost-per-year and quality scores...",
  "Finding hidden gems from niche manufacturers..."
]

export default function SearchLoadingState() {
  const [messageIndex, setMessageIndex] = useState(0)

  // Rotate messages every 3.5 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setMessageIndex((prev) => (prev + 1) % loadingMessages.length)
    }, 3500)

    return () => clearInterval(interval)
  }, [])

  return (
    <div className="min-h-[60vh] flex items-center justify-center">
      <div className="text-center">
        {/* Animated Pickaxe */}
        <div className="mb-6 animate-swing-pickaxe">
          <span className="text-[32px]">⛏️</span>
        </div>

        {/* Title */}
        <h2 className="text-[14px] font-semibold uppercase tracking-wide text-black mb-3">
          Kenny is digging...
        </h2>

        {/* Rotating Message */}
        <p
          key={messageIndex}
          className="text-[12px] text-[#79786c] max-w-md mx-auto animate-fade-in-text"
        >
          {loadingMessages[messageIndex]}
        </p>
      </div>

      <style jsx>{`
        @keyframes swing-pickaxe {
          0%, 100% {
            transform: rotate(-15deg);
          }
          50% {
            transform: rotate(15deg);
          }
        }

        @keyframes fade-in-text {
          0% {
            opacity: 0;
            transform: translateY(-5px);
          }
          100% {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .animate-swing-pickaxe {
          animation: swing-pickaxe 2s ease-in-out infinite;
          display: inline-block;
          transform-origin: center center;
        }

        .animate-fade-in-text {
          animation: fade-in-text 0.5s ease-out;
        }
      `}</style>
    </div>
  )
}
