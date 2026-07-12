#!/usr/bin/env bash

# Deploy script for Shadow backend
# This script builds the Docker image, runs it locally for testing,
# and optionally triggers a Render deployment if a RENDER_API_KEY is set.

set -euo pipefail

# Configuration
IMAGE_NAME="shadow-backend"
TAG="latest"
FULL_TAG="${IMAGE_NAME}:${TAG}"

# Build Docker image
echo "Building Docker image ${FULL_TAG}..."
DockerBuildOutput=$(docker build -t ${FULL_TAG} ./backend 2>&1) || {
  echo "Docker build failed:"; echo "$DockerBuildOutput"; exit 1
}

echo "Docker image built successfully."

# Run container locally for quick smoke test (optional)
read -p "Run container locally for smoke test? (y/N): " run_local
if [[ "$run_local" =~ ^[Yy]$ ]]; then
  echo "Starting container..."
  docker run -d --name shadow-backend-test -p 8000:8000 ${FULL_TAG}
  echo "Container started. Waiting 5 seconds for API to start..."
  sleep 5
  echo "Health check:"
  curl -s http://localhost:8000/api/health || echo "Health check failed"
  echo "Stopping and removing test container..."
  docker stop shadow-backend-test && docker rm shadow-backend-test
fi

# Deploy to Render via API (if token provided)
if [[ -z "${RENDER_API_KEY:-}" ]]; then
  echo "RENDER_API_KEY not set. Skipping Render deployment."
else
  # Render API expects JSON payload to create a service or trigger a deploy.
  # Here we assume the repo is already linked to Render and a service exists.
  # Trigger a new deploy:
  echo "Triggering Render deploy..."
  DEPLOY_RESPONSE=$(curl -s -X POST "https://api.render.com/v1/services/<YOUR_SERVICE_ID>/deploys" \
    -H "Authorization: Bearer ${RENDER_API_KEY}" \
    -H "Content-Type: application/json" \
    -d '{}')
  echo "Render response: $DEPLOY_RESPONSE"
fi

echo "Deployment script completed."
