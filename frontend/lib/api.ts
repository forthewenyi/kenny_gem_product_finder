import axios from 'axios'
import type { SearchQuery, SearchResponse, Category, ValueMetrics } from '@/types'

// Use empty string for production (relative URLs on same domain), localhost for development
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL !== undefined
  ? process.env.NEXT_PUBLIC_API_URL
  : 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 180000, // 3 minutes for comprehensive AI search
})

// Add auth token to all requests
api.interceptors.request.use((config) => {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Redirect to login on 401 errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && typeof window !== 'undefined') {
      localStorage.removeItem('access_token')
      window.location.href = '/login?error=session_expired'
    }
    return Promise.reject(error)
  }
)

export const searchProducts = async (searchQuery: SearchQuery): Promise<SearchResponse> => {
  const { data } = await api.post<SearchResponse>('/api/search', searchQuery)
  return data
}

export const getCategories = async (): Promise<{categories: Category[]}> => {
  const { data } = await api.get('/api/categories')
  return data
}

export const calculateValue = async (
  price: number,
  lifespan: number
): Promise<ValueMetrics> => {
  const { data } = await api.post<ValueMetrics>(
    `/api/calculate-value?price=${price}&lifespan=${lifespan}`
  )
  return data
}

export interface Characteristic {
  label: string
  reason: string
  explanation: string
  image_keyword: string
}

export const generateCharacteristics = async (
  query: string,
  location: string = 'US'
): Promise<{ characteristics: Characteristic[] }> => {
  const { data } = await api.post<{ characteristics: Characteristic[] }>(
    `/api/generate-characteristics?query=${encodeURIComponent(query)}&location=${encodeURIComponent(location)}`
  )
  return data
}

export interface PopularSearchItem {
  term: string
  count: number
}

export const getPopularSearches = async (
  category: 'cookware' | 'knives' | 'bakeware' | 'small_appliances' | 'kitchen_tools',
  limit: number = 8
): Promise<{ category: string; items: PopularSearchItem[] }> => {
  const { data } = await api.get<{ category: string; items: PopularSearchItem[] }>(
    `/api/popular-searches/${category}?limit=${limit}`
  )
  return data
}

export const trackSearch = async (
  query: string,
  category: 'cookware' | 'knives' | 'bakeware' | 'small_appliances' | 'kitchen_tools'
): Promise<{ success: boolean }> => {
  try {
    const { data } = await api.post<{ success: boolean }>(
      `/api/track-search?query=${encodeURIComponent(query)}&category=${category}`
    )
    return data
  } catch (error) {
    // Fire-and-forget - don't block on tracking errors
    console.warn('Failed to track search:', error)
    return { success: false }
  }
}
