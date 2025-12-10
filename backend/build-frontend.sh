#!/bin/bash
#
# Build frontend and copy static files to backend
# Run this before deploying to Cloud Run
#

set -e  # Exit on error

echo "============================================"
echo "📦 Building Frontend for Production"
echo "============================================"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$SCRIPT_DIR"
FRONTEND_DIR="$(dirname "$BACKEND_DIR")/frontend"
STATIC_DIR="$BACKEND_DIR/static"

echo "Backend dir:  $BACKEND_DIR"
echo "Frontend dir: $FRONTEND_DIR"
echo "Output dir:   $STATIC_DIR"
echo ""

# Check if frontend directory exists
if [ ! -d "$FRONTEND_DIR" ]; then
    echo "❌ Frontend directory not found: $FRONTEND_DIR"
    exit 1
fi

# Navigate to frontend directory
cd "$FRONTEND_DIR"

echo "📋 Step 1: Install dependencies..."
echo ""
npm install

echo ""
echo "📋 Step 2: Build Next.js for production..."
echo ""
NODE_ENV=production npm run build

echo ""
echo "📋 Step 3: Copy static files to backend..."
echo ""

# Remove old static directory
rm -rf "$STATIC_DIR"

# Copy the built files
# Next.js 16 with output: 'export' creates files in /out directory
if [ -d "$FRONTEND_DIR/out" ]; then
    cp -r "$FRONTEND_DIR/out" "$STATIC_DIR"
    echo "✅ Copied Next.js output from /out to $STATIC_DIR"
else
    echo "❌ Next.js output directory not found: $FRONTEND_DIR/out"
    echo "   Make sure next.config.js has output: 'export'"
    exit 1
fi

echo ""
echo "📋 Step 4: Verify build..."
echo ""

if [ -f "$STATIC_DIR/index.html" ]; then
    echo "✅ index.html found"
else
    echo "❌ index.html not found"
    exit 1
fi

if [ -d "$STATIC_DIR/_next" ]; then
    echo "✅ _next directory found (JS bundles)"
    ls -lh "$STATIC_DIR/_next/static" | head -5
else
    echo "❌ _next directory not found"
    exit 1
fi

echo ""
echo "============================================"
echo "✅ Frontend build complete!"
echo "============================================"
echo ""
echo "Static files location: $STATIC_DIR"
echo ""
echo "📋 Next steps:"
echo "  1. Test locally:"
echo "     cd $BACKEND_DIR"
echo "     uvicorn main:app --reload"
echo "     # Visit http://localhost:8000"
echo ""
echo "  2. Deploy to Cloud Run:"
echo "     ./deploy.sh"
echo ""
