#!/bin/bash
#
# Initial setup script for Google Cloud Run deployment
# Creates secrets in Secret Manager and sets up IAM permissions
#
# Run this ONCE before deploying with deploy.sh
#

set -e  # Exit on error

# ============================================================================
# CONFIGURATION
# ============================================================================

PROJECT_ID="${GCP_PROJECT_ID:-your-project-id}"
REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="kenny-gem-finder"

# Service account for Cloud Run
SERVICE_ACCOUNT="${SERVICE_NAME}-sa@${PROJECT_ID}.iam.gserviceaccount.com"

# ============================================================================
# FUNCTIONS
# ============================================================================

create_secret() {
    local secret_name=$1
    local secret_value=$2

    echo "Creating secret: $secret_name"

    # Check if secret already exists
    if gcloud secrets describe "$secret_name" --project="$PROJECT_ID" >/dev/null 2>&1; then
        echo "  ⚠️  Secret already exists. Adding new version..."
        echo "$secret_value" | gcloud secrets versions add "$secret_name" \
            --project="$PROJECT_ID" \
            --data-file=-
    else
        echo "  ✅ Creating new secret..."
        echo "$secret_value" | gcloud secrets create "$secret_name" \
            --project="$PROJECT_ID" \
            --replication-policy="automatic" \
            --data-file=-
    fi

    # Grant access to service account
    gcloud secrets add-iam-policy-binding "$secret_name" \
        --project="$PROJECT_ID" \
        --member="serviceAccount:$SERVICE_ACCOUNT" \
        --role="roles/secretmanager.secretAccessor" \
        >/dev/null 2>&1 || echo "  ℹ️  IAM binding already exists"

    echo "  ✅ Done"
    echo ""
}

# ============================================================================
# MAIN SETUP
# ============================================================================

echo "============================================"
echo "🔐 Kenny Gem Finder - Initial Setup"
echo "============================================"
echo ""
echo "Project: $PROJECT_ID"
echo "Region:  $REGION"
echo ""
echo "This script will:"
echo "  1. Enable required GCP APIs"
echo "  2. Create a service account"
echo "  3. Store secrets in Secret Manager"
echo "  4. Grant necessary IAM permissions"
echo ""

read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "❌ Setup cancelled"
    exit 1
fi

echo ""
echo "📋 Step 1: Enable required APIs..."
echo ""

gcloud services enable run.googleapis.com --project="$PROJECT_ID"
gcloud services enable secretmanager.googleapis.com --project="$PROJECT_ID"
gcloud services enable cloudbuild.googleapis.com --project="$PROJECT_ID"

echo "✅ APIs enabled"
echo ""

echo "📋 Step 2: Create service account..."
echo ""

# Create service account if it doesn't exist
if gcloud iam service-accounts describe "$SERVICE_ACCOUNT" --project="$PROJECT_ID" >/dev/null 2>&1; then
    echo "  ⚠️  Service account already exists"
else
    gcloud iam service-accounts create "${SERVICE_NAME}-sa" \
        --project="$PROJECT_ID" \
        --display-name="Kenny Gem Finder Cloud Run Service Account"
    echo "  ✅ Service account created"
fi

echo ""

echo "📋 Step 3: Store API keys in Secret Manager..."
echo ""
echo "⚠️  You will be prompted to enter your API keys."
echo "    These will be stored SECURELY in Google Secret Manager."
echo "    They will NEVER appear in your code or git history."
echo ""

# Gemini API Key
read -sp "Enter your Gemini API Key: " GEMINI_KEY
echo ""
create_secret "GEMINI_API_KEY" "$GEMINI_KEY"

# Google Search API Key
read -sp "Enter your Google Search API Key: " GOOGLE_SEARCH_KEY
echo ""
create_secret "GOOGLE_SEARCH_API_KEY" "$GOOGLE_SEARCH_KEY"

# Google Search Engine ID
read -p "Enter your Google Search Engine ID: " GOOGLE_SEARCH_ID
create_secret "GOOGLE_SEARCH_ENGINE_ID" "$GOOGLE_SEARCH_ID"

# Portfolio access password
echo ""
echo "📋 Portfolio Access Protection:"
echo "    Set a password to protect your portfolio project."
echo "    Recruiters/viewers will need this to access the demo."
echo ""
read -sp "Enter portfolio access password: " PORTFOLIO_PASSWORD
echo ""
create_secret "PORTFOLIO_ACCESS_PASSWORD" "$PORTFOLIO_PASSWORD"

# JWT Secret Key (auto-generate)
JWT_SECRET=$(openssl rand -hex 32)
create_secret "JWT_SECRET_KEY" "$JWT_SECRET"

echo "============================================"
echo "✅ Setup complete!"
echo "============================================"
echo ""
echo "📋 What was created:"
echo "  - Service account: $SERVICE_ACCOUNT"
echo "  - 5 secrets in Secret Manager"
echo "  - IAM permissions for Secret Manager access"
echo ""
echo "📋 Next steps:"
echo "  1. Review the secrets:"
echo "     gcloud secrets list --project=$PROJECT_ID"
echo ""
echo "  2. Deploy to Cloud Run:"
echo "     cd /path/to/backend"
echo "     ./deploy.sh"
echo ""
echo "🔐 Security Notes:"
echo "  - Your API keys are ONLY stored in Secret Manager"
echo "  - Cloud Run fetches them at runtime"
echo "  - They are NEVER exposed in code or logs"
echo "  - Service account has minimal permissions"
echo ""
echo "💡 To update a secret later:"
echo "   echo 'NEW_VALUE' | gcloud secrets versions add SECRET_NAME --data-file=-"
echo ""
