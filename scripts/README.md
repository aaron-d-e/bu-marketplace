# Scripts

## setup_postgres_user.sh

One-time setup for the Django project's PostgreSQL database.

**When:** Before first `python manage.py migrate` (or when you see `FATAL: role "aaron" does not exist`).

**Run:**

```bash
./scripts/setup_postgres_user.sh
```

Creates the `aaron` user and `products` database to match `.env`, then run:

```bash
python manage.py migrate
```
