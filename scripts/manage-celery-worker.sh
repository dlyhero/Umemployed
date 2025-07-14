#!/bin/bash

# Azure Celery Worker Deployment Commands
# Run these commands to manually manage your Celery worker

RESOURCE_GROUP="UmEmployed_RG"
CONTAINER_NAME="celery-worker"
IMAGE_NAME="celeryworkerumemployed.azurecr.io/celery-worker:latest"

echo "🔧 Azure Celery Worker Management Commands"
echo "========================================"

case "$1" in
  "status")
    echo "📊 Checking container status..."
    az container show \
      --resource-group $RESOURCE_GROUP \
      --name $CONTAINER_NAME \
      --query "{name:name,state:containers[0].instanceView.currentState.state,image:containers[0].image,restartCount:containers[0].instanceView.restartCount,startTime:containers[0].instanceView.currentState.startTime}" \
      --output table
    ;;
    
  "logs")
    echo "📋 Fetching container logs..."
    az container logs \
      --resource-group $RESOURCE_GROUP \
      --name $CONTAINER_NAME \
      --follow
    ;;
    
  "restart")
    echo "🔄 Restarting container..."
    az container restart \
      --resource-group $RESOURCE_GROUP \
      --name $CONTAINER_NAME
    echo "✅ Container restarted"
    ;;
    
  "delete")
    echo "🗑️ Deleting container..."
    az container delete \
      --resource-group $RESOURCE_GROUP \
      --name $CONTAINER_NAME \
      --yes
    echo "✅ Container deleted"
    ;;
    
  "deploy")
    echo "🚀 Creating new container..."
    echo "⚠️  Make sure you have all environment variables set!"
    echo "Set these environment variables first:"
    echo "export AZURE_DB_NAME=your_db_name"
    echo "export AZURE_DB_USER=your_db_user"
    echo "export AZURE_DB_PASSWORD=your_db_password"
    echo "export AZURE_DB_HOST=your_db_host"
    echo "export REDIS_URL=your_redis_url"
    echo "export SECRET_KEY=your_secret_key"
    echo ""
    read -p "Continue with deployment? (y/N): " confirm
    if [[ $confirm =~ ^[Yy]$ ]]; then
      az container create \
        --resource-group $RESOURCE_GROUP \
        --name $CONTAINER_NAME \
        --image $IMAGE_NAME \
        --registry-login-server celeryworkerumemployed.azurecr.io \
        --restart-policy Always \
        --cpu 1 \
        --memory 1.5 \
        --command-line "celery -A umemployed worker --loglevel=info --concurrency=2" \
        --environment-variables \
          DJANGO_SETTINGS_MODULE=umemployed.settings \
          AZURE_DB_NAME="$AZURE_DB_NAME" \
          AZURE_DB_USER="$AZURE_DB_USER" \
          AZURE_DB_PASSWORD="$AZURE_DB_PASSWORD" \
          AZURE_DB_HOST="$AZURE_DB_HOST" \
          AZURE_DB_PORT="5432" \
          REDIS_URL="$REDIS_URL" \
          SECRET_KEY="$SECRET_KEY" \
          DEBUG=False \
          REDIS_SSL_CERT_REQS=none
      echo "✅ Container deployed"
    else
      echo "❌ Deployment cancelled"
    fi
    ;;
    
  *)
    echo "Usage: $0 {status|logs|restart|delete|deploy}"
    echo ""
    echo "Commands:"
    echo "  status  - Show container status"
    echo "  logs    - Show container logs (follow mode)"
    echo "  restart - Restart the container"
    echo "  delete  - Delete the container"
    echo "  deploy  - Deploy new container (manual)"
    echo ""
    echo "Examples:"
    echo "  $0 status"
    echo "  $0 logs"
    echo "  $0 restart"
    ;;
esac
