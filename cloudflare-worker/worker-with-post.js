/**
 * Cloudflare Worker: API Response Cache (with POST support)
 * Caches JSON API responses for 5 minutes, including POST requests
 *
 * This version supports caching POST requests by creating cache keys
 * based on URL + request body hash
 */

// Cache configuration
const CACHE_DURATION = 300 // 5 minutes in seconds
const CACHE_NAME = 'api-cache-v1'

addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request, event))
})

/**
 * Handle incoming requests with caching logic
 */
async function handleRequest(request, event) {
  const cache = caches.default

  try {
    // Generate cache key (supports both GET and POST)
    const cacheKey = await generateCacheKey(request)

    // Check if we have a cached response
    let response = await cache.match(cacheKey)

    if (response) {
      // Cache hit
      const cachedResponse = new Response(response.body, response)
      cachedResponse.headers.set('X-Cache-Status', 'HIT')
      cachedResponse.headers.set('X-Cached-At', response.headers.get('X-Cached-At') || 'unknown')
      return cachedResponse
    }

    // Cache miss - fetch from origin
    response = await forwardRequest(request)

    // Only cache successful JSON responses
    if (response.ok && response.headers.get('content-type')?.includes('application/json')) {
      // Clone the response to cache it
      const responseToCache = response.clone()

      // Add cache metadata headers
      const headers = new Headers(responseToCache.headers)
      headers.set('Cache-Control', `public, max-age=${CACHE_DURATION}`)
      headers.set('X-Cache-Status', 'MISS')
      headers.set('X-Cached-At', new Date().toISOString())

      // Create response with cache headers
      const cachedResponse = new Response(responseToCache.body, {
        status: responseToCache.status,
        statusText: responseToCache.statusText,
        headers: headers
      })

      // Store in cache (don't await to avoid blocking the response)
      event.waitUntil(cache.put(cacheKey, cachedResponse.clone()))

      return cachedResponse
    }

    // Non-JSON or error response - return without caching
    return response

  } catch (error) {
    console.error('Cache error:', error)
    return forwardRequest(request)
  }
}

/**
 * Generate cache key for the request
 * For POST requests, includes a hash of the request body
 */
async function generateCacheKey(request) {
  const url = new URL(request.url)

  // For GET requests, use URL as cache key
  if (request.method === 'GET') {
    return new Request(url.toString(), { method: 'GET' })
  }

  // For POST requests, include body hash in cache key
  if (request.method === 'POST') {
    const body = await request.clone().text()
    const bodyHash = await hashString(body)

    // Create a unique cache URL with body hash as query parameter
    url.searchParams.set('_body_hash', bodyHash)

    return new Request(url.toString(), { method: 'GET' })
  }

  // For other methods, don't cache
  return request
}

/**
 * Hash a string using SHA-256
 */
async function hashString(str) {
  const buffer = new TextEncoder().encode(str)
  const hashBuffer = await crypto.subtle.digest('SHA-256', buffer)
  const hashArray = Array.from(new Uint8Array(hashBuffer))
  const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('')
  return hashHex.substring(0, 16) // Use first 16 chars for shorter URLs
}

/**
 * Forward request to origin server
 */
async function forwardRequest(request) {
  try {
    const response = await fetch(request)
    return response
  } catch (error) {
    return new Response(
      JSON.stringify({
        error: 'Failed to fetch from origin',
        message: error.message
      }),
      {
        status: 502,
        headers: {
          'Content-Type': 'application/json',
          'X-Cache-Status': 'ERROR'
        }
      }
    )
  }
}
