# Django GCP Project with Gunicorn and Celery

This project is a Django application configured to run with Gunicorn and Celery using Redis as the message broker.

## Prerequisites

- Python 3.11+
- Redis server running locally (or configured in settings.py)
- Virtual environment (venv)

## Setup

1. Activate your virtual environment:
   ```
   source venv/bin/activate
   ```

2. Install dependencies (if not already installed):
   ```
   pip install django gunicorn celery redis django-celery-results
   ```

3. Make sure Redis is running:
   ```
   redis-server
   ```

## Running the Application

### Option 1: Using the run script

The easiest way to run both Gunicorn and Celery together is using the provided script:

```
./run.sh
```

This will start both Gunicorn and Celery worker processes.

### Option 2: Running components separately

#### Start Celery worker:

```
celery -A config worker --loglevel=info
```

#### Start Gunicorn:

```
gunicorn -c gunicorn_config.py config.wsgi:application
```

## Configuration

- Gunicorn configuration is in `gunicorn_config.py`
- Celery configuration is in `config/settings.py`

## Production Deployment

For production deployment, consider:

1. Setting `DEBUG = False` in settings.py
2. Configuring proper `ALLOWED_HOSTS`
3. Setting up a proper process manager like systemd or supervisor
4. Using a reverse proxy like Nginx in front of Gunicorn