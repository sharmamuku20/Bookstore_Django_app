#!/bin/sh
set -e

# Run Django maintenance commands
python manage.py collectstatic --noinput
python manage.py migrate --noinput

# Start Gunicorn
exec gunicorn bookstore.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3 --timeout 120
