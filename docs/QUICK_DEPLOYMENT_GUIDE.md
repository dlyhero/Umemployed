# 🚀 Quick Reference: Automated Celery Deployment

## 🎯 One-Time Setup (Do this once)

### 1. Edit GitHub repository info
```bash
nano scripts/deployment/setup-github-secrets.sh
# Change: REPO_OWNER and REPO_NAME to your GitHub username and repo
```

### 2. Install GitHub CLI (if not installed)
```bash
sudo apt update && sudo apt install gh
gh auth login  # Follow prompts to login
```

### 3. Set up all secrets automatically
```bash
./scripts/deployment/setup-github-secrets.sh
```

## ⚡ Daily Workflow (Automatic!)

1. **Make code changes** to your Celery tasks, models, etc.
2. **Commit and push** to main/master branch:
   ```bash
   git add .
   git commit -m "Updated celery tasks"
   git push origin main
   ```
3. **That's it!** GitHub Actions automatically:
   - Builds new Docker images
   - Pushes to Azure Container Registry
   - Deploys updated containers
   - Verifies deployment

## 📊 Monitor Deployments

### GitHub Web Interface
- Go to your repo → **Actions** tab
- Watch real-time deployment progress
- View logs and status

### Command Line
```bash
# Check recent deployments
gh run list

# View specific deployment details  
gh run view [RUN_ID]

# Check container status
./scripts/development/monitor-celery.sh
```

## 🔧 Manual Override (if needed)

If GitHub Actions is down or you need immediate deployment:
```bash
./scripts/deployment/deploy-celery-acr.sh      # Deploy worker
./scripts/deployment/deploy-celery-beat.sh     # Deploy beat scheduler
```

## 🎉 Benefits

✅ **Fast**: 5-7 minutes vs 10-15 minutes manual
✅ **Secure**: All secrets stored safely in GitHub
✅ **Automatic**: Just push code, deployment happens
✅ **Versioned**: Each deployment tagged with commit SHA
✅ **Reliable**: Consistent deployment process
✅ **Zero downtime**: Containers restart with new version

## 🔍 Troubleshooting

### Workflow fails?
1. Check Actions tab for error logs
2. Verify all GitHub secrets are set correctly
3. Ensure Azure service principal has proper permissions

### Manual deployment needed?
```bash
./scripts/deployment/deploy-celery-acr.sh --force
```

### Check container health
```bash
./scripts/development/monitor-celery.sh --logs
```

---
**🎯 Remember**: After one-time setup, just push your code and everything deploys automatically!
