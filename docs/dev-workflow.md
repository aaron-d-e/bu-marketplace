# Dev Workflow & Tech Stack

## Tech Stack

| Layer | Technology |
|---|---|
| **Web framework** | Django 6.0 (Python) |
| **Database** | PostgreSQL (via psycopg3 driver) |
| **Config** | python-dotenv (reads `.env`) |
| **Data model** | `Product` linked to Django's built-in `User` |

---

## Does `runserver` boot a database?

**No.** PostgreSQL is a separate process that runs independently — it's already running via Homebrew (`brew services start postgresql@14`). Django just *connects* to it. If Postgres isn't running, Django will throw a connection error. You can verify anytime with:

```bash
brew services list | grep postgres
```

---

## Development Workflow

**1. Check your branch**
```bash
git branch                  # see current branch
git checkout -b my-feature  # create & switch to a new branch
```

**2. Activate the Python venv** (every new terminal session)
```bash
source .venv/bin/activate
```
Your prompt will show `(.venv)` when active.

**3. Run the dev server**
```bash
python manage.py runserver
# → http://127.0.0.1:8000
```

**4. Django MVT pattern** — the framework you follow is **MVT (Model-View-Template)**:
- `market_app/models.py` — define your data (e.g. `Product`)
- `market_app/views.py` — handle request logic
- `main/urls.py` — route URLs to views
- Templates folder (not yet created) — HTML rendering

**5. Schema changes workflow**
```bash
# After editing models.py:
python manage.py makemigrations   # generate migration file
python manage.py migrate          # apply it to Postgres
```

**6. Useful commands**
```bash
python manage.py dbshell                                    # jump into psql as erick
python manage.py create_user username password email        # create a user
python manage.py create_user --admin username pass email    # superuser
```
