from __future__ import absolute_import, unicode_literals

import os
import ssl

from celery import Celery
from django.conf import settings

# Load environment variables
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "umemployed.settings")

app = Celery("umemployed")

app.config_from_object(settings, namespace="CELERY")

app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
