#!/bin/bash

# Deploy Celery Worker to Azure Container Registry and Container Instance
# This script will NOT affect your virtual environment

set -e

# Configuration
RESOURCE_GROUP="UmEmployed_RG"
ACR_NAME="celeryworkerumemployed"
LOCATION="canadacentral"
IMAGE_NAME="celery-worker"
CONTAINER_INSTANCE_NAME="umemployed-celery-worker"

echo "🚀 Starting Celery Worker Azure Deployment..."
echo "📋 Configuration:"
echo "  Resource Group: $RESOURCE_GROUP"
echo "  ACR Name: $ACR_NAME"
echo "  Location: $LOCATION"
echo "  Image: $IMAGE_NAME"
echo ""

# Step 1: Check if ACR exists, create if not
echo "🔍 Checking if ACR exists..."
if ! az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo "📦 Creating Azure Container Registry..."
    az acr create \
        --resource-group $RESOURCE_GROUP \
        --name $ACR_NAME \
        --sku Basic \
        --location $LOCATION \
        --admin-enabled true
    echo "✅ ACR created successfully!"
else
    echo "✅ ACR already exists!"
fi

# Step 2: Build and push the image to ACR
echo "🔨 Building and pushing Celery worker image to ACR..."
az acr build \
    --registry $ACR_NAME \
    --image $IMAGE_NAME:latest \
    --file Dockerfile.celery \
    .

echo "✅ Image built and pushed successfully!"

# Step 3: Get ACR credentials
echo "🔑 Getting ACR credentials..."
ACR_SERVER=$(az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query "loginServer" --output tsv)
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query "username" --output tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" --output tsv)

echo "📋 ACR Details:"
echo "  Server: $ACR_SERVER"
echo "  Username: $ACR_USERNAME"
echo ""

# Step 4: Create Container Instance for Celery Worker
echo "🐳 Creating Container Instance for Celery Worker..."

# Delete existing container instance if it exists
if az container show --resource-group $RESOURCE_GROUP --name $CONTAINER_INSTANCE_NAME &> /dev/null; then
    echo "🗑️ Deleting existing container instance..."
    az container delete \
        --resource-group $RESOURCE_GROUP \
        --name $CONTAINER_INSTANCE_NAME \
        --yes
    echo "✅ Existing container deleted!"
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
    "STRIPE_SECRET_KEY" "STRIPE_PUBLISHABLE_KEY"
    "AGORA_APP_ID" "AGORA_APP_CERTIFICATE"
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

# Create new container instance
az container create \
    --resource-group $RESOURCE_GROUP \
    --name $CONTAINER_INSTANCE_NAME \
    --image $ACR_SERVER/$IMAGE_NAME:latest \
    --registry-username $ACR_USERNAME \
    --registry-password $ACR_PASSWORD \
    --cpu 1 \
    --memory 2 \
    --os-type Linux \
    --restart-policy Always \
    --environment-variables \
        DEBUG=0 \
        DJANGO_ALLOWED_HOSTS="*" \
        DB_NAME="$AZURE_DB_NAME" \
        DB_USER="$AZURE_DB_USER" \
        DB_PASSWORD="$AZURE_DB_PASSWORD" \
        DB_HOST="$AZURE_DB_HOST" \
        DB_PORT="$AZURE_DB_PORT" \
        AZURE_DB_NAME="$AZURE_DB_NAME" \
        AZURE_DB_USER="$AZURE_DB_USER" \
        AZURE_DB_PASSWORD="$AZURE_DB_PASSWORD" \
        AZURE_DB_HOST="$AZURE_DB_HOST" \
        AZURE_DB_PORT="$AZURE_DB_PORT" \
        REDIS_URL="$REDIS_URL" \
        REDIS_PASSWORD="$REDIS_PASSWORD" \
        SECRET_KEY="$SECRET_KEY" \
        OPENAI_API_KEY="$OPENAI_API_KEY" \
        GEMINI_API_KEY="$GEMINI_API_KEY" \
        LLAMA_API_KEY="$LLAMA_API_KEY" \
        AZURE_ACCOUNT_NAME="$AZURE_ACCOUNT_NAME" \
        AZURE_ACCOUNT_KEY="$AZURE_ACCOUNT_KEY" \
        AZURE_CONTAINER="$AZURE_CONTAINER" \
        STRIPE_SECRET_KEY="$STRIPE_SECRET_KEY" \
        STRIPE_PUBLISHABLE_KEY="$STRIPE_PUBLISHABLE_KEY" \
        AGORA_APP_ID="$AGORA_APP_ID" \
        AGORA_APP_CERTIFICATE="$AGORA_APP_CERTIFICATE"

echo "✅ Container Instance created successfully!"

# Step 5: Show container status
echo "📊 Container Instance Status:"
az container show \
    --resource-group $RESOURCE_GROUP \
    --name $CONTAINER_INSTANCE_NAME \
    --query "{Name:name,State:containers[0].instanceView.currentState.state,RestartCount:containers[0].instanceView.restartCount}" \
    --output table

echo ""
echo "🎉 Celery Worker deployment completed!"
echo "📋 Summary:"
echo "  ✅ ACR: $ACR_SERVER"
echo "  ✅ Image: $IMAGE_NAME:latest"
echo "  ✅ Container Instance: $CONTAINER_INSTANCE_NAME"
echo ""
echo "🔍 To check logs:"
echo "  az container logs --resource-group $RESOURCE_GROUP --name $CONTAINER_INSTANCE_NAME"
echo ""
echo "🔄 To restart container:"
echo "  az container restart --resource-group $RESOURCE_GROUP --name $CONTAINER_INSTANCE_NAME"
