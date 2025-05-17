import os
import subprocess

# Set environment variables if needed manually or assume Azure will inject them
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "umemployed.settings")

# Start Celery worker
subprocess.call(["celery", "-A", "umemployed", "worker", "--loglevel=info"])
