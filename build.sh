#!/bin/bash
# Build the project (per Medium: Deploying Django to Vercel)
# Dependencies are installed by Vercel from requirements.txt; do not run pip here (uv-managed env).
set -e
echo "Make migrations..."
python manage.py makemigrations --noinput || true
python manage.py migrate --noinput
echo "Collect static..."
python manage.py collectstatic --noinput --clear
