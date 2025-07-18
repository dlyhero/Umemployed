#!/bin/bash

# Azure Deployment Troubleshooting Script
# This script helps diagnose and fix common Azure deployment issues

set -e

echo "🔍 Azure Deployment Troubleshooting Script"
echo "=========================================="

# Configuration
APP_NAME="umemployed"
RESOURCE_GROUP="UmEmployed_RG"
SUBSCRIPTION_ID=$(az account show --query id --output tsv)

echo "📋 Current Configuration:"
echo "  App Name: $APP_NAME"
echo "  Resource Group: $RESOURCE_GROUP"
echo "  Subscription: $SUBSCRIPTION_ID"
echo ""

# Function to check Azure CLI login
check_azure_login() {
    echo "🔐 Checking Azure CLI login status..."
    if az account show &> /dev/null; then
        echo "✅ Azure CLI is logged in"
        echo "   Account: $(az account show --query user.name --output tsv)"
        echo "   Subscription: $(az account show --query name --output tsv)"
    else
        echo "❌ Azure CLI is not logged in"
        echo "   Run: az login"
        exit 1
    fi
    echo ""
}

# Function to check app service status
check_app_service() {
    echo "🌐 Checking App Service status..."
    if az webapp show --name $APP_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
        echo "✅ App Service exists"
        
        # Get app service details
        STATE=$(az webapp show --name $APP_NAME --resource-group $RESOURCE_GROUP --query state --output tsv)
        KIND=$(az webapp show --name $APP_NAME --resource-group $RESOURCE_GROUP --query kind --output tsv)
        SKU=$(az webapp show --name $APP_NAME --resource-group $RESOURCE_GROUP --query sku.name --output tsv)
        
        echo "   State: $STATE"
        echo "   Kind: $KIND"
        echo "   SKU: $SKU"
        
        # Check if app service is running
        if [ "$STATE" = "Running" ]; then
            echo "✅ App Service is running"
        else
            echo "⚠️  App Service is not running (State: $STATE)"
            echo "   Consider restarting: az webapp restart --name $APP_NAME --resource-group $RESOURCE_GROUP"
        fi
    else
        echo "❌ App Service does not exist"
        echo "   Create it first or check the resource group"
    fi
    echo ""
}

# Function to check deployment slots
check_deployment_slots() {
    echo "📦 Checking deployment slots..."
    SLOTS=$(az webapp deployment slot list --name $APP_NAME --resource-group $RESOURCE_GROUP --query "[].name" --output tsv 2>/dev/null || echo "production")
    
    for slot in $SLOTS; do
        echo "   Slot: $slot"
        
        # Check slot status
        SLOT_STATE=$(az webapp show --name $APP_NAME --resource-group $RESOURCE_GROUP --slot $slot --query state --output tsv 2>/dev/null || echo "unknown")
        echo "   State: $SLOT_STATE"
        
        # Check recent deployments
        echo "   Recent deployments:"
        az webapp deployment list --name $APP_NAME --resource-group $RESOURCE_GROUP --slot $slot --query "[0:3].[id,status,message]" --output table 2>/dev/null || echo "   No deployments found"
    done
    echo ""
}

# Function to check for deployment conflicts
check_deployment_conflicts() {
    echo "⚠️  Checking for deployment conflicts..."
    
    # Check if there are any ongoing deployments
    ONGOING_DEPLOYMENTS=$(az webapp deployment list --name $APP_NAME --resource-group $RESOURCE_GROUP --query "[?status=='InProgress'].id" --output tsv 2>/dev/null || echo "")
    
    if [ -n "$ONGOING_DEPLOYMENTS" ]; then
        echo "❌ Found ongoing deployments:"
        echo "$ONGOING_DEPLOYMENTS"
        echo "   Wait for these to complete or cancel them"
    else
        echo "✅ No ongoing deployments found"
    fi
    
    # Check deployment logs for recent errors
    echo "📋 Recent deployment logs:"
    az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP --provider docker 2>/dev/null | head -20 || echo "   No recent logs available"
    echo ""
}

