#!/bin/bash

# Alternative GitHub Secrets Setup - Manual Azure Service Principal Creation
# Use this when you don't have permissions to create service principals automatically

set -e

REPO_OWNER="dlyhero"
REPO_NAME="Umemployed"

echo "🔐 Manual Azure Service Principal Setup"
echo "======================================"
echo ""
echo "⚠️  You need to ask your Azure administrator to create a service principal"
echo "   OR use your personal Azure credentials as a workaround."
echo ""

# Load environment variables safely (same as before)
if [ -f ".env" ]; then
    echo "🔧 Loading environment variables from .env file..."
    
    while IFS='=' read -r key value; do
        [[ $key =~ ^[[:space:]]*# ]] && continue
        [[ -z $key ]] && continue
        
        key=$(echo "$key" | xargs)
        value=$(echo "$value" | xargs)
        
        if [[ $value =~ ^\".*\"$ ]] || [[ $value =~ ^\'.*\'$ ]]; then
            value="${value:1:-1}"
        fi
        
        export "$key"="$value"
    done < <(grep -v '^[[:space:]]*#' .env | grep -v '^[[:space:]]*$')
    
    echo "✅ Environment variables loaded safely"
else
    echo "❌ .env file not found!"
    exit 1
fi

# Function to set a secret
set_secret() {
    local secret_name=$1
    local secret_value=$2
    local description=$3
    
    echo "🔐 Setting secret: $secret_name"
    echo "   Description: $description"
    
    echo "$secret_value" | gh secret set "$secret_name" --repo "$REPO_OWNER/$REPO_NAME"
    
    if [ $? -eq 0 ]; then
        echo "   ✅ Success!"
    else
        echo "   ❌ Failed to set $secret_name"
        return 1
    fi
    echo ""
}

echo ""
echo "🚀 Setting GitHub Secrets (Application Variables)..."
echo ""

# Set all the application secrets (non-Azure auth)
set_secret "DB_NAME" "$AZURE_DB_NAME" "Azure PostgreSQL database name"
set_secret "DB_USER" "$AZURE_DB_USER" "Azure PostgreSQL username"
set_secret "DB_PASSWORD" "$AZURE_DB_PASSWORD" "Azure PostgreSQL password"
set_secret "DB_HOST" "$AZURE_DB_HOST" "Azure PostgreSQL host"
set_secret "DB_PORT" "$AZURE_DB_PORT" "Azure PostgreSQL port"

set_secret "REDIS_URL" "$REDIS_URL" "Azure Redis Cache URL"
set_secret "REDIS_PASSWORD" "$REDIS_PASSWORD" "Azure Redis Cache password"

set_secret "SECRET_KEY" "$SECRET_KEY" "Django secret key"

set_secret "OPENAI_API_KEY" "$OPENAI_API_KEY" "OpenAI API key"
set_secret "GEMINI_API_KEY" "$GEMINI_API_KEY" "Google Gemini API key"
set_secret "LLAMA_API_KEY" "$LLAMA_API_KEY" "Llama API key"

set_secret "AZURE_ACCOUNT_NAME" "$AZURE_ACCOUNT_NAME" "Azure Storage account name"
set_secret "AZURE_ACCOUNT_KEY" "$AZURE_ACCOUNT_KEY" "Azure Storage account key"
set_secret "AZURE_CONTAINER" "$AZURE_CONTAINER" "Azure Storage container name"

set_secret "STRIPE_SECRET_KEY" "$STRIPE_SECRET_KEY" "Stripe secret key"
set_secret "STRIPE_PUBLISHABLE_KEY" "$STRIPE_PUBLISHABLE_KEY" "Stripe publishable key"

set_secret "AGORA_APP_ID" "$AGORA_APP_ID" "Agora video app ID"
set_secret "AGORA_APP_CERTIFICATE" "$AGORA_APP_CERTIFICATE" "Agora video app certificate"

echo ""
echo "✅ Application secrets set successfully!"
echo ""
echo "🔑 AZURE AUTHENTICATION SETUP NEEDED"
echo "====================================="
echo ""
echo "Option 1: Ask Azure Administrator (Recommended)"
echo "----------------------------------------------"
echo "Ask your Azure admin to create a service principal with these commands:"
echo ""
echo "az ad sp create-for-rbac \\"
echo "  --name 'github-actions-celery-deployment' \\"
echo "  --role contributor \\"
echo "  --scopes /subscriptions/a16d0b75-3385-44d8-8628-a24792118275/resourceGroups/UmEmployed_RG \\"
echo "  --sdk-auth"
echo ""
echo "Then manually set the AZURE_CREDENTIALS secret with the JSON output."
echo ""
echo "Option 2: Use Personal Azure Credentials (Temporary workaround)"
echo "-------------------------------------------------------------"
echo "1. Get your Azure credentials:"
echo "   az account show --sdk-auth"
echo ""
echo "2. Copy the JSON output and manually set it as AZURE_CREDENTIALS secret in GitHub:"
echo "   Go to: https://github.com/$REPO_OWNER/$REPO_NAME/settings/secrets/actions"
echo "   Click 'New repository secret'"
echo "   Name: AZURE_CREDENTIALS"
echo "   Value: [paste the JSON]"
echo ""
echo "Option 3: Manual Deployment Only"
echo "-------------------------------"
echo "Skip GitHub Actions for now and use manual deployment:"
echo "   ./deploy-celery-acr.sh"
echo ""
echo "🎯 Next Steps:"
echo "1. Choose one of the options above to set up AZURE_CREDENTIALS"
echo "2. Then test GitHub Actions by pushing to main branch"
echo "3. Or use manual deployment for now"
