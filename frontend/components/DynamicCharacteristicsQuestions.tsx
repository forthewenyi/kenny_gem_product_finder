'use client'

import { useState, useMemo } from 'react'
import type { CharacteristicConfig, ProductCharacteristics, CharacteristicAnswer } from '@/types/characteristics'
import type { CharacteristicAnswers } from '@/types/characteristics'

interface DynamicCharacteristicsQuestionsProps {
  productConfig: ProductCharacteristics
  answers: CharacteristicAnswers
  onAnswer: (characteristicId: string, value: string | string[]) => void
  onClear: (characteristicId: string) => void
  onClearAllMemory?: () => void
  getRememberedAnswers?: () => CharacteristicAnswer[]
}

export default function DynamicCharacteristicsQuestions({
  productConfig,
  answers,
  onAnswer,
  onClear,
  onClearAllMemory,
  getRememberedAnswers
}: DynamicCharacteristicsQuestionsProps) {
  const [showAll, setShowAll] = useState(false)

  // Get only characteristic-type questions (not filters)
  const allCharacteristics = productConfig.characteristics.filter(c => c.category === 'characteristic')

  // Get remembered answers to show indicators
  const rememberedAnswers = useMemo(() => {
    if (!getRememberedAnswers) return []
    return getRememberedAnswers()
  }, [getRememberedAnswers])

  // Check if an answer was pre-filled from memory
  const isRemembered = (characteristicId: string): boolean => {
    return rememberedAnswers.some(ra => ra.characteristicId === characteristicId && ra.source === 'remembered')
  }

  // Separate by priority
  const highPriority = allCharacteristics.filter(c => c.priority === 'high')
  const mediumPriority = allCharacteristics.filter(c => c.priority === 'medium')
  const lowPriority = allCharacteristics.filter(c => c.priority === 'low')

  // Show high priority by default, all if expanded
  const visibleCharacteristics = showAll
    ? allCharacteristics
    : highPriority.slice(0, 3)

  const hiddenCount = allCharacteristics.length - visibleCharacteristics.length

  const handleOptionSelect = (characteristic: CharacteristicConfig, optionValue: string) => {
    const currentAnswer = answers[characteristic.id]

    if (characteristic.multiSelect) {
      // Multi-select logic
      const currentValues = Array.isArray(currentAnswer) ? currentAnswer : currentAnswer ? [currentAnswer] : []
      if (currentValues.includes(optionValue)) {
        const newValues = currentValues.filter(v => v !== optionValue)
        if (newValues.length === 0) {
          onClear(characteristic.id)
        } else {
          onAnswer(characteristic.id, newValues)
        }
      } else {
        onAnswer(characteristic.id, [...currentValues, optionValue])
      }
    } else {
      // Single select logic
      if (currentAnswer === optionValue) {
        onClear(characteristic.id)
      } else {
        onAnswer(characteristic.id, optionValue)
      }
    }
  }

  const isSelected = (characteristicId: string, optionValue: string): boolean => {
    const answer = answers[characteristicId]
    if (!answer) return false
    if (Array.isArray(answer)) return answer.includes(optionValue)
    return answer === optionValue
  }

  if (allCharacteristics.length === 0) {
    return null
  }

  return (
    <section className="max-w-[1400px] mx-auto px-10 pb-10">
      {/* Section Header */}
      <div className="mb-6">
        <h2 className="text-[14px] font-bold uppercase tracking-wider mb-2">
          Help us find your perfect {productConfig.categoryDisplayName}
        </h2>
        <p className="text-[11px] text-gray-500">
          Answer a few questions so we can personalize your recommendations
        </p>
      </div>

      {/* Questions */}
      <div className="space-y-6">
        {visibleCharacteristics.map((characteristic) => {
          const hasAnswer = !!answers[characteristic.id]

          return (
            <div
              key={characteristic.id}
              className="bg-white border border-gray-200 rounded-lg p-5 hover:border-gray-300 transition-colors"
            >
              {/* Question Header */}
              <div className="mb-4">
                <div className="flex items-center gap-2 mb-2">
                  <h3 className="text-[13px] font-semibold text-gray-900">
                    {characteristic.question}
                  </h3>
                  {/* Remembered indicator */}
                  {hasAnswer && isRemembered(characteristic.id) && (
                    <span className="text-[9px] px-2 py-0.5 bg-blue-100 text-blue-700 rounded uppercase tracking-wide font-semibold">
                      ✓ From previous search
                    </span>
                  )}
                </div>

                {/* "Why it matters" tooltip */}
                {characteristic.whyItMatters && (
                  <div className="flex items-start gap-2 bg-gray-50 px-3 py-2 rounded">
                    <span className="text-[11px] flex-shrink-0">💡</span>
                    <p className="text-[10px] text-gray-600 leading-relaxed">
                      {characteristic.whyItMatters}
                    </p>
                  </div>
                )}
              </div>

              {/* Options */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {characteristic.options.map((option) => {
                  const selected = isSelected(characteristic.id, option.value)

                  return (
                    <button
                      key={option.value}
                      onClick={() => handleOptionSelect(characteristic, option.value)}
                      className={`relative p-4 rounded-lg border-2 transition-all text-left ${
                        selected
                          ? 'border-black bg-black text-white'
                          : 'border-gray-200 bg-white hover:border-gray-400'
                      }`}
                    >
                      {/* Checkmark for selected */}
                      {selected && (
                        <div className="absolute top-2 right-2 w-5 h-5 bg-white text-black rounded-full flex items-center justify-center text-[10px] font-bold">
                          ✓
                        </div>
                      )}

                      {/* Icon */}
                      {option.icon && (
                        <div className="text-2xl mb-2">{option.icon}</div>
                      )}

                      {/* Label */}
                      <div className={`text-[12px] font-semibold mb-1 ${
                        selected ? 'text-white' : 'text-gray-900'
                      }`}>
                        {option.label}
                      </div>

                      {/* Description */}
                      {option.description && (
                        <div className={`text-[10px] ${
                          selected ? 'text-gray-200' : 'text-gray-500'
                        }`}>
                          {option.description}
                        </div>
                      )}

                      {/* Recommended For */}
                      {option.recommendedFor && option.recommendedFor.length > 0 && (
                        <div className={`text-[9px] mt-2 pt-2 border-t ${
                          selected ? 'border-gray-600 text-gray-300' : 'border-gray-200 text-gray-400'
                        }`}>
                          For: {option.recommendedFor.join(', ')}
                        </div>
                      )}
                    </button>
                  )
                })}
              </div>

              {/* Clear Answer Button */}
              {hasAnswer && (
                <button
                  onClick={() => onClear(characteristic.id)}
                  className="mt-3 text-[10px] text-gray-500 hover:text-black uppercase tracking-wide underline"
                >
                  Clear answer
                </button>
              )}
            </div>
          )
        })}
      </div>

      {/* Show More / Show Less Button */}
      {hiddenCount > 0 && (
        <div className="mt-6 text-center">
          <button
            onClick={() => setShowAll(!showAll)}
            className="text-[11px] uppercase tracking-wide font-semibold text-gray-700 hover:text-black underline"
          >
            {showAll ? 'Show fewer factors' : `Show ${hiddenCount} more factor${hiddenCount !== 1 ? 's' : ''}`}
          </button>
        </div>
      )}

      {/* Answer Count & Reset Button */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        {Object.keys(answers).length > 0 && (
          <p className="text-[11px] text-gray-600 text-center mb-3">
            ✓ You've answered {Object.keys(answers).length} of {allCharacteristics.length} questions
          </p>
        )}

        {/* Reset my preferences button */}
        {onClearAllMemory && rememberedAnswers.length > 0 && (
          <div className="text-center">
            <button
              onClick={() => {
                if (confirm('This will clear all your saved preferences. Are you sure?')) {
                  onClearAllMemory()
                  // Also clear current answers for remembered characteristics
                  allCharacteristics
                    .filter(c => c.rememberAcrossSearches)
                    .forEach(c => onClear(c.id))
                }
              }}
              className="text-[11px] text-gray-500 hover:text-red-600 uppercase tracking-wide underline"
            >
              Reset my preferences
            </button>
          </div>
        )}
      </div>
    </section>
  )
}
