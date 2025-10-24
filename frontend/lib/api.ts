import axios from 'axios'
import type { SearchQuery, SearchResponse, Category, ValueMetrics } from '@/types'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 120000, // 2 minutes for AI search
})

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
