import { SignJWT } from 'jose'
import { cookies } from 'next/headers'

export interface User {
  userId: string
  email: string
  name?: string
}

/**
 * Create a JWT token for a user
 */
export async function createToken(user: User): Promise<string> {
  const secret = new TextEncoder().encode(
    process.env.JWT_SECRET || 'your-secret-key-change-this-in-production'
  )

  const token = await new SignJWT({
    userId: user.userId,
    email: user.email,
    name: user.name,
  })
    .setProtectedHeader({ alg: 'HS256' })
    .setIssuedAt()
    .setExpirationTime('7d') // Token expires in 7 days
    .sign(secret)

  return token
}

/**
 * Set authentication cookie (server-side only)
 */
export async function setAuthCookie(token: string) {
  const cookieStore = await cookies()

  cookieStore.set('auth_token', token, {
    httpOnly: true, // Cannot be accessed by JavaScript
    secure: process.env.NODE_ENV === 'production', // HTTPS only in production
    sameSite: 'lax', // CSRF protection
    maxAge: 60 * 60 * 24 * 7, // 7 days
    path: '/',
  })
}

/**
 * Clear authentication cookie (server-side only)
 */
export async function clearAuthCookie() {
  const cookieStore = await cookies()
  cookieStore.delete('auth_token')
}

/**
 * Get authentication cookie (server-side only)
 */
export async function getAuthCookie(): Promise<string | undefined> {
  const cookieStore = await cookies()
  return cookieStore.get('auth_token')?.value
}
