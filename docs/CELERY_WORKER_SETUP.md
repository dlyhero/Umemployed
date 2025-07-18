# 🔧 Celery Worker Environment Setup Guide

## Current Status: Container Created via Portal ❌

Your container was created via Azure Portal without proper configuration. Here's how to fix it:

## ⚡ Quick Fix - Delete and Recreate

### Step 1: Delete Current Container
```bash
az container delete --resource-group UmEmployed_RG --name celery-worker --yes
```

### Step 2: Get Required Environment Values

#### Database Credentials:
```bash
# Check your current Azure Database settings
az postgres server show --resource-group UmEmployed_RG --name <your-postgres-server>
```

#### Redis Credentials:
```bash
# If using Azure Redis Cache
az redis show --resource-group UmEmployed_RG --name <your-redis-name>
az redis list-keys --resource-group UmEmployed_RG --name <your-redis-name>
```

#### Secret Key:
```bash
# Generate a new Django secret key
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

### Step 3: Set GitHub Secrets

Go to your repository: `Settings > Secrets and variables > Actions`

Add these secrets:
- `ACR_USERNAME` - Your container registry username
- `ACR_PASSWORD` - Your container registry password  
- `AZURE_CREDENTIALS` - Service principal JSON
- `AZURE_DB_NAME` - PostgreSQL database name
- `AZURE_DB_USER` - PostgreSQL username
- `AZURE_DB_PASSWORD` - PostgreSQL password
- `AZURE_DB_HOST` - PostgreSQL host
- `AZURE_DB_PORT` - PostgreSQL port (usually 5432)
- `REDIS_URL` - Redis connection string
- `SECRET_KEY` - Django secret key
- `SOCIAL_AUTH_GOOGLE_OAUTH_KEY` - Google OAuth client ID
- `SOCIAL_AUTH_GOOGLE_OAUTH_SECRET` - Google OAuth secret

### Step 4: Test Deployment

Push a change to trigger the workflow:

```bash
# Make a small change to trigger deployment
echo "# Trigger deployment $(date)" >> README.md
git add README.md
git commit -m "Trigger Celery worker deployment"
git push origin main
```

## 🔍 Troubleshooting

### Check Container Logs:
```bash
./scripts/manage-celery-worker.sh logs
```

### Check Container Status:
```bash
./scripts/manage-celery-worker.sh status
```

### Manual Restart:
```bash
./scripts/manage-celery-worker.sh restart
```

## 🎯 Expected Celery Worker Behavior

When properly configured, your Celery worker should:

1. **Connect to Redis** - For task queue
2. **Connect to PostgreSQL** - For Django models
3. **Process tasks** from these modules:
   - `resume.tasks` - Resume enhancement tasks
   - `job.tasks` - Job-related background tasks  
   - `users.tasks` - User management tasks
   - `messaging.tasks` - Message processing tasks

## 📊 Monitoring

### View Active Tasks:
```bash
# From your main app, check Celery status
celery -A umemployed inspect active
celery -A umemployed inspect registered
```

### Check Redis Connection:
```bash
# Test Redis connection
redis-cli -u "$REDIS_URL" ping
```

## 🚀 Automatic Deployment Triggers

Your workflow triggers on changes to:
- `resume/tasks.py`
- `resume/models.py` 
- `job/tasks.py`
- `users/tasks.py`
- `messaging/tasks.py`
- `Dockerfile.celery`
- `requirements.txt`
- `umemployed/celery.py`
- `umemployed/settings.py`

## ⚠️ Important Notes

1. **Container Resources**: 1 CPU, 1.5GB RAM with concurrency=2
2. **SSL Requirements**: Redis SSL cert requirements disabled for Azure
3. **Restart Policy**: Always restart on failure
4. **Image Updates**: Auto-pulls latest image on deployment

## 🔗 Related Files

- Main workflow: `.github/workflows/azure-acr-build.yml`
- Docker config: `Dockerfile.celery`
- Celery config: `umemployed/celery.py`
- Management script: `scripts/manage-celery-worker.sh`
