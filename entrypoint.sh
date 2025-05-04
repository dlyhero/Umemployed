#!/bin/bash

# Wait for the database to be ready
echo "Waiting for the database to be ready..."
# You can use `wait-for-it` or similar tools if needed to wait for the database

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Collect static files (if not already done during build)
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start the application with Gunicorn
echo "Starting Gunicorn server..."
exec gunicorn umemployed.wsgi:application --bind 0.0.0.0:8000
