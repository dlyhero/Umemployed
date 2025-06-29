#!/bin/bash

# Build and Package Celery Worker for Manual Upload
# This script creates a Docker image and saves it as a tar file for manual deployment

set -e

IMAGE_NAME="umemployed-celery-worker"
OUTPUT_FILE="celery-worker-$(date +%Y%m%d-%H%M%S).tar"

echo "🐳 Building Celery Worker Docker Image..."

# Build the Docker image
docker build -f Dockerfile.celery -t ${IMAGE_NAME}:latest .

echo "✅ Image built successfully!"

# Save the image to a tar file
echo "📦 Saving image to ${OUTPUT_FILE}..."
docker save ${IMAGE_NAME}:latest > ${OUTPUT_FILE}

# Get file size
FILE_SIZE=$(du -sh ${OUTPUT_FILE} | cut -f1)

echo "✅ Image saved successfully!"
echo ""
echo "📋 Build Summary:"
echo "- Image Name: ${IMAGE_NAME}:latest"
echo "- Output File: ${OUTPUT_FILE}"
echo "- File Size: ${FILE_SIZE}"
echo ""
echo "🚀 Next Steps:"
echo "1. Upload ${OUTPUT_FILE} to your Azure Container Registry or use it directly"
echo "2. For Azure Container Apps, you can:"
echo "   - Upload to ACR: docker load < ${OUTPUT_FILE} && docker tag ${IMAGE_NAME}:latest your-registry.azurecr.io/celery-worker:latest"
echo "   - Push: docker push your-registry.azurecr.io/celery-worker:latest"
echo "   - Deploy: Update your Container App to use the new image"
echo ""
echo "🔧 To load the image later:"
echo "docker load < ${OUTPUT_FILE}"
