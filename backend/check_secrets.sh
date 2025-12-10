#!/bin/bash
#
# Quick script to check what password is stored in Secret Manager
# This helps debug 401 errors when the entered password doesn't match
#

set -e

PROJECT_ID="${GCP_PROJECT_ID:-your-project-id}"

echo "=========================================="
echo "🔐 Secret Manager Values"
echo "=========================================="
echo ""
echo "⚠️  WARNING: This will display your secrets in plain text!"
echo "    Only run this in a secure environment."
echo ""

read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "❌ Cancelled"
    exit 1
fi

echo ""
echo "Project: $PROJECT_ID"
echo ""

# Check PORTFOLIO_ACCESS_PASSWORD
echo "📋 PORTFOLIO_ACCESS_PASSWORD:"
if gcloud secrets versions access latest --secret="PORTFOLIO_ACCESS_PASSWORD" --project="$PROJECT_ID" 2>/dev/null; then
    echo ""
else
    echo "  ❌ Secret not found or you don't have access"
fi

echo ""

# Check JWT_SECRET_KEY (just show length for security)
echo "📋 JWT_SECRET_KEY:"
if jwt_secret=$(gcloud secrets versions access latest --secret="JWT_SECRET_KEY" --project="$PROJECT_ID" 2>/dev/null); then
    echo "  Length: ${#jwt_secret} characters"
    echo "  First 10 chars: ${jwt_secret:0:10}..."
else
    echo "  ❌ Secret not found or you don't have access"
fi

echo ""
echo "=========================================="
echo ""
echo "💡 To update the password:"
echo "   echo 'NEW_PASSWORD' | gcloud secrets versions add PORTFOLIO_ACCESS_PASSWORD --project=$PROJECT_ID --data-file=-"
echo ""
echo "💡 After updating, redeploy Cloud Run:"
echo "   ./deploy.sh"
echo ""
