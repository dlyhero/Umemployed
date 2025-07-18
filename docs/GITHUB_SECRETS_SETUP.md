# GitHub Secrets Required for Celery Worker Deployment

## Required Secrets in your GitHub Repository:
## Go to: Settings > Secrets and variables > Actions > New repository secret

# Azure Container Registry
ACR_USERNAME=celeryworkerumemployed
ACR_PASSWORD=<your-acr-admin-password>

# Azure Authentication
AZURE_CREDENTIALS=<your-azure-service-principal-json>

# Database Configuration (from your Django settings)
AZURE_DB_NAME=<your-postgres-db-name>
AZURE_DB_USER=<your-postgres-username>
AZURE_DB_PASSWORD=<your-postgres-password>
AZURE_DB_HOST=<your-postgres-host>
AZURE_DB_PORT=5432

# Redis Configuration
REDIS_URL=<your-redis-connection-string>

# Django Settings
SECRET_KEY=<your-django-secret-key>

# Google OAuth (if Celery tasks use these)
SOCIAL_AUTH_GOOGLE_OAUTH_KEY=<your-google-oauth-key>
SOCIAL_AUTH_GOOGLE_OAUTH_SECRET=<your-google-oauth-secret>

## How to get these values:

### Azure Container Registry credentials:
```bash
# Get ACR admin credentials
az acr credential show --name celeryworkerumemployed --resource-group UmEmployed_RG
```

### Azure Service Principal for AZURE_CREDENTIALS:
```bash
# Create service principal
az ad sp create-for-rbac \
  --name "github-actions-celery-sp" \
  --role contributor \
  --scopes /subscriptions/<subscription-id>/resourceGroups/UmEmployed_RG \
  --sdk-auth
```

### Redis URL format examples:
# Azure Redis Cache: rediss://your-redis.redis.cache.windows.net:6380/0?ssl_cert_reqs=none
# Redis Labs: rediss://username:password@hostname:port/0?ssl_cert_reqs=none
# Local: redis://localhost:6379/0
