# Cloudflare Worker: API Response Cache

A Cloudflare Worker that caches JSON API responses for 5 minutes to improve performance and reduce backend load.

## Features

- 5-minute cache duration for JSON responses
- Support for GET requests (worker.js)
- Support for POST requests via body hashing (worker-with-post.js)
- Cache status headers (`X-Cache-Status`, `X-Cached-At`)
- Automatic cache control headers
- Error handling and fallback to origin

## Files

- `worker.js` - Basic worker for GET requests only
- `worker-with-post.js` - Enhanced worker supporting POST request caching
- `wrangler.toml` - Configuration file for deployment

## Cache Headers

The worker adds the following headers to responses:

- `X-Cache-Status`: `HIT`, `MISS`, or `ERROR`
- `X-Cached-At`: Timestamp when the response was cached
- `Cache-Control`: `public, max-age=300` (5 minutes)

## Setup

### 1. Install Wrangler CLI

```bash
npm install -g wrangler
```

### 2. Login to Cloudflare

```bash
wrangler login
```

### 3. Configure the Worker

Edit `wrangler.toml` to set your worker name and routes:

```toml
name = "kenny-gem-finder-api-cache"
main = "worker.js"  # or "worker-with-post.js" for POST support

# For production, configure routes
route = "api.yourdomain.com/*"
zone_name = "yourdomain.com"
```

### 4. Test Locally

```bash
cd cloudflare-worker
wrangler dev
```

This starts a local development server at `http://localhost:8787`

### 5. Deploy to Cloudflare

```bash
wrangler deploy
```

## Usage Examples

### Example 1: GET Request Caching

```bash
# First request (cache MISS)
curl -i https://your-worker.workers.dev/api/products
# X-Cache-Status: MISS

# Second request within 5 minutes (cache HIT)
curl -i https://your-worker.workers.dev/api/products
# X-Cache-Status: HIT
```

### Example 2: POST Request Caching (with worker-with-post.js)

```bash
# Search request
curl -X POST https://your-worker.workers.dev/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "knife"}'
# X-Cache-Status: MISS

# Same search again within 5 minutes
curl -X POST https://your-worker.workers.dev/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "knife"}'
# X-Cache-Status: HIT
```

## Configuration

### Changing Cache Duration

Edit the `CACHE_DURATION` constant in the worker file:

```javascript
const CACHE_DURATION = 300 // 5 minutes in seconds
```

Examples:
- 1 minute: `60`
- 5 minutes: `300`
- 1 hour: `3600`
- 1 day: `86400`

### Adding Custom Routes

You can configure specific routes to cache in `wrangler.toml`:

```toml
# Cache all API routes
route = "api.yourdomain.com/*"

# Or specific endpoints only
route = "yourdomain.com/api/search"
route = "yourdomain.com/api/products"
```

## Integration with Kenny Gem Finder

To use this worker with the Kenny Gem Finder app:

### Option 1: Use as API Proxy

1. Deploy the worker to Cloudflare
2. Configure route: `api.yourdomain.com/*`
3. Update frontend API URL in `.env.local`:

```bash
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

### Option 2: Use Workers Route

1. Deploy worker with route matching your backend
2. Worker automatically intercepts and caches API calls
3. No frontend changes needed

## Performance Benefits

With 5-minute caching:
- First search: ~40-55 seconds (cache MISS)
- Subsequent identical searches: <100ms (cache HIT)
- Reduced backend load by ~99% for repeated queries

## Monitoring

View cache performance in Cloudflare dashboard:
1. Go to Workers & Pages
2. Select your worker
3. View metrics: requests, cache hit rate, errors

## Advanced: Cache Invalidation

To manually clear cache:

```javascript
// Add to worker.js
if (url.searchParams.get('clear_cache') === 'true') {
  await caches.default.delete(cacheKey)
  return new Response('Cache cleared', { status: 200 })
}
```

Then call:
```bash
curl https://your-worker.workers.dev/api/search?clear_cache=true
```

## Troubleshooting

### Cache not working?

1. Check that responses have `Content-Type: application/json`
2. Verify responses return 2xx status codes
3. Check cache headers in response
4. View worker logs: `wrangler tail`

### POST requests not caching?

Use `worker-with-post.js` instead of `worker.js`:

```toml
# In wrangler.toml
main = "worker-with-post.js"
```

## Security Considerations

- Only caches successful (2xx) responses
- Only caches JSON responses
- Cache keys include request URL and body
- HTTP-only (no sensitive data in cache keys)

## License

MIT