# Function to check app service configuration
check_app_service_config() {
    echo "⚙️  Checking App Service configuration..."
    
    # Check Python version
    PYTHON_VERSION=$(az webapp config show --name $APP_NAME --resource-group $RESOURCE_GROUP --query "linuxFxVersion" --output tsv 2>/dev/null || echo "unknown")
    echo "   Python Version: $PYTHON_VERSION"
    
    # Check startup command
    STARTUP_COMMAND=$(az webapp config show --name $APP_NAME --resource-group $RESOURCE_GROUP --query "appCommandLine" --output tsv 2>/dev/null || echo "default")
    echo "   Startup Command: $STARTUP_COMMAND"
    
    # Check environment variables
    echo "   Environment Variables:"
    az webapp config appsettings list --name $APP_NAME --resource-group $RESOURCE_GROUP --query "[?name=='WEBSITES_ENABLE_APP_SERVICE_STORAGE'].{Name:name,Value:value}" --output table 2>/dev/null || echo "   No custom storage settings"
    echo ""
}

# Function to provide solutions
provide_solutions() {
    echo "🔧 Common Solutions for Deployment Issues:"
    echo "=========================================="
    echo ""
    echo "1. **Restart App Service** (if stuck):"
    echo "   az webapp restart --name $APP_NAME --resource-group $RESOURCE_GROUP"
    echo ""
    echo "2. **Clear deployment cache** (if conflicts persist):"
    echo "   az webapp deployment source config-zip --name $APP_NAME --resource-group $RESOURCE_GROUP --src /dev/null"
    echo ""
    echo "3. **Check deployment logs**:"
    echo "   az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP"
    echo ""
    echo "4. **Verify publish profile**:"
    echo "   - Go to Azure Portal → App Service → Get publish profile"
    echo "   - Update GitHub secret: AZUREAPPSERVICE_PUBLISHPROFILE_*"
    echo ""
    echo "5. **Force deployment** (if needed):"
    echo "   - Delete the app service and recreate it"
    echo "   - Or use a different deployment slot"
    echo ""
    echo "6. **Check resource limits**:"
    echo "   - Verify App Service Plan limits"
    echo "   - Check if you've hit deployment quotas"
    echo ""
}

# Function to fix common issues
fix_common_issues() {
    echo "🛠️  Attempting to fix common issues..."
    echo ""
    
    # Restart app service if it's not running
    STATE=$(az webapp show --name $APP_NAME --resource-group $RESOURCE_GROUP --query state --output tsv 2>/dev/null || echo "unknown")
    if [ "$STATE" != "Running" ]; then
        echo "🔄 Restarting App Service..."
        az webapp restart --name $APP_NAME --resource-group $RESOURCE_GROUP
        echo "✅ App Service restarted"
        echo "   Wait 30 seconds for it to fully start..."
        sleep 30
    fi
    
    # Clear any stuck deployments
    echo "🧹 Clearing deployment cache..."
    az webapp deployment source config-zip --name $APP_NAME --resource-group $RESOURCE_GROUP --src /dev/null 2>/dev/null || echo "   No cache to clear"
    echo "✅ Deployment cache cleared"
    echo ""
}

# Main execution
main() {
    check_azure_login
    check_app_service
    check_deployment_slots
    check_deployment_conflicts
    check_app_service_config
    provide_solutions
    
    echo "🤔 Would you like to attempt automatic fixes? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        fix_common_issues
        echo "✅ Automatic fixes completed"
        echo "   Try deploying again now"
    fi
    
    echo ""
    echo "📞 If issues persist, check:"
    echo "   - GitHub Actions logs for detailed error messages"
    echo "   - Azure Portal → App Service → Logs"
    echo "   - Azure Portal → App Service → Deployment Center"
}

# Run main function
main 