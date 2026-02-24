# Scripts

## setup_env.sh — Python environment & dependencies

**For new clones / collaborators.** Creates a virtualenv and installs dependencies from `requirements.txt`.

From the project root:

```bash
./scripts/setup_env.sh
```

Then activate the environment and set up the app:

```bash
source .venv/bin/activate   # Linux/macOS
# or:  .venv\Scripts\activate   on Windows

cp .env.example .env       # then edit .env with your DB credentials
python manage.py migrate
python manage.py runserver
```

---

## setup_postgres_user.sh — PostgreSQL user & database

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
