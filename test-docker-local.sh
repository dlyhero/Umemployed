#!/bin/bash

# Local Docker testing script for Celery worker
# This script helps you test the Docker image locally before deployment

set -e

echo "🐳 Building Celery Worker Docker Image Locally..."

# Build the image
docker build -f Dockerfile.celery -t umemployed/um_celery_worker:local .

echo "✅ Image built successfully!"

# Check if .env file exists for local testing
if [ ! -f ".env.local" ]; then
    echo "📝 Creating .env.local template..."
    cat > .env.local << EOF
# Local testing environment variables
# Copy this file and fill in your actual values

REDIS_URL=redis://localhost:6379/0
DATABASE_URL=sqlite:///./db.sqlite3
SECRET_KEY=your-secret-key-here
DJANGO_SETTINGS_MODULE=umemployed.settings
DEBUG=True
OPENAI_API_KEY=your-openai-api-key-here
REDIS_SSL_CERT_REQS=none
EOF
    echo "📝 Created .env.local template. Please fill in your values."
    echo "   You can also use your existing environment variables."
fi

echo ""
echo "🚀 To run the Celery worker locally:"
echo "docker run --rm -it --env-file .env.local umemployed/um_celery_worker:local"
echo ""
echo "🔍 To run with shell access for debugging:"
echo "docker run --rm -it --env-file .env.local --entrypoint /bin/bash umemployed/um_celery_worker:local"
echo ""
echo "🧪 To test specific commands:"
echo "docker run --rm -it --env-file .env.local umemployed/um_celery_worker:local python manage.py shell"
echo ""
echo "📊 To check what tasks are registered:"
echo "docker run --rm -it --env-file .env.local umemployed/um_celery_worker:local celery -A umemployed inspect registered"
