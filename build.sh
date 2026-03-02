#!/bin/bash
# Build the project (per Medium: Deploying Django to Vercel)
set -e
echo "Building the project..."
python -m pip install -r requirements.txt
echo "Make migrations..."
python manage.py makemigrations --noinput || true
python manage.py migrate --noinput
echo "Collect static..."
python manage.py collectstatic --noinput --clear
