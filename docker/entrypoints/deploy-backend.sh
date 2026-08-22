#! /bin/sh

export RKN_SECRET_KEY=$(uv run python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")

uv run --no-dev gunicorn rekono.wsgi:application --bind 0.0.0.0:8000 --workers 4 --access-logfile $REKONO_HOME/logs/gunicorn.access.log --error-logfile $REKONO_HOME/logs/gunicorn.error.log --log-level info --timeout 120 --graceful-timeout 30