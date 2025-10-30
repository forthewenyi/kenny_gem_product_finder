'use client'

import { useState, useEffect, useCallback } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import type { ContextFilters } from '@/components/ContextFiltersBar'

export function useContextFilters() {
  const searchParams = useSearchParams()
  const router = useRouter()

  // Initialize filters as empty (don't persist across page refreshes)
  const [filters, setFilters] = useState<ContextFilters>({})

  // Clear value_preference from URL on mount if it exists
  useEffect(() => {
    if (searchParams.get('value_preference')) {
      const params = new URLSearchParams(searchParams.toString())
      params.delete('value_preference')
      const newUrl = params.toString() ? `?${params.toString()}` : '/'
      router.replace(newUrl, { scroll: false })
    }
  }, []) // Only run on mount

  // Update filters and URL when filters change
  const updateFilters = useCallback((newFilters: ContextFilters) => {
    setFilters(newFilters)

    // Build new URL with filter params
    const params = new URLSearchParams(searchParams.toString())

    // Remove filter param first
    params.delete('value_preference')

    // Add non-empty filter param
    if (newFilters.value_preference) params.set('value_preference', newFilters.value_preference)

    // Update URL without navigation
    const newUrl = params.toString() ? `?${params.toString()}` : ''
    router.push(newUrl, { scroll: false })
  }, [searchParams, router])

  // Clear all filters
  const clearFilters = useCallback(() => {
    updateFilters({})
  }, [updateFilters])

  // Get filter count
  const filterCount = Object.values(filters).filter(v => v).length

  return {
    filters,
    updateFilters,
    clearFilters,
    filterCount,
  }
}
