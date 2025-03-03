#!/bin/bash

if [ "$1" = "web" ]; then
    exec python manage.py runserver 0.0.0.0:8000
elif [ "$1" = "celery" ]; then
    exec celery -A umemployed worker --loglevel=info
elif [ "$1" = "daphne" ]; then
    exec daphne -b 0.0.0.0 -p 8001 umemployed.asgi:application
else
    exec "$@"
fi