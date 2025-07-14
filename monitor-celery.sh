#!/bin/bash

# Monitor Celery Worker and Beat containers
# This script checks the status and logs of your Celery containers

RESOURCE_GROUP="UmEmployed_RG"
CELERY_WORKER_NAME="umemployed-celery-worker"
CELERY_BEAT_NAME="umemployed-celery-beat"

echo "🔍 Celery Containers Monitoring Dashboard"
echo "========================================"
echo ""

# Function to check container status
check_container_status() {
    local container_name=$1
    local display_name=$2
    
    echo "📊 $display_name Status:"
    echo "------------------------"
    
    if az container show --resource-group $RESOURCE_GROUP --name $container_name &> /dev/null; then
        az container show \
            --resource-group $RESOURCE_GROUP \
            --name $container_name \
            --query "{Name:name,State:containers[0].instanceView.currentState.state,RestartCount:containers[0].instanceView.restartCount,CPU:containers[0].resourceRequirements.requests.cpu,Memory:containers[0].resourceRequirements.requests.memoryInGB}" \
            --output table
        
        echo ""
        echo "🏃 Current State Details:"
        az container show \
            --resource-group $RESOURCE_GROUP \
            --name $container_name \
            --query "containers[0].instanceView.currentState" \
            --output table
        echo ""
    else
        echo "❌ Container '$container_name' not found!"
        echo ""
    fi
}

# Function to show recent logs
show_recent_logs() {
    local container_name=$1
    local display_name=$2
    
    echo "📋 $display_name Recent Logs (last 20 lines):"
    echo "--------------------------------------------"
    
    if az container show --resource-group $RESOURCE_GROUP --name $container_name &> /dev/null; then
        az container logs \
            --resource-group $RESOURCE_GROUP \
            --name $container_name \
            --tail 20
        echo ""
    else
        echo "❌ Container '$container_name' not found!"
        echo ""
    fi
}

# Check Celery Worker
check_container_status $CELERY_WORKER_NAME "Celery Worker"

# Check Celery Beat
check_container_status $CELERY_BEAT_NAME "Celery Beat (Scheduler)"

# Show logs if requested
if [[ "$1" == "--logs" ]]; then
    echo "📜 RECENT LOGS"
    echo "=============="
    echo ""
    
    show_recent_logs $CELERY_WORKER_NAME "Celery Worker"
    show_recent_logs $CELERY_BEAT_NAME "Celery Beat"
fi

# Show quick commands
echo "🛠️  Quick Commands:"
echo "==================="
echo ""
echo "View full logs:"
echo "  Worker: az container logs --resource-group $RESOURCE_GROUP --name $CELERY_WORKER_NAME"
echo "  Beat:   az container logs --resource-group $RESOURCE_GROUP --name $CELERY_BEAT_NAME"
echo ""
echo "Restart containers:"
echo "  Worker: az container restart --resource-group $RESOURCE_GROUP --name $CELERY_WORKER_NAME"
echo "  Beat:   az container restart --resource-group $RESOURCE_GROUP --name $CELERY_BEAT_NAME"
echo ""
echo "Monitor with logs: ./monitor-celery.sh --logs"
echo ""
echo "Delete containers:"
echo "  Worker: az container delete --resource-group $RESOURCE_GROUP --name $CELERY_WORKER_NAME --yes"
echo "  Beat:   az container delete --resource-group $RESOURCE_GROUP --name $CELERY_BEAT_NAME --yes"
