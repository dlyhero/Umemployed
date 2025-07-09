# Deployment Guide

This document outlines the process for deploying the Umemployed application to production environments.

## Deployment Options

The application can be deployed using several methods:

1. Docker deployment with Docker Compose
2. Azure App Service deployment via GitHub Actions
3. Traditional deployment on a Linux server

## Prerequisites

- Production-ready PostgreSQL database
- Redis server for Celery and caching
- SMTP server for sending emails
- Storage service (Azure Blob Storage or AWS S3) for static/media files
- SSL certificate for HTTPS

## Docker Deployment

### 1. Configure Environment Variables

Copy the `.env.example` file and configure the production settings:

```bash
cp .env.example .env.prod
# Edit .env.prod with production values
```

### 2. Build and Start the Containers

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### 3. Apply Database Migrations

```bash
docker-compose exec web python manage.py migrate
```

### 4. Collect Static Files

```bash
docker-compose exec web python manage.py collectstatic --noinput
```

## Azure App Service Deployment

The repository is already configured for continuous deployment to Azure App Service using GitHub Actions.

### 1. Configure Azure App Service

1. Create an Azure App Service with the required plan
2. Set up a PostgreSQL server in Azure
3. Configure Azure Application Insights for monitoring

### 2. Configure GitHub Secrets

Add the following secrets to your GitHub repository:

- `AZURE_CREDENTIALS`: Azure service principal credentials
- `AZURE_APP_NAME`: The name of your Azure App Service
- `AZURE_RESOURCE_GROUP`: The resource group name
- `DATABASE_URL`: Connection string for your PostgreSQL database
- Other environment variables as defined in `.env.example`

### 3. Trigger the Deployment

The deployment will be triggered automatically on pushes to the main branch. You can also manually trigger the workflow from the GitHub Actions tab.

## Traditional Server Deployment

### 1. Server Setup

```bash
# Update packages
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3-pip python3-venv nginx postgresql redis-server

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 2. Configure Gunicorn

Create a systemd service file for Gunicorn:

```ini
# /etc/systemd/system/umemployed.service
[Unit]
Description=Umemployed Gunicorn daemon
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/path/to/umemployed
ExecStart=/path/to/umemployed/venv/bin/gunicorn --workers 3 --bind unix:/path/to/umemployed/umemployed.sock umemployed.wsgi:application
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

### 3. Configure Nginx

```nginx
# /etc/nginx/sites-available/umemployed
server {
    listen 80;
    server_name yourdomain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /path/to/umemployed;
    }
    
    location /media/ {
        root /path/to/umemployed;
    }
    
    location / {
        include proxy_params;
        proxy_pass http://unix:/path/to/umemployed/umemployed.sock;
    }
}
```

### 4. Set Up Celery

Create a systemd service file for Celery:

```ini
# /etc/systemd/system/umemployed-celery.service
[Unit]
Description=Umemployed Celery Worker
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/path/to/umemployed
ExecStart=/path/to/umemployed/venv/bin/celery -A umemployed worker -l info
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

### 5. Start Services

```bash
# Enable and start services
sudo systemctl enable umemployed.service
sudo systemctl start umemployed.service
sudo systemctl enable umemployed-celery.service
sudo systemctl start umemployed-celery.service

# Configure Nginx
sudo ln -s /etc/nginx/sites-available/umemployed /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

## SSL Configuration

Use Let's Encrypt for free SSL certificates:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

## Monitoring

Set up monitoring for your production deployment:

1. Sentry for error tracking
2. Prometheus for metrics
3. Grafana for visualization
4. ELK stack for log management

## Backups

Configure automated database backups:

1. Set up daily PostgreSQL dumps
2. Store backups in a secure location (separate cloud storage)
3. Test backup restoration periodically
