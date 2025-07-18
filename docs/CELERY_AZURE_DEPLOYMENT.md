# 🚀 Celery Azure Deployment Guide

## Overview
This guide helps you deploy your Celery worker and beat scheduler to Azure Container Registry (ACR) and Azure Container Instances (ACI).

## 📋 Prerequisites
- Azure CLI installed and logged in
- Your virtual environment activated (we won't deactivate it!)
- Resource Group: `UmEmployed_RG`
- ACR Name: `celeryworkerumemployed`

## 🚀 Automated Deployment with GitHub Actions

### Why GitHub Actions?
Manual deployments are slow and time-consuming. With GitHub Actions, your Celery containers are automatically built and deployed every time you push code changes to GitHub!

### 🔧 One-Time Setup

#### 1. Set Up GitHub Repository Secrets
```bash
# First, edit the script to add your GitHub username and repo name
nano scripts/deployment/setup-github-secrets.sh

# Then run the script to set up all secrets securely
chmod +x scripts/deployment/setup-github-secrets.sh
./scripts/deployment/setup-github-secrets.sh
```

This script will:
- ✅ Create Azure service principal for GitHub Actions
- ✅ Set up all environment variables as GitHub secrets
- ✅ Configure authentication credentials

#### 2. GitHub Workflow Configuration
The workflow file `.github/workflows/deploy-celery.yml` is already created and will:
- ✅ Build images only when relevant files change
- ✅ Push to ACR with commit SHA tags for versioning
- ✅ Deploy both Celery Worker and Beat containers
- ✅ Verify deployment and show logs

### 🎯 Automatic Triggers

The workflow triggers on:
- **Push to main/master branch** when these files change:
  - `Dockerfile.celery`
  - `requirements.txt`
  - Any Python files in `umemployed/`, `job/`, `messaging/`, `resume/`, `users/`
  - The workflow file itself
- **Manual trigger** from GitHub Actions tab

### 🔐 Security Best Practices

✅ **Environment variables are stored as GitHub Secrets**
✅ **Azure credentials use service principal (least privilege)**
✅ **Passwords are masked in logs**
✅ **No secrets in code or Docker images**
✅ **Local .env file for development (gitignored)**
✅ **Variable validation before deployment**

📋 **See `SECURITY_IMPROVEMENTS.md` for detailed security analysis**

### 📊 Deployment Process

1. **Code Push** → GitHub detects changes
2. **Build Phase** → Creates Docker images in ACR
3. **Deploy Phase** → Updates Container Instances
4. **Verify Phase** → Checks deployment status and logs

### 🕐 Time Savings

- **Manual deployment**: ~10-15 minutes
- **Automated deployment**: ~5-7 minutes
- **Your involvement**: 0 minutes (just push code!)

### 🔍 Monitoring Automated Deployments

#### Check Workflow Status
```bash
# View recent workflow runs
gh run list --repo YOUR_USERNAME/YOUR_REPO

# View specific run details
gh run view RUN_ID --repo YOUR_USERNAME/YOUR_REPO
```

#### Monitor from GitHub Web Interface
1. Go to your repository on GitHub
2. Click **Actions** tab
3. View real-time deployment progress
4. Check logs for any issues

## 🎯 Quick Start

### 1. Deploy Celery Worker
```bash
./scripts/deployment/deploy-celery-acr.sh
```

This script will:
- ✅ Create ACR if it doesn't exist
- ✅ Build and push Celery worker image
- ✅ Create Container Instance for Celery worker
- ✅ Configure all environment variables from .env

### 2. Deploy Celery Beat (Scheduler)
```bash
./scripts/deployment/deploy-celery-beat.sh
```

This script will:
- ✅ Build and push Celery Beat image
- ✅ Create Container Instance for Celery Beat
- ✅ Configure scheduler for periodic tasks

### 3. Monitor Your Containers
```bash
./scripts/development/monitor-celery.sh          # Check status
./scripts/development/monitor-celery.sh --logs   # Check status + recent logs
```

## 📊 What Gets Deployed

### Celery Worker Container
- **Name**: `umemployed-celery-worker`
- **Image**: `celeryworkerumemployed.azurecr.io/celery-worker:latest`
- **Resources**: 1 CPU, 2GB RAM
- **Command**: `celery -A umemployed worker --loglevel=info`

### Celery Beat Container  
- **Name**: `umemployed-celery-beat`
- **Image**: `celeryworkerumemployed.azurecr.io/celery-beat:latest`
- **Resources**: 0.5 CPU, 1GB RAM
- **Command**: `celery -A umemployed beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler`

## 🔧 Environment Variables Configured

All containers are configured with:
- Database connection (Azure PostgreSQL)
- Redis connection (Azure Redis Cache)
- API keys (OpenAI, Gemini, Llama)
- Azure Blob Storage credentials
- Stripe credentials
- Agora video credentials
- Django secret key

## 📈 Monitoring & Management

### Check Container Status
```bash
# Quick status check
./scripts/development/monitor-celery.sh

# Status with recent logs
./scripts/development/monitor-celery.sh --logs
```

### View Full Logs
```bash
# Celery Worker logs
az container logs --resource-group UmEmployed_RG --name umemployed-celery-worker

# Celery Beat logs
az container logs --resource-group UmEmployed_RG --name umemployed-celery-beat
```

### Restart Containers
```bash
# Restart worker
az container restart --resource-group UmEmployed_RG --name umemployed-celery-worker

# Restart beat
az container restart --resource-group UmEmployed_RG --name umemployed-celery-beat
```

## ⚙️ Setting Up Periodic Tasks

After deploying Celery Beat:

1. Go to your Django Admin panel
2. Navigate to **Periodic Tasks** section
3. Add your scheduled tasks:
   - Click "Add Periodic Task"
   - Set the task name and cron schedule
   - Select the task to run
   - Configure any arguments

### Example Periodic Tasks Setup

```python
# In Django admin, you can set up tasks like:

# Daily email reports at 9 AM
Name: Daily Email Reports
Task: users.tasks.send_daily_reports
Cron: 0 9 * * *  # Every day at 9 AM

# Weekly cleanup at midnight Sunday
Name: Weekly Cleanup
Task: job.tasks.cleanup_old_jobs
Cron: 0 0 * * 0  # Every Sunday at midnight

# Hourly health check
Name: Health Check
Task: messaging.tasks.health_check
Cron: 0 * * * *  # Every hour
```

## 🔍 Troubleshooting

### Common Issues

1. **Container won't start**: Check logs for environment variable issues
2. **Redis connection failed**: Verify Redis URL and SSL settings
3. **Database connection failed**: Check PostgreSQL credentials
4. **Tasks not executing**: Ensure Celery Beat is running and tasks are registered

### Debug Commands

```bash
# Check if containers are running
az container list --resource-group UmEmployed_RG --output table

# Get detailed container information
az container show --resource-group UmEmployed_RG --name umemployed-celery-worker

# Check ACR images
az acr repository list --name celeryworkerumemployed --output table
```

## 🧹 Cleanup

To remove all Celery containers:

```bash
# Delete worker
az container delete --resource-group UmEmployed_RG --name umemployed-celery-worker --yes

# Delete beat
az container delete --resource-group UmEmployed_RG --name umemployed-celery-beat --yes
```

## 💡 Tips

1. **Monitor regularly**: Use the monitoring script to check container health
2. **Scale if needed**: Increase CPU/memory in the deployment scripts if tasks are heavy
3. **Use different task queues**: Consider separating heavy tasks into different queues
4. **Log analysis**: Regularly check logs for any errors or performance issues

## 🎉 Success Indicators

Your Celery setup is working correctly when:
- ✅ Both containers show "Running" state
- ✅ Worker logs show "ready" messages
- ✅ Beat logs show scheduler startup
- ✅ Tasks appear in your application as completed
- ✅ No error messages in container logs

## 📞 Support

If you encounter issues:
1. Check container logs first
2. Verify environment variables are correct
3. Ensure your Django application can connect to Redis and database
4. Test task execution manually in your Django shell
