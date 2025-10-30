'use client'

import { useState, useEffect, useCallback } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import type { CharacteristicAnswers, CharacteristicAnswer } from '@/types/characteristics'

/**
 * Hook for managing characteristic answers with URL persistence and localStorage memory
 */
export function useCharacteristicAnswers() {
  const searchParams = useSearchParams()
  const router = useRouter()

  // Initialize answers from URL params
  const [answers, setAnswers] = useState<CharacteristicAnswers>(() => {
    const initialAnswers: CharacteristicAnswers = {}

    // Parse all URL params as potential characteristic answers
    searchParams.forEach((value, key) => {
      // Skip known non-characteristic params
      if (['value_preference', 'query', 'max_price'].includes(key)) {
        return
      }

      // Check if it's a multi-select (comma-separated)
      if (value.includes(',')) {
        initialAnswers[key] = value.split(',')
      } else {
        initialAnswers[key] = value
      }
    })

    return initialAnswers
  })

  /**
   * Update a single characteristic answer
   */
  const setAnswer = useCallback((characteristicId: string, value: string | string[]) => {
    setAnswers(prev => ({
      ...prev,
      [characteristicId]: value
    }))
  }, [])

  /**
   * Clear a single characteristic answer
   */
  const clearAnswer = useCallback((characteristicId: string) => {
    setAnswers(prev => {
      const newAnswers = { ...prev }
      delete newAnswers[characteristicId]
      return newAnswers
    })
  }, [])

  /**
   * Clear all characteristic answers
   */
  const clearAllAnswers = useCallback(() => {
    setAnswers({})
  }, [])

  /**
   * Save answers to localStorage for cross-search memory
   */
  const saveAnswersToMemory = useCallback((characteristicIds: string[]) => {
    try {
      const answersToSave: CharacteristicAnswer[] = characteristicIds
        .filter(id => answers[id])
        .map(id => ({
          characteristicId: id,
          value: answers[id],
          timestamp: Date.now(),
          source: 'user_input' as const
        }))

      localStorage.setItem('kenny_characteristic_memory', JSON.stringify(answersToSave))
    } catch (error) {
      console.warn('Failed to save answers to localStorage:', error)
    }
  }, [answers])

  /**
   * Load remembered answers from localStorage
   */
  const loadRememberedAnswers = useCallback((): CharacteristicAnswer[] => {
    try {
      const stored = localStorage.getItem('kenny_characteristic_memory')
      if (stored) {
        return JSON.parse(stored)
      }
    } catch (error) {
      console.warn('Failed to load answers from localStorage:', error)
    }
    return []
  }, [])

  /**
   * Apply remembered answers (but don't override user input)
   */
  const applyRememberedAnswers = useCallback((characteristicIds: string[]) => {
    const remembered = loadRememberedAnswers()
    const newAnswers = { ...answers }

    remembered.forEach((item) => {
      // Only apply if:
      // 1. The characteristic is in the current product config
      // 2. User hasn't already answered it
      if (characteristicIds.includes(item.characteristicId) && !newAnswers[item.characteristicId]) {
        newAnswers[item.characteristicId] = item.value
        // Mark as remembered by updating the source
        item.source = 'remembered'
      }
    })

    setAnswers(newAnswers)
  }, [answers, loadRememberedAnswers])

  /**
   * Sync answers to URL params
   */
  useEffect(() => {
    const params = new URLSearchParams(searchParams.toString())

    // Remove old characteristic params (keep only known params)
    const knownParams = ['value_preference', 'query', 'max_price']
    const paramsToRemove: string[] = []

    params.forEach((_, key) => {
      if (!knownParams.includes(key) && !answers[key]) {
        paramsToRemove.push(key)
      }
    })

    paramsToRemove.forEach(key => params.delete(key))

    // Add current answers
    Object.entries(answers).forEach(([key, value]) => {
      if (Array.isArray(value)) {
        params.set(key, value.join(','))
      } else {
        params.set(key, value)
      }
    })

    // Update URL
    const newUrl = params.toString() ? `?${params.toString()}` : ''
    router.replace(newUrl, { scroll: false })
  }, [answers, searchParams, router])

  /**
   * Get answer count
   */
  const answerCount = Object.keys(answers).length

  /**
   * Check if a characteristic has been answered
   */
  const hasAnswer = useCallback((characteristicId: string): boolean => {
    return !!answers[characteristicId]
  }, [answers])

  /**
   * Get answer for a characteristic
   */
  const getAnswer = useCallback((characteristicId: string): string | string[] | undefined => {
    return answers[characteristicId]
  }, [answers])

  /**
   * Clear all remembered answers from localStorage
   */
  const clearAllMemory = useCallback(() => {
    try {
      localStorage.removeItem('kenny_characteristic_memory')
    } catch (error) {
      console.warn('Failed to clear memory from localStorage:', error)
    }
  }, [])

  return {
    answers,
    setAnswer,
    clearAnswer,
    clearAllAnswers,
    saveAnswersToMemory,
    loadRememberedAnswers,
    applyRememberedAnswers,
    clearAllMemory,
    answerCount,
    hasAnswer,
    getAnswer
  }
}
