#!/bin/bash
#
# Cloud Run Deployment Diagnostics
# Run this to check if secrets are properly configured
#

set -e

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-your-project-id}"
REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="kenny-gem-finder"

echo "=========================================="
echo "🔍 Cloud Run Deployment Diagnostics"
echo "=========================================="
echo ""
echo "Project: $PROJECT_ID"
echo "Region:  $REGION"
echo "Service: $SERVICE_NAME"
echo ""

# Step 1: Check if secrets exist in Secret Manager
echo "📋 Step 1: Checking Secret Manager..."
echo ""

REQUIRED_SECRETS=(
    "GEMINI_API_KEY"
    "GOOGLE_SEARCH_API_KEY"
    "GOOGLE_SEARCH_ENGINE_ID"
    "PORTFOLIO_ACCESS_PASSWORD"
    "JWT_SECRET_KEY"
)

for secret in "${REQUIRED_SECRETS[@]}"; do
    if gcloud secrets describe "$secret" --project="$PROJECT_ID" >/dev/null 2>&1; then
        echo "  ✅ $secret exists"

        # Check if it has a value
        version_count=$(gcloud secrets versions list "$secret" --project="$PROJECT_ID" --format="value(name)" | wc -l)
        echo "     └─ Versions: $version_count"

        # Get latest version state
        latest_state=$(gcloud secrets versions list "$secret" --project="$PROJECT_ID" --limit=1 --format="value(state)")
        echo "     └─ Latest state: $latest_state"
    else
        echo "  ❌ $secret MISSING - Run setup.sh to create it"
    fi
done

echo ""

# Step 2: Check service account permissions
echo "📋 Step 2: Checking service account permissions..."
echo ""

SERVICE_ACCOUNT="${SERVICE_NAME}-sa@${PROJECT_ID}.iam.gserviceaccount.com"

if gcloud iam service-accounts describe "$SERVICE_ACCOUNT" --project="$PROJECT_ID" >/dev/null 2>&1; then
    echo "  ✅ Service account exists: $SERVICE_ACCOUNT"

    # Check IAM bindings for each secret
    echo ""
    echo "  Checking secret access permissions..."
    for secret in "${REQUIRED_SECRETS[@]}"; do
        if gcloud secrets get-iam-policy "$secret" --project="$PROJECT_ID" --flatten="bindings[].members" --filter="bindings.members:serviceAccount:$SERVICE_ACCOUNT" --format="value(bindings.role)" 2>/dev/null | grep -q "secretAccessor"; then
            echo "    ✅ $secret - Can access"
        else
            echo "    ❌ $secret - NO ACCESS (run setup.sh to fix)"
        fi
    done
else
    echo "  ❌ Service account MISSING - Run setup.sh to create it"
fi

echo ""

# Step 3: Check Cloud Run service configuration
echo "📋 Step 3: Checking Cloud Run service..."
echo ""

if gcloud run services describe "$SERVICE_NAME" --region="$REGION" --project="$PROJECT_ID" >/dev/null 2>&1; then
    echo "  ✅ Service exists: $SERVICE_NAME"
    echo ""

    # Check environment variables
    echo "  Environment variables:"
    gcloud run services describe "$SERVICE_NAME" --region="$REGION" --project="$PROJECT_ID" --format="value(spec.template.spec.containers[0].env)" 2>/dev/null || echo "    (none set)"

    echo ""

    # Check secret bindings
    echo "  Secret bindings:"
    secrets_output=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --project="$PROJECT_ID" --format="json" | grep -A 5 "secretKeyRef" || echo "")

    if [ -z "$secrets_output" ]; then
        echo "    ❌ NO SECRETS MOUNTED"
        echo "    This is the problem! Secrets are not being injected into the container."
        echo ""
        echo "    Fix: Redeploy with deploy.sh to mount secrets"
    else
        echo "    ✅ Secrets are mounted:"
        gcloud run services describe "$SERVICE_NAME" --region="$REGION" --project="$PROJECT_ID" --format="json" | grep -B 2 -A 2 "secretKeyRef" || true
    fi

    echo ""

    # Get service URL
    SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --project="$PROJECT_ID" --format="value(status.url)")
    echo "  Service URL: $SERVICE_URL"

else
    echo "  ❌ Service NOT DEPLOYED - Run deploy.sh to deploy"
fi

echo ""

# Step 4: Test the health endpoint
echo "📋 Step 4: Testing deployed service..."
echo ""

if [ -n "$SERVICE_URL" ]; then
    echo "  Testing health endpoint..."
    if curl -s -f "$SERVICE_URL/health" >/dev/null 2>&1; then
        echo "  ✅ Service is reachable"
        echo ""
        echo "  Response:"
        curl -s "$SERVICE_URL/health" | jq '.' 2>/dev/null || curl -s "$SERVICE_URL/health"
    else
        echo "  ❌ Service is NOT reachable or health check failed"
    fi
else
    echo "  ⚠️  Service URL not found - service may not be deployed"
fi

echo ""
echo "=========================================="
echo "📊 Summary"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. If secrets are missing, run:"
echo "   ./setup.sh"
echo ""
echo "2. If secrets exist but are not mounted, redeploy:"
echo "   ./deploy.sh"
echo ""
echo "3. If service account lacks permissions:"
echo "   Run setup.sh to fix IAM bindings"
echo ""
echo "4. To check Cloud Run logs for errors:"
echo "   gcloud run services logs read $SERVICE_NAME --region=$REGION --limit=50"
echo ""
echo "5. To manually test login (replace PASSWORD with your secret):"
echo "   curl -X POST $SERVICE_URL/api/auth/login \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"password\":\"PASSWORD\"}'"
echo ""
