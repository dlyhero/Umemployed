#!/bin/bash

# Deploy Celery Beat (Scheduler) to Azure Container Instance
# This handles periodic tasks

set -e

# Configuration
RESOURCE_GROUP="UmEmployed_RG"
ACR_NAME="celeryworkerumemployed"
IMAGE_NAME="celery-beat"
CONTAINER_INSTANCE_NAME="umemployed-celery-beat"

echo "⏰ Starting Celery Beat (Scheduler) Azure Deployment..."
echo "📋 Configuration:"
echo "  Resource Group: $RESOURCE_GROUP"
echo "  ACR Name: $ACR_NAME"
echo "  Image: $IMAGE_NAME"
echo ""

# Step 1: Build and push Celery Beat image to ACR
echo "🔨 Building and pushing Celery Beat image to ACR..."

# Create a temporary Dockerfile for Celery Beat
cat > Dockerfile.celery-beat << 'EOF'
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev gcc python3-dev libmagic1 dnsutils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Celery and django-celery-beat
RUN pip install celery django-celery-beat

# Copy the application code into the container
COPY . .

# Set environment variables
ENV REDIS_SSL_CERT_REQS=none

# Copy and prepare entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set the entrypoint to the entrypoint script
ENTRYPOINT ["/entrypoint.sh"]

# Default command for Celery Beat
CMD ["celery", "-A", "umemployed", "beat", "--loglevel=info", "--scheduler", "django_celery_beat.schedulers:DatabaseScheduler"]
EOF

az acr build \
    --registry $ACR_NAME \
    --image $IMAGE_NAME:latest \
    --file Dockerfile.celery-beat \
    .

# Clean up temporary Dockerfile
rm Dockerfile.celery-beat

echo "✅ Celery Beat image built and pushed successfully!"

# Step 2: Get ACR credentials
echo "🔑 Getting ACR credentials..."
ACR_SERVER=$(az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query "loginServer" --output tsv)
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query "username" --output tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" --output tsv)

# Step 3: Create Container Instance for Celery Beat
echo "⏰ Creating Container Instance for Celery Beat..."

# Delete existing container instance if it exists
if az container show --resource-group $RESOURCE_GROUP --name $CONTAINER_INSTANCE_NAME &> /dev/null; then
    echo "🗑️ Deleting existing Celery Beat container instance..."
    az container delete \
        --resource-group $RESOURCE_GROUP \
        --name $CONTAINER_INSTANCE_NAME \
        --yes
    echo "✅ Existing Celery Beat container deleted!"
fi

# Load environment variables from .env file for local deployment (with safe parsing)
if [ -f ".env" ]; then
    echo "🔧 Loading environment variables from .env file..."
    
    # Use a safer method to load .env that handles special characters
    while IFS='=' read -r key value; do
        # Skip comments and empty lines
        [[ $key =~ ^[[:space:]]*# ]] && continue
        [[ -z $key ]] && continue
        
        # Remove leading/trailing whitespace and quotes
        key=$(echo "$key" | xargs)
        value=$(echo "$value" | xargs)
        
        # Remove quotes if present
        if [[ $value =~ ^\".*\"$ ]] || [[ $value =~ ^\'.*\'$ ]]; then
            value="${value:1:-1}"
        fi
        
        # Export the variable
        export "$key"="$value"
    done < <(grep -v '^[[:space:]]*#' .env | grep -v '^[[:space:]]*$')
    
    echo "   ✅ Environment variables loaded safely"
else
    echo "⚠️  No .env file found. Make sure environment variables are set externally."
fi

# Validate required environment variables
required_vars=(
    "AZURE_DB_NAME" "AZURE_DB_USER" "AZURE_DB_PASSWORD" "AZURE_DB_HOST" "AZURE_DB_PORT"
    "REDIS_URL" "REDIS_PASSWORD" "SECRET_KEY"
    "OPENAI_API_KEY" "GEMINI_API_KEY" "LLAMA_API_KEY"
    "AZURE_ACCOUNT_NAME" "AZURE_ACCOUNT_KEY" "AZURE_CONTAINER"
)

echo "🔍 Validating required environment variables..."
missing_vars=()
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    echo "❌ Missing required environment variables:"
    printf '  - %s\n' "${missing_vars[@]}"
    echo ""
    echo "💡 Make sure to:"
    echo "   1. Have .env file with all variables (for local deployment)"
    echo "   2. Or set them as GitHub Secrets (for automated deployment)"
    exit 1
fi

echo "✅ All environment variables validated!"

# Create new container instance for Celery Beat
az container create \
    --resource-group $RESOURCE_GROUP \
    --name $CONTAINER_INSTANCE_NAME \
    --image $ACR_SERVER/$IMAGE_NAME:latest \
    --registry-username $ACR_USERNAME \
    --registry-password $ACR_PASSWORD \
    --cpu 0.5 \
    --memory 1 \
    --restart-policy Always \
    --environment-variables \
        DEBUG=0 \
        DJANGO_ALLOWED_HOSTS="*" \
        DB_NAME="$AZURE_DB_NAME" \
        DB_USER="$AZURE_DB_USER" \
        DB_PASSWORD="$AZURE_DB_PASSWORD" \
        DB_HOST="$AZURE_DB_HOST" \
        DB_PORT="$AZURE_DB_PORT" \
        REDIS_URL="$REDIS_URL" \
        REDIS_PASSWORD="$REDIS_PASSWORD" \
        SECRET_KEY="$SECRET_KEY" \
        OPENAI_API_KEY="$OPENAI_API_KEY" \
        GEMINI_API_KEY="$GEMINI_API_KEY" \
        LLAMA_API_KEY="$LLAMA_API_KEY" \
        AZURE_ACCOUNT_NAME="$AZURE_ACCOUNT_NAME" \
        AZURE_ACCOUNT_KEY="$AZURE_ACCOUNT_KEY" \
        AZURE_CONTAINER="$AZURE_CONTAINER"

echo "✅ Celery Beat Container Instance created successfully!"

# Step 4: Show container status
echo "📊 Celery Beat Container Instance Status:"
az container show \
    --resource-group $RESOURCE_GROUP \
    --name $CONTAINER_INSTANCE_NAME \
    --query "{Name:name,State:containers[0].instanceView.currentState.state,RestartCount:containers[0].instanceView.restartCount}" \
    --output table

echo ""
echo "🎉 Celery Beat deployment completed!"
echo "📋 Summary:"
echo "  ✅ ACR: $ACR_SERVER"
echo "  ✅ Image: $IMAGE_NAME:latest"
echo "  ✅ Container Instance: $CONTAINER_INSTANCE_NAME"
echo ""
echo "⚠️  IMPORTANT: Make sure to add periodic tasks in Django Admin:"
echo "  1. Go to your Django admin panel"
echo "  2. Navigate to Periodic Tasks section"
echo "  3. Add your scheduled tasks"
echo ""
echo "🔍 To check logs:"
echo "  az container logs --resource-group $RESOURCE_GROUP --name $CONTAINER_INSTANCE_NAME"
