'use client'

import { Suspense, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import HomePageContent from './HomePageContent'

export default function Home() {
  const router = useRouter()

  useEffect(() => {
    // Check if user is authenticated
    const token = localStorage.getItem('access_token')
    if (!token) {
      // No token, redirect to login
      router.push('/login')
    }
  }, [router])

  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center">Loading...</div>}>
      <HomePageContent />
    </Suspense>
  )
}
