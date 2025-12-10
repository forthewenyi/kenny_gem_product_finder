# Google Cloud Run Deployment Guide

**Kenny Gem Finder - Password-Protected Portfolio Project**

This guide walks you through deploying the full-stack Kenny Gem Finder application (Frontend + Backend) to Google Cloud Run as a **single container** with enterprise-grade security and cost controls.

---

## Architecture Overview

### Full-Stack Single Container Deployment

```
┌─────────────┐
│   User      │
└──────┬──────┘
       │
       │ 1. Visit https://your-app.run.app/
       ▼
┌───────────────────────────────────────────────────────────────┐
│   Cloud Run Container (Single Service)                        │
│                                                                │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  Next.js 16 Frontend (Static Export)                 │    │
│  │  - React 19 UI                                        │    │
│  │  - Served from /app/static/                           │    │
│  │  - Client-side routing (SPA)                          │    │
│  │  - index.html, _next/static/*.js, CSS                │    │
│  └──────────────────────────────────────────────────────┘    │
│                       ↓                                        │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  FastAPI Backend (Python + uv)                       │    │
│  │  - Serves static files (/, /login → index.html)      │    │
│  │  - JWT Authentication middleware                     │    │ 2. Login flow
│  │  - /api/auth/login → Get JWT token (public)          │    │
│  │  - /api/search → Protected (requires JWT)            │    │
│  │  - /ws/search-progress → WebSocket (requires JWT)    │    │
│  │  - /health → Health check (public)                   │    │
│  └──────────────────────────────────────────────────────┘    │
└────────┬──────────────────────────────────────────────────────┘
         │
         │ 3. Fetch secrets at runtime
         ▼
┌─────────────────────────────────┐
│   Secret Manager (Vault)        │
│   - GEMINI_API_KEY              │
│   - GOOGLE_SEARCH_API_KEY       │
│   - GOOGLE_SEARCH_ENGINE_ID     │
│   - PORTFOLIO_ACCESS_PASSWORD   │
│   - JWT_SECRET_KEY              │
└─────────────────────────────────┘
         │
         │ 4. Call external APIs
         ▼
┌─────────────────────────────────┐
│   External Services             │
│   - Google Gemini 2.0 Flash     │
│   - Google Custom Search API    │
│   - Google ADK Agents           │
└─────────────────────────────────┘
```

### Multi-Stage Docker Build

The Dockerfile uses a **multi-stage build** with `uv` for faster Python dependency installation:

1. **Stage 1 (Node.js)**: Build Next.js frontend with `.env.production` → static files in `/out`
2. **Stage 2 (Python)**: Install dependencies with `uv sync` + copy static files → single container

**Build Process:**
```dockerfile
# Stage 1: Build frontend
FROM node:20-alpine AS frontend-builder
COPY frontend/ ./
RUN NODE_ENV=production npm run build  # Uses .env.production for config

# Stage 2: Python backend with uv
FROM python:3.11-slim-bookworm
COPY --from=docker.io/astral/uv:latest /uv /uvx /bin/
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-dev  # 10x faster than pip
COPY --from=frontend-builder /frontend/out ./static
CMD exec uv run gunicorn main:app ...
```

**Benefits:**
- ✅ Single URL for frontend + backend (no CORS)
- ✅ Faster builds with `uv` (10x faster than pip)
- ✅ Layer caching for dependencies
- ✅ Production environment variables via `.env.production`
- ✅ Smaller container size (~500MB)

**Why This is Secure:**
- ✅ API keys NEVER in code or `.env` files
- ✅ Secrets stored in Google's encrypted vault
- ✅ JWT authentication on all protected endpoints
- ✅ Cost controls prevent abuse (max 1 instance)
- ✅ JWT tokens expire after 8 hours
- ✅ WebSocket connections require token authentication

---

## Authentication Architecture

### JWT Token-Based Authentication

The application uses **JWT (JSON Web Tokens)** to protect API endpoints from unauthorized access.

#### Authentication Flow

```
1. User visits app → Frontend checks localStorage for token
   ├─ No token? → Redirect to /login
   └─ Has token? → Show home page

2. User enters access code → POST /api/auth/login
   ├─ Wrong password? → 401 Unauthorized
   └─ Correct password? → Return JWT token

3. Frontend stores token in localStorage
   └─ Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

4. All API requests include token
   └─ Authorization: Bearer <token>

5. Backend validates token on every request
   ├─ Invalid/Expired? → 401 Unauthorized → Redirect to /login
   └─ Valid? → Process request
```

