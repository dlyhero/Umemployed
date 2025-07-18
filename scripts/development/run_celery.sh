#!/bin/bash

# Check if running locally (venv directory exists)
if [ -d "venv" ]; then
    echo "Running locally: activating venv"
    source venv/bin/activate
else
    echo "Running on Azure or production environment"
    # No need to activate venv, Azure will handle it
fi

export $(cat .env | grep -v '^#' | xargs)
# Start the Celery worker
celery -A umemployed worker --loglevel=info
