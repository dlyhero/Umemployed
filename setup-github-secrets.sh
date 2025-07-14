#!/bin/bash

# GitHub Secrets Setup for Celery Deployment
# This script helps you set up all required GitHub secrets securely

set -e

REPO_OWNER="dlyhero"  # Replace with your GitHub username
REPO_NAME="Umemployed"         # Replace with your repository name

echo "🔐 GitHub Secrets Setup for Celery Deployment"
echo "=============================================="
echo ""
echo "⚠️  IMPORTANT: Replace REPO_OWNER and REPO_NAME in this script first!"
echo "    Current values: $REPO_OWNER/$REPO_NAME"
echo ""

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI is not installed!"
    echo "📥 Install it with:"
    echo "   sudo apt update && sudo apt install gh"
    echo "   or visit: https://cli.github.com/"
    exit 1
fi

# Check if user is logged in to GitHub CLI
if ! gh auth status &> /dev/null; then
    echo "🔑 Please login to GitHub CLI first:"
    echo "   gh auth login"
    exit 1
fi

echo "✅ GitHub CLI is ready!"
echo ""

# Function to set a secret
set_secret() {
    local secret_name=$1
    local secret_value=$2
    local description=$3
    
    echo "🔐 Setting secret: $secret_name"
    echo "   Description: $description"
    
    # Use GitHub CLI to set the secret
    echo "$secret_value" | gh secret set "$secret_name" --repo "$REPO_OWNER/$REPO_NAME"
    
    if [ $? -eq 0 ]; then
        echo "   ✅ Success!"
    else
        echo "   ❌ Failed to set $secret_name"
        return 1
    fi
    echo ""
}

echo "📋 Setting up secrets from your .env file..."
echo ""

# Load environment variables from .env (with safe parsing)
if [ -f ".env" ]; then
    echo "✅ Found .env file, loading variables safely..."
    
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
        echo "   Loaded: $key"
    done < <(grep -v '^[[:space:]]*#' .env | grep -v '^[[:space:]]*$')
    
    echo "✅ Environment variables loaded safely"
else
    echo "❌ .env file not found!"
    exit 1
fi

echo ""
echo "🚀 Setting GitHub Secrets..."
echo ""

# Set all the secrets
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

echo "🔐 Now setting up Azure service principal for authentication..."
echo ""

# Azure Service Principal setup
echo "Creating Azure service principal for GitHub Actions..."

# Get subscription ID
SUBSCRIPTION_ID=$(az account show --query id --output tsv)
echo "📋 Subscription ID: $SUBSCRIPTION_ID"

# Create service principal
SP_OUTPUT=$(az ad sp create-for-rbac \
    --name "github-actions-celery-deployment" \
    --role contributor \
    --scopes /subscriptions/$SUBSCRIPTION_ID/resourceGroups/UmEmployed_RG \
    --sdk-auth)

echo "🔑 Service principal created!"

# Set Azure credentials secret
set_secret "AZURE_CREDENTIALS" "$SP_OUTPUT" "Azure service principal credentials for GitHub Actions"

echo ""
echo "🎉 All secrets have been set up successfully!"
echo ""
echo "📋 Summary of secrets configured:"
echo "  ✅ Database credentials (DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)"
echo "  ✅ Redis credentials (REDIS_URL, REDIS_PASSWORD)"
echo "  ✅ Django secret key (SECRET_KEY)"
echo "  ✅ API keys (OPENAI, GEMINI, LLAMA)"
echo "  ✅ Azure Storage (AZURE_ACCOUNT_NAME, AZURE_ACCOUNT_KEY, AZURE_CONTAINER)"
echo "  ✅ Stripe credentials (STRIPE_SECRET_KEY, STRIPE_PUBLISHABLE_KEY)"
echo "  ✅ Agora video (AGORA_APP_ID, AGORA_APP_CERTIFICATE)"
echo "  ✅ Azure authentication (AZURE_CREDENTIALS)"
echo ""
echo "🚀 Your GitHub Actions workflow is now ready!"
echo "   Push to main/master branch to trigger automatic deployment"
echo ""
echo "🔍 Check your secrets at:"
echo "   https://github.com/$REPO_OWNER/$REPO_NAME/settings/secrets/actions"

