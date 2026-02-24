#!/usr/bin/env bash
# One-time setup: create PostgreSQL user and database for Django (bu-market).
# Run once: ./scripts/setup_postgres_user.sh
# Uses same credentials as .env: user aaron, database products.

set -e

DB_USER="aaron"
DB_NAME="products"
# Must match PASSWORD in .env
DB_PASSWORD="Cowboy0621!"

echo "Creating PostgreSQL user '$DB_USER'..."
sudo -u postgres psql -v ON_ERROR_STOP=0 -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';" || true

echo "Creating database '$DB_NAME' (if not exists)..."
sudo -u postgres createdb -O "$DB_USER" "$DB_NAME" 2>/dev/null || true

echo "Granting privileges..."
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
sudo -u postgres psql -d "$DB_NAME" -c "GRANT ALL ON SCHEMA public TO $DB_USER;"
sudo -u postgres psql -d "$DB_NAME" -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $DB_USER;"

echo "Done. Run: python manage.py migrate"
