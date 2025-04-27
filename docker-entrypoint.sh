#!/bin/bash

# Wait for Redis to be ready
echo "Waiting for Redis..."
sleep 5

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Execute the command passed to docker-entrypoint.sh
exec "$@"