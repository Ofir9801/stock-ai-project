#!/usr/bin/env bash
# Build the backend/frontend images and push them to the ECR repos created by Terraform.
# Usage: terraform/scripts/push-images.sh [tag]   (tag defaults to "latest")
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TF_DIR="$(dirname "$SCRIPT_DIR")"
ROOT_DIR="$(dirname "$TF_DIR")"
TAG="${1:-latest}"

BACKEND_URL="$(terraform -chdir="$TF_DIR" output -raw ecr_backend_url)"
FRONTEND_URL="$(terraform -chdir="$TF_DIR" output -raw ecr_frontend_url)"
REGISTRY="${BACKEND_URL%%/*}"             # e.g. 123456789.dkr.ecr.us-east-1.amazonaws.com
REGION="$(echo "$REGISTRY" | cut -d. -f4)"

echo ">> Logging in to ECR ($REGISTRY)"
aws ecr get-login-password --region "$REGION" \
  | docker login --username AWS --password-stdin "$REGISTRY"

echo ">> Building images"
docker build -f "$ROOT_DIR/Dockerfile.backend"  -t "$BACKEND_URL:$TAG"  "$ROOT_DIR"
docker build -f "$ROOT_DIR/Dockerfile.frontend" -t "$FRONTEND_URL:$TAG" "$ROOT_DIR"

echo ">> Pushing images"
docker push "$BACKEND_URL:$TAG"
docker push "$FRONTEND_URL:$TAG"

echo ">> Done. Roll the services to pick up the new images:"
CLUSTER="$(terraform -chdir="$TF_DIR" output -raw ecs_cluster)"
echo "   aws ecs update-service --cluster $CLUSTER --service stock-ai-backend  --force-new-deployment --region $REGION"
echo "   aws ecs update-service --cluster $CLUSTER --service stock-ai-frontend --force-new-deployment --region $REGION"
