'use client'

import { Suspense, useState, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'

function LoginForm() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const redirect = searchParams.get('redirect') || '/'
  const sessionExpired = searchParams.get('error') === 'session_expired'

  // Check if already logged in
  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (token && !sessionExpired) {
      // Already logged in, redirect to home
      router.push(redirect)
    }
  }, [router, redirect, sessionExpired])

  useEffect(() => {
    if (sessionExpired) {
      setError('Your session has expired. Please enter the access code again.')
    }
  }, [sessionExpired])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      // Use empty string for production (relative URLs on same domain), localhost for development
      const apiUrl = process.env.NEXT_PUBLIC_API_URL !== undefined
        ? process.env.NEXT_PUBLIC_API_URL
        : 'http://localhost:8000'
      const response = await fetch(`${apiUrl}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ password }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Login failed')
      }

      // Store the access token
      if (data.access_token) {
        localStorage.setItem('access_token', data.access_token)
      }

      // Redirect to the intended page or home
      router.push(redirect)
      router.refresh()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <main className="min-h-screen bg-white flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        {/* Logo/Title */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold uppercase tracking-wide mb-2">
            Kenny Gem Finder
          </h1>
          <p className="text-[13px] text-[#79786c] uppercase tracking-wide">
            Enter access code to continue
          </p>
        </div>

        {/* Login Form */}
        <div className="bg-[#f8f8f8] rounded-2xl p-8 shadow-sm">
          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Error Message */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-sm text-red-700">{error}</p>
              </div>
            )}

            {/* Password Input */}
            <div>
              <label
                htmlFor="password"
                className="block text-[13px] font-medium text-gray-700 mb-2 uppercase tracking-wide"
              >
                Access Code
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full px-4 py-3 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent text-[15px]"
                placeholder="Enter access code"
                disabled={isLoading}
                autoFocus
              />
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-black text-white py-3 rounded-lg font-medium text-[15px] uppercase tracking-wide hover:bg-gray-800 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Verifying...' : 'Access Portfolio'}
            </button>
          </form>

          {/* Additional Info */}
          <div className="mt-6 text-center">
            <p className="text-[11px] text-[#79786c]">
              This is a portfolio project. Contact the owner for access.
            </p>
          </div>
        </div>
      </div>
    </main>
  )
}

export default function LoginPage() {
  return (
    <Suspense fallback={
      <main className="min-h-screen bg-white flex items-center justify-center px-4">
        <div className="w-full max-w-md text-center">
          <div className="text-4xl font-bold uppercase tracking-wide mb-2">
            Kenny Gem Finder
          </div>
          <p className="text-[13px] text-[#79786c] uppercase tracking-wide">
            Loading...
          </p>
        </div>
      </main>
    }>
      <LoginForm />
    </Suspense>
  )
}
