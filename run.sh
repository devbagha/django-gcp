#!/bin/bash

# Activate virtual environment if needed
# source venv/bin/activate

# Set environment variables
export DJANGO_SETTINGS_MODULE=config.settings

# Start Celery worker in the background
echo "Starting Celery worker..."
celery -A config worker --loglevel=info &

# Store the Celery worker PID
CELERY_PID=$!

# Start Gunicorn with the configuration file
echo "Starting Gunicorn server..."
gunicorn -c gunicorn_config.py config.wsgi:application

# If Gunicorn exits, also kill the Celery worker
kill $CELERY_PID