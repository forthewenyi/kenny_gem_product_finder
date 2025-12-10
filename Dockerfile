# ============================================================================
# Stage 1: Build Frontend (Next.js)
# ============================================================================
FROM node:20-alpine AS frontend-builder

WORKDIR /frontend

# Copy frontend package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci

# Copy frontend source code
COPY frontend/ ./

# Build Next.js for production (static export)
# .env.production file sets NEXT_PUBLIC_API_URL="" for relative URLs
RUN NODE_ENV=production npm run build

# ============================================================================
# Stage 2: Build Backend (Python + Frontend Static Files)
# ============================================================================
FROM python:3.11-slim-bookworm

# Copy uv from the official image
COPY --from=docker.io/astral/uv:latest /uv /uvx /bin/

# Set working directory in container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy pyproject.toml and uv.lock for dependency installation
COPY backend/pyproject.toml backend/uv.lock ./

# Install Python dependencies using uv
RUN uv sync --frozen --no-dev

# Copy backend application code
COPY backend/ .

# Copy frontend build from stage 1
COPY --from=frontend-builder /frontend/out ./static

# Verify frontend files copied correctly
RUN ls -la /app/static && \
    test -f /app/static/index.html || (echo "ERROR: Frontend index.html not found" && exit 1)

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PORT=8080 \
    ENVIRONMENT=production

# Expose port (Cloud Run uses PORT env variable)
EXPOSE 8080

# Run the application with Gunicorn for production
# Use 1 worker to control costs, timeout of 300s for long-running AI queries
CMD exec uv run gunicorn main:app \
    --bind :$PORT \
    --workers 1 \
    --threads 4 \
    --timeout 300 \
    --worker-class uvicorn.workers.UvicornWorker \
    --access-logfile - \
    --error-logfile -
