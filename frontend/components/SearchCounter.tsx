'use client'

import { useState, useEffect } from 'react'

interface SearchCounterProps {
  targetCount?: number
  query?: string
}

export default function SearchCounter({ targetCount = 1247, query = 'cast iron skillets' }: SearchCounterProps) {
  const [count, setCount] = useState(0)

  useEffect(() => {
    // Reset and animate counter
    setCount(0)

    const duration = 2000 // 2 seconds animation
    const steps = 60 // Number of steps in animation
    const increment = targetCount / steps
    const stepDuration = duration / steps

    let currentStep = 0
    const timer = setInterval(() => {
      currentStep++
      if (currentStep >= steps) {
        setCount(targetCount)
        clearInterval(timer)
      } else {
        setCount(Math.floor(increment * currentStep))
      }
    }, stepDuration)

    return () => clearInterval(timer)
  }, [targetCount])

  return (
    <div className="max-w-[1400px] mx-auto px-10 py-6 mt-16 flex items-center gap-3 bg-gray-50 border-t border-b border-gray-200">
      {/* Animated pickaxe icon */}
      <span className="text-2xl animate-bounce">⛏️</span>

      <span className="text-xs uppercase tracking-wide text-gray-700">
        Kenny has searched{' '}
        <span className="font-bold text-black">
          {count.toLocaleString()}
        </span>{' '}
        products to find you the best {query}
      </span>
    </div>
  )
}
