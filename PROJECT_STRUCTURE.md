# UmEmployed Project Structure

## Overview
This document outlines the organized structure of the UmEmployed project after restructuring the root directory.

## Root Directory Structure

```
Umemployed/
├── 📁 Django Apps
│   ├── asseessments/          # Assessment and quiz functionality
│   ├── company/              # Company and recruiter features
│   ├── dashboard/            # Dashboard views and analytics
│   ├── job/                  # Job posting and management
│   ├── messages/             # Messaging system
│   ├── messaging/            # Enhanced messaging features
│   ├── notifications/        # Notification system
│   ├── onboarding/          # User onboarding process
│   ├── resume/              # Resume management and processing
│   ├── social_features/     # Social networking features
│   ├── transactions/        # Payment and subscription handling
│   ├── users/               # User management and profiles
│   ├── videochat/           # Video chat functionality
│   └── website/             # Main website views
│
├── 📁 Configuration & Setup
│   ├── config/              # Configuration files
│   │   ├── nginx.conf       # Nginx configuration
│   │   └── scale-rules.json # Azure scaling rules
│   ├── umemployed/          # Django project settings
│   ├── manage.py            # Django management script
│   ├── requirements.txt     # Python dependencies
│   ├── pyproject.toml       # Project configuration
│   ├── pytest.ini          # Testing configuration
│   ├── .flake8             # Code linting configuration
│   ├── .pre-commit-config.yaml # Git hooks
│   └── .python-version     # Python version specification
│
├── 📁 Deployment & Infrastructure
│   ├── scripts/deployment/  # Deployment scripts
│   │   ├── deploy-celery-acr.sh
│   │   ├── deploy-celery-beat.sh
│   │   ├── build-celery-worker.sh
│   │   ├── setup-github-secrets.sh
│   │   ├── setup-github-secrets-manual.sh
│   │   ├── verify-secrets.sh
│   │   └── upload-env.sh
│   ├── scripts/development/ # Development and utility scripts
│   │   ├── monitor-celery.sh
│   │   ├── run_celery.sh
│   │   ├── run_tests.sh
│   │   ├── test-docker-local.sh
│   │   ├── monitor_job_creation.py
│   │   ├── validate-setup.py
│   │   ├── daily_email_script.py
│   │   ├── test_google_oauth.py
│   │   ├── utils.py
│   │   └── pool_example.py
│   ├── Dockerfile           # Main application Dockerfile
│   ├── Dockerfile.celery    # Celery worker Dockerfile
│   ├── docker-compose.yml   # Docker Compose configuration
│   ├── entrypoint.sh        # Docker entrypoint script
│   ├── .dockerignore        # Docker ignore file
│   ├── Procfile             # Heroku deployment configuration
│   └── Makefile             # Build automation
│
├── 📁 Documentation
│   ├── docs/               # All documentation files
│   │   ├── deployment/     # Deployment guides
│   │   ├── development/    # Development guides
│   │   ├── testing/        # Testing documentation
│   │   ├── README.md       # Main project README
│   │   ├── FRONTEND_API_DOCUMENTATION.md
│   │   ├── CELERY_AZURE_DEPLOYMENT.md
│   │   ├── CELERY_WORKER_SETUP.md
│   │   ├── DOCKER_HUB_DEPLOYMENT.md
│   │   ├── GITHUB_SECRETS_SETUP.md
│   │   ├── POSTMAN_TESTING_GUIDE.md
│   │   ├── QUICK_DEPLOYMENT_GUIDE.md
│   │   ├── SECURITY_IMPROVEMENTS.md
│   │   └── ... (other .md files)
│   └── postman/            # API testing collections
│
├── 📁 Examples & Templates
│   ├── examples/           # Code examples and templates
│   │   ├── next-js-google-oauth-example.js
│   │   └── google-meet-frontend-example.js
│   └── templates/          # Django HTML templates
│
├── 📁 Static & Media Files
│   ├── static/             # Static files (CSS, JS, images)
│   ├── staticfiles/        # Collected static files
│   ├── media/              # User-uploaded media files
│   ├── resumes/            # Resume file storage
│   └── transcripts/        # Transcript file storage
│
├── 📁 Data & Backups
│   ├── backup/             # Database backups
│   ├── all_data.json       # Data export
│   ├── latest.dump         # Database dump
│   └── db.sqlite3          # SQLite database (development)
│
├── 📁 Testing & Quality
│   ├── tests/              # Test files
│   ├── .pytest_cache/      # Pytest cache
│   └── test_venv/          # Test virtual environment
│
├── 📁 Version Control & CI/CD
│   ├── .git/               # Git repository
│   ├── .github/            # GitHub Actions workflows
│   ├── .gitignore          # Git ignore rules
│   └── .vscode/            # VS Code configuration
│
└── 📁 Environment & Virtual Environments
    ├── .venv/              # Main virtual environment
    ├── myenv/              # Alternative virtual environment
    ├── .env                # Environment variables (not in git)
    └── .production         # Production flag
```

## Key Benefits of This Structure

### 1. **Clear Separation of Concerns**
- Django apps are clearly separated
- Configuration files are centralized
- Deployment scripts are organized by purpose

### 2. **Easy Navigation**
- Related files are grouped together
- Scripts are categorized by function
- Documentation is well-organized

### 3. **Maintainability**
- Easy to find specific files
- Clear ownership of different components
- Reduced clutter in root directory

### 4. **Scalability**
- Easy to add new components
- Clear structure for new team members
- Consistent organization patterns

## Quick Reference

### 🚀 **Deployment**
- **Scripts**: `scripts/deployment/`
- **Config**: `config/`
- **Docs**: `docs/deployment/`

### 🛠️ **Development**
- **Scripts**: `scripts/development/`
- **Utils**: `scripts/development/utils.py`
- **Testing**: `scripts/development/run_tests.sh`

### 📚 **Documentation**
- **All docs**: `docs/`
- **API docs**: `docs/FRONTEND_API_DOCUMENTATION.md`
- **Setup guides**: `docs/GITHUB_SECRETS_SETUP.md`

### 🐳 **Docker & Infrastructure**
- **Dockerfiles**: Root directory
- **Compose**: `docker-compose.yml`
- **Config**: `config/`

## Migration Notes

### Files Moved from Root:
- **Deployment scripts** → `scripts/deployment/`
- **Development scripts** → `scripts/development/`
- **Documentation** → `docs/`
- **Configuration** → `config/`
- **Examples** → `examples/`

### Files Remaining in Root:
- Django apps (unchanged)
- Core configuration files
- Docker files
- Main project files

## Next Steps

1. **Update any hardcoded paths** in scripts that reference moved files
2. **Update documentation** that references old file locations
3. **Test deployment scripts** to ensure they work from new locations
4. **Update CI/CD workflows** if they reference moved files

This structure makes the project much more organized and maintainable while preserving all functionality. 