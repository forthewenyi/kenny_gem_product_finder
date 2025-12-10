#!/bin/bash
#
# Cloud Run Deployment Script for Kenny Gem Finder
# Portfolio project with password protection and Secret Manager integration
#
# Prerequisites:
#   1. Run setup.sh first to create secrets in Secret Manager
#   2. gcloud CLI installed and authenticated
#   3. Docker installed (Cloud Build will use buildpacks)
#

set -e  # Exit on error

# ============================================================================
# CONFIGURATION
# ============================================================================

# Project settings
PROJECT_ID="${GCP_PROJECT_ID:-your-project-id}"
REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="kenny-gem-finder"

# Cost control settings (IMPORTANT for portfolio project)
MAX_INSTANCES=1          # Prevent runaway costs
MIN_INSTANCES=0          # Scale to zero when not in use
CONCURRENCY=10           # Max concurrent requests per instance
TIMEOUT=300              # 5 minutes (for long AI queries)
MEMORY="2Gi"             # 2GB RAM (needed for Gemini AI)
CPU=2                    # 2 vCPUs

# Secret names (must match setup.sh)
GEMINI_API_KEY_SECRET="GEMINI_API_KEY"
GOOGLE_SEARCH_API_KEY_SECRET="GOOGLE_SEARCH_API_KEY"
GOOGLE_SEARCH_ENGINE_ID_SECRET="GOOGLE_SEARCH_ENGINE_ID"
PORTFOLIO_PASSWORD_SECRET="PORTFOLIO_ACCESS_PASSWORD"
JWT_SECRET_KEY_SECRET="JWT_SECRET_KEY"

# Service account (for Secret Manager access)
SERVICE_ACCOUNT="${SERVICE_NAME}-sa@${PROJECT_ID}.iam.gserviceaccount.com"

# ============================================================================
# DEPLOYMENT
# ============================================================================

echo "============================================"
echo "🚀 Deploying Kenny Gem Finder to Cloud Run"
echo "============================================"
echo ""
echo "Project:  $PROJECT_ID"
echo "Region:   $REGION"
echo "Service:  $SERVICE_NAME"
echo ""
echo "Cost Controls:"
echo "  - Max instances: $MAX_INSTANCES (prevents scaling costs)"
echo "  - Min instances: $MIN_INSTANCES (scales to zero when idle)"
echo "  - Concurrency:   $CONCURRENCY requests/instance"
echo "  - Timeout:       ${TIMEOUT}s"
echo "  - Memory:        $MEMORY"
echo ""

# Confirm deployment
read -p "Deploy to Cloud Run? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "❌ Deployment cancelled"
    exit 1
fi

echo ""
echo "📦 Building and deploying..."
echo ""

# Deploy to Cloud Run
# NOTE: We deploy from project root (not backend/) to include frontend in build context
cd "$(dirname "$0")/.." || exit 1
echo "📍 Build context: $(pwd)"
echo ""

gcloud run deploy "$SERVICE_NAME" \
  --source . \
  --project "$PROJECT_ID" \
  --region "$REGION" \
  --platform managed \
  --allow-unauthenticated \
  --service-account "$SERVICE_ACCOUNT" \
  --max-instances "$MAX_INSTANCES" \
  --min-instances "$MIN_INSTANCES" \
  --concurrency "$CONCURRENCY" \
  --timeout "$TIMEOUT" \
  --memory "$MEMORY" \
  --cpu "$CPU" \
  --set-env-vars "ENVIRONMENT=production,CACHE_ENABLED=false,GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GOOGLE_CLOUD_LOCATION=${REGION},GOOGLE_GENAI_USE_VERTEXAI=true" \
  --set-secrets="GOOGLE_API_KEY=${GEMINI_API_KEY_SECRET}:latest" \
  --set-secrets="GOOGLE_SEARCH_API_KEY=${GOOGLE_SEARCH_API_KEY_SECRET}:latest" \
  --set-secrets="GOOGLE_SEARCH_ENGINE_ID=${GOOGLE_SEARCH_ENGINE_ID_SECRET}:latest" \
  --set-secrets="PORTFOLIO_ACCESS_PASSWORD=${PORTFOLIO_PASSWORD_SECRET}:latest" \
  --set-secrets="JWT_SECRET_KEY=${JWT_SECRET_KEY_SECRET}:latest"

echo ""
echo "============================================"
echo "✅ Deployment complete!"
echo "============================================"
echo ""

# Get the service URL
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
  --project "$PROJECT_ID" \
  --region "$REGION" \
  --format 'value(status.url)')

echo "🌐 Service URL: $SERVICE_URL"
echo ""
echo "📋 Next steps:"
echo "  1. Test health endpoint: curl $SERVICE_URL/health"
echo "  2. Get access token:"
echo "     curl -X POST $SERVICE_URL/api/auth/login \\"
echo "       -H 'Content-Type: application/json' \\"
echo "       -d '{\"password\":\"YOUR_PASSWORD\"}'"
echo "  3. Use token in requests:"
echo "     curl -X POST $SERVICE_URL/api/search \\"
echo "       -H 'Authorization: Bearer YOUR_TOKEN' \\"
echo "       -H 'Content-Type: application/json' \\"
echo "       -d '{\"query\":\"cast iron skillet\",\"max_price\":100}'"
echo ""
echo "💰 Cost monitoring:"
echo "   gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.conditions)'"
echo ""
echo "🔐 Security:"
echo "   - Password protected via JWT tokens"
echo "   - Secrets stored in Secret Manager"
echo "   - Max 1 instance prevents abuse"
echo ""
