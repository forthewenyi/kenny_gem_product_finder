'use client'

import { useState, useEffect } from 'react'

const messages = [
  "No algorithms. No ads. Just honest recommendations for kitchen tools that last.",
  "Meet Kenny, Your Personal Gem Finder",
  "Kenny doesn't take affiliate commissions",
  "Kenny calculates cost-per-year, not just price tags"
]

export default function TopBanner() {
  const [currentIndex, setCurrentIndex] = useState(0)
  const [isVisible, setIsVisible] = useState(true)

  useEffect(() => {
    const interval = setInterval(() => {
      // Fade out
      setIsVisible(false)

      // After fade out, change message and fade in
      setTimeout(() => {
        setCurrentIndex((prev) => (prev + 1) % messages.length)
        setIsVisible(true)
      }, 300) // Half of transition duration
    }, 5000) // Change every 5 seconds

    return () => clearInterval(interval)
  }, [])

  return (
    <div className="bg-black text-white text-center py-2.5 px-5">
      <div
        className={`text-xs uppercase tracking-wider transition-opacity duration-500 ${
          isVisible ? 'opacity-100' : 'opacity-0'
        }`}
      >
        {messages[currentIndex]}
      </div>
    </div>
  )
}