#### Protected vs Public Endpoints

| Endpoint | Auth Required | Purpose |
|----------|--------------|---------|
| `GET /` | ❌ Public | Serves frontend (redirects to /login if no token) |
| `GET /login` | ❌ Public | Serves login page |
| `POST /api/auth/login` | ❌ Public | Issues JWT tokens |
| `GET /health` | ❌ Public | Cloud Run health checks |
| `POST /api/search` | ✅ **Protected** | Product search (requires JWT) |
| `GET /api/categories` | ✅ **Protected** | Get categories (requires JWT) |
| `GET /api/popular-searches/{category}` | ✅ **Protected** | Popular searches (requires JWT) |
| `WS /ws/search-progress?token=...` | ✅ **Protected** | Real-time search updates (JWT in query param) |

#### Environment Variables for Authentication

**Development (`.env.local`):**
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000  # Points to local backend
```

**Production (`.env.production`):**
```bash
NEXT_PUBLIC_API_URL=  # Empty = relative URLs (same domain)
```

**Why empty in production?**
- Frontend and backend run on same domain (e.g., `https://your-app.run.app`)
- Empty `baseURL` makes axios use relative paths: `/api/search` → `https://your-app.run.app/api/search`
- Avoids CORS issues and simplifies deployment

#### Client-Side Routing (SPA)

The frontend is a **Single Page Application (SPA)** with client-side routing:

```python
# Backend catch-all route serves index.html for all non-API routes
@app.get("/{full_path:path}")
async def catch_all(request: Request, full_path: str):
    """Enables /login, /about, etc. to work with static export"""
    if full_path.startswith(("api/", "ws/", "health", "_next/")):
        raise HTTPException(status_code=404)
    return FileResponse("static/index.html")  # React Router handles routing
```

This allows routes like `/login` to work even though it's a static export.

#### Security Best Practices

1. **JWT Secret**: Stored in Secret Manager, never in code
2. **Token Expiration**: 8 hours (configurable in `auth_middleware.py`)
3. **HTTPS Only**: Cloud Run enforces TLS for all traffic
4. **No Session Storage**: Stateless authentication (no database needed)
5. **WebSocket Auth**: Token passed as query parameter (`?token=...`)
6. **Auto-Redirect**: 401 responses trigger automatic redirect to login

---

## Prerequisites

### 1. Google Cloud Account
- Create a new GCP project: https://console.cloud.google.com/projectcreate
- Enable billing (required for Cloud Run)
- Note your **Project ID**

### 2. Install gcloud CLI
```bash
# macOS
brew install google-cloud-sdk

# Linux
curl https://sdk.cloud.google.com | bash

# Authenticate
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### 3. API Keys
You'll need these API keys (get them before running setup.sh):

#### Gemini API Key
1. Go to https://makersuite.google.com/app/apikey
2. Create API key
3. Copy the key (starts with `AIza...`)

#### Google Custom Search API
1. Go to https://console.cloud.google.com/apis/credentials
2. Create credentials > API key
3. Restrict to "Custom Search API"
4. Copy the key

#### Google Custom Search Engine ID
1. Go to https://programmablesearchengine.google.com/
2. Create a search engine
3. Get the "Search engine ID" (cx parameter)

---

## Deployment Steps

### Step 1: Initial Setup (One-time)

Run the setup script to create secrets and configure IAM:

```bash
cd backend

# Set your project ID
export GCP_PROJECT_ID="your-project-id"
export GCP_REGION="us-central1"  # or your preferred region

