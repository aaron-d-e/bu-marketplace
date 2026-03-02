# BU Marketplace - Copilot Instructions

## Project Overview
Django 6 e-commerce platform for Baylor University. Regular users browse/buy products; only superusers can create products.

## Tech Stack
- **Django 6.0.2** with PostgreSQL (Supabase-hosted via `dj-database-url`)
- **Supabase S3-compatible storage** for product images (bucket: `product-images`)
- **Bootstrap 5** (CDN) + **Crispy Forms** for frontend
- **Email-based auth** via custom `EmailBackend` in `market_app/backends.py`

## Commands

```bash
# Development
source .venv/bin/activate
python manage.py runserver

# Database
python manage.py makemigrations
python manage.py migrate
python manage.py dbshell              # PostgreSQL shell

# Users
python manage.py create_user <username> <password> <email>
python manage.py create_user --admin <username> <password> <email>  # superuser

# Tests
python manage.py test                           # all tests
python manage.py test market_app.tests.ProductImageModelTests  # single class
python manage.py test market_app.tests.ProductImageModelTests.test_product_without_image  # single test
```

## Architecture

### Key Files
- `main/settings.py` - DB, S3 storage, auth backends
- `market_app/views.py` - All view functions with `@superuser_required` decorator
- `market_app/backends.py` - Custom `EmailBackend` for email login
- `market_app/static/css/app.css` - **Single CSS file** (all styles here)
- `market_app/templates/main/base.html` - Master template

### Permission Model
```python
# Superuser-only views use this decorator
def superuser_required(view_func):
    return user_passes_test(lambda u: u.is_superuser)(view_func)
```

### Image Upload Flow
Form → `create_product` view → `ProductForm.save()` → `django-storages` S3 backend → Supabase bucket

Image URLs use `custom_domain` for public access:
`https://{PROJECT_ID}.supabase.co/storage/v1/object/public/product-images/{filename}`

## Key Conventions

### Single CSS File Policy
All custom styles go in `market_app/static/css/app.css`. Do NOT create additional CSS files.

### Baylor Theme Colors
```css
:root {
  --bu-green: #154734;        /* Primary - navbar, buttons */
  --bu-green-hover: #1a5a42;  /* Hover state */
  --bu-gold: #FFB81C;         /* Accent - links, highlights */
}
```

### Template Pattern
- All pages extend `{% extends 'main/base.html' %}`
- Use `{% block content %}` for page content
- Forms: `{{ form|crispy }}` for Bootstrap styling
- Static files: `{% load static %}` then `{% static 'css/app.css' %}`

### Views Pattern
- Function-based views with decorators
- Use `@superuser_required` for admin-only views
- Use `@login_required` for authenticated views

## Environment Variables
Required in `.env`:
```
SECRET_KEY, DATABASE_URL, SUPABASE_URL, SUPABASE_KEY, SUPABASE_S3_ACCESS_KEY, SUPABASE_S3_SECRET_KEY
```
