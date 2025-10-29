/**
 * Cloudflare Worker: API Response Cache
 * Caches JSON API responses for 5 minutes to improve performance
 */

// Cache configuration
const CACHE_DURATION = 300 // 5 minutes in seconds
const CACHE_NAME = 'api-cache-v1'

/**
 * Main worker fetch handler
 */
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

/**
 * Handle incoming requests with caching logic
 */
async function handleRequest(request) {
  // Only cache GET requests
  if (request.method !== 'GET') {
    return forwardRequest(request)
  }

  // Generate cache key from request URL
  const cacheKey = new Request(request.url, request)
  const cache = caches.default

  try {
    // Check if we have a cached response
    let response = await cache.match(cacheKey)

    if (response) {
      // Cache hit - return cached response with header indicating it's cached
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
    // On error, try to return origin response
    return forwardRequest(request)
  }
}

/**
 * Forward request to origin server
 */
async function forwardRequest(request) {
  try {
    const response = await fetch(request)
    return response
  } catch (error) {
    // Return error response
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