# Run setup (will prompt for API keys)
./setup.sh
```

**What this does:**
- ✅ Enables required GCP APIs (Cloud Run, Secret Manager, Cloud Build)
- ✅ Creates a service account for Cloud Run
- ✅ Prompts you to enter your API keys **securely** (not echoed to terminal)
- ✅ Stores secrets in Secret Manager
- ✅ Grants service account permission to read secrets
- ✅ Generates a random JWT secret

**You will be prompted for:**
1. Gemini API Key
2. Google Search API Key
3. Google Search Engine ID
4. Portfolio access password (what recruiters will use)

---

### Step 2: Deploy to Cloud Run

After setup is complete, deploy the application:

```bash
# Deploy (uses environment variables from Step 1)
./deploy.sh
```

**What this does:**
- ✅ Builds Docker container using Cloud Build
- ✅ Deploys to Cloud Run with cost controls:
  - Max 1 instance (prevents scaling costs)
  - Min 0 instances (scales to zero when idle)
  - 10 concurrent requests per instance
  - 5-minute timeout (for long AI queries)
  - 2GB RAM, 2 vCPUs
- ✅ Connects secrets from Secret Manager as environment variables
- ✅ Makes the service publicly accessible (but password-protected)

**Output:**
```
✅ Deployment complete!
🌐 Service URL: https://kenny-gem-finder-abc123-uc.a.run.app
```

---

## Testing the Deployment

### 1. Access the Frontend

Open your browser and visit the Cloud Run URL:
```
https://kenny-gem-finder-abc123-uc.a.run.app
```

**Expected Behavior:**
1. First visit → Redirects to `/login` (no token in localStorage)
2. Login page displays with single "Access Code" field
3. After entering correct password → JWT token stored in localStorage
4. Redirects to home page → Can now search for products
5. Refresh page → Stays logged in (token persists in localStorage)

**Testing Login Flow:**
```bash
# 1. Visit the site (should redirect to /login)
# 2. Enter access code from Secret Manager
# 3. Click "Access Portfolio"
# 4. Should redirect to home page
# 5. Open DevTools → Application → Local Storage
#    Should see: access_token: eyJhbGc...
```

---

### 2. Health Check (API Endpoint)
```bash
curl https://YOUR_SERVICE_URL/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "environment": "production"
}
```

---

### 3. Test Authentication API

#### Get JWT Token (Login)

```bash
curl -X POST https://YOUR_SERVICE_URL/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"password":"YOUR_PORTFOLIO_PASSWORD"}'
```

**Success Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJncmFudGVkIiwiZXhwIjoxNzY1MzUzMTk4fQ.PECDro4PmCBGLyV1RLe3jpDNmzHiJ5iElfcNcEUnY7s",
  "token_type": "bearer",
  "message": "Access granted. Welcome to Kenny Gem Finder!"
}
```

**Failure Response (wrong password):**
```json
{
  "detail": "Incorrect access code. Please contact portfolio owner for access."
}
```

#### Verify Token

```bash
# Test with valid token
TOKEN="eyJhbGc..."
curl -X GET https://YOUR_SERVICE_URL/api/auth/verify \
  -H "Authorization: Bearer $TOKEN"

# Success: {"access": "granted"}
# Failure: {"detail": "Invalid or expired access code."}
```

---

### 4. Make Authenticated Request

Use the access token to search for products:

```bash
# Save token to variable
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Search for products
curl -X POST https://YOUR_SERVICE_URL/api/search \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "cast iron skillet",
    "max_price": 100
  }'
```

**Success Response:**
```json
{
  "results": {
    "good": [...],
    "better": [...],
    "best": [...]
  },
  "total_products_found": 7,
  "search_query": {
    "query": "cast iron skillet",
    "max_price": 100
  }
}
```

---

## Cost Controls

### Budget Protection

The deployment is configured with strict cost controls:

| Setting | Value | Purpose |
|---------|-------|---------|
| Max Instances | 1 | **Prevents runaway scaling** |
| Min Instances | 0 | Scales to zero when idle (no cost) |
| Concurrency | 10 | Max requests per instance |
| Timeout | 300s | Kills long-running requests |
| Memory | 2GB | Enough for AI, not excessive |

**Expected Costs:**
- **Idle**: $0/month (scales to zero)
- **Light use** (10 searches/day): ~$5-10/month
- **Heavy use** (100 searches/day): ~$20-30/month
- **Max possible**: ~$50/month (1 instance running 24/7)

### Monitoring Costs

```bash
# Check current instances
gcloud run services describe kenny-gem-finder \
  --region us-central1 \
  --format 'value(status.conditions)'

# View logs
gcloud run services logs read kenny-gem-finder \
  --region us-central1 \
  --limit 50

# Set budget alert (recommended)
gcloud billing budgets create \
  --billing-account YOUR_BILLING_ACCOUNT \
  --display-name "Kenny Gem Finder Budget" \
  --budget-amount 50
```

---

## Security Best Practices

### ✅ What Makes This Secure

1. **Secret Manager**: API keys never in code/git
2. **Password Protection**: JWT-based authentication
3. **IAM Permissions**: Service account has minimal permissions
4. **Cost Controls**: Max 1 instance prevents abuse
5. **HTTPS Only**: Cloud Run enforces TLS
6. **No Database**: Stateless app, no user data storage

