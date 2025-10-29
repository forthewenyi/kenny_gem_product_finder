import { NextRequest, NextResponse } from 'next/server'
import { createToken, setAuthCookie } from '@/lib/auth'

export async function POST(request: NextRequest) {
  try {
    const { email, password } = await request.json()

    // TODO: Replace with your actual authentication logic
    // This is just an example - you should verify credentials against your database
    if (!email || !password) {
      return NextResponse.json(
        { error: 'Email and password are required' },
        { status: 400 }
      )
    }

    // Example: Verify credentials (replace with your actual logic)
    // const user = await verifyCredentials(email, password)

    // For demonstration purposes, accepting any email/password
    // In production, verify against your backend/database
    const user = {
      userId: 'user123', // Get this from your database
      email: email,
      name: 'John Doe', // Get this from your database
    }

    // Create JWT token
    const token = await createToken(user)

    // Set HTTP-only cookie
    await setAuthCookie(token)

    return NextResponse.json({
      success: true,
      user: {
        email: user.email,
        name: user.name,
      },
    })
  } catch (error) {
    console.error('Login error:', error)
    return NextResponse.json(
      { error: 'Authentication failed' },
      { status: 401 }
    )
  }
}
