#!/bin/bash
# Build the project (per Medium: Deploying Django to Vercel)
# Static-build has no deps; create venv and install with uv (pip is blocked in uv-managed env).
set -e
echo "Creating virtual environment..."
uv venv
source .venv/bin/activate
echo "Installing dependencies..."
uv pip install -r requirements.txt
echo "Make migrations..."
python manage.py makemigrations --noinput || true
python manage.py migrate --noinput
echo "Collect static..."
python manage.py collectstatic --noinput --clear