### 🔐 How Secrets Work

```python
# In your code, secrets are accessed as environment variables
import os
gemini_key = os.getenv("GEMINI_API_KEY")  # ← Fetched from Secret Manager at runtime
```

Cloud Run automatically:
1. Reads secrets from Secret Manager on container startup
2. Injects them as environment variables
3. Keeps them encrypted in memory
4. NEVER logs them

---

## Updating the Deployment

### Update Application Code

```bash
cd backend
./deploy.sh  # Builds new container and deploys
```

### Update a Secret

```bash
# Update Gemini API key
echo "NEW_API_KEY" | gcloud secrets versions add GEMINI_API_KEY --data-file=-

# Update portfolio password
echo "NEW_PASSWORD" | gcloud secrets versions add PORTFOLIO_ACCESS_PASSWORD --data-file=-

# Restart service to pick up new secrets
gcloud run services update kenny-gem-finder --region us-central1
```

---

## Troubleshooting

### Issue: Deployment fails with "permission denied"

**Solution**: Enable APIs and create service account
```bash
gcloud services enable run.googleapis.com secretmanager.googleapis.com
./setup.sh
```

---

### Issue: "Secret not found" error in logs

**Solution**: Verify secrets exist and have correct IAM bindings
```bash
# List secrets
gcloud secrets list

# Check IAM bindings
gcloud secrets get-iam-policy GEMINI_API_KEY
```

---

### Issue: 401 Unauthorized on API requests

**Cause**: Token expired or invalid

**Solution**: Get a new token
```bash
curl -X POST https://YOUR_URL/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"password":"YOUR_PASSWORD"}'
```

---

### Issue: High costs

**Solution**: Check number of instances
```bash
# Should show max 1 instance
gcloud run services describe kenny-gem-finder \
  --region us-central1 \
  --format 'value(spec.template.spec.maxInstanceCount)'

# If not, redeploy with correct settings
./deploy.sh
```

---

## Production Checklist

Before sharing your portfolio:

### Backend & API
- [ ] Test health endpoint returns 200 OK
- [ ] Test login with correct password works
- [ ] Test login with wrong password fails (401)
- [ ] Test authenticated search request works
- [ ] Test unauthenticated search request fails (401)
- [ ] Verify all secrets loaded from Secret Manager (check logs)
- [ ] Verify JWT_SECRET_KEY is set and differs from dev

### Frontend
- [ ] Visit root URL → should redirect to `/login`
- [ ] Login page shows single "Access Code" field (not email)
- [ ] After login → redirects to home page
- [ ] Token stored in localStorage after login
- [ ] Refresh page while logged in → stays logged in
- [ ] WebSocket connection works with token
- [ ] Clear localStorage → redirects back to login

### Infrastructure
- [ ] Verify max instances = 1 in Cloud Run console
- [ ] Verify min instances = 0 (scales to zero)
- [ ] Set up budget alert for $50/month
- [ ] Test that service scales to zero after 15 minutes of inactivity
- [ ] Confirm HTTPS works (no HTTP access)

### Sharing
- [ ] Add Cloud Run URL to your resume/portfolio
- [ ] Share access password with recruiters separately (email, not public)
- [ ] Document that it's a portfolio project (not production)
- [ ] Include tech stack: Next.js 16, FastAPI, Google Gemini, ADK

---

## Cleanup / Tear Down

To delete everything and stop all costs:

```bash
# Delete Cloud Run service
gcloud run services delete kenny-gem-finder --region us-central1

# Delete secrets
gcloud secrets delete GEMINI_API_KEY --quiet
gcloud secrets delete GOOGLE_SEARCH_API_KEY --quiet
gcloud secrets delete GOOGLE_SEARCH_ENGINE_ID --quiet
gcloud secrets delete PORTFOLIO_ACCESS_PASSWORD --quiet
gcloud secrets delete JWT_SECRET_KEY --quiet

# Delete service account
gcloud iam service-accounts delete kenny-gem-finder-sa@PROJECT_ID.iam.gserviceaccount.com
```

---

## Support & Resources

- **Cloud Run Docs**: https://cloud.google.com/run/docs
- **Secret Manager Docs**: https://cloud.google.com/secret-manager/docs
- **Pricing Calculator**: https://cloud.google.com/products/calculator
- **Gemini API**: https://ai.google.dev/docs
- **Google Custom Search**: https://developers.google.com/custom-search

---

**Questions?** Check the main README.md or open an issue on GitHub.
