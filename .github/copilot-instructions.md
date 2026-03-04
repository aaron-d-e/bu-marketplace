# BU Marketplace - Copilot Instructions

## Project Overview
Django 6 e-commerce platform for Baylor University. Regular users browse/buy products; staff/superusers manage products via dashboard.

## Tech Stack
- **Django 6.0.2** with PostgreSQL (Supabase-hosted via `dj-database-url`)
- **Supabase S3-compatible storage** for images (buckets: `product-images`, `profile-images`)
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
python manage.py test                                                # all tests
python manage.py test market_app.tests.ProductImageModelTests        # single class
python manage.py test market_app.tests.ProductImageModelTests.test_product_without_image  # single test
```

## Architecture

### Key Files
- `main/settings.py` - DB config, S3 storage backends, auth backends
- `market_app/views.py` - All view functions with permission decorators
- `market_app/backends.py` - Custom `EmailBackend` for email login
- `market_app/static/css/app.css` - **Single CSS file** (all styles here)
- `market_app/templates/main/base.html` - Master template

### Permission Model
```python
# Dashboard views use @staff_required (staff OR superuser)
def staff_required(view_func):
    return user_passes_test(lambda u: u.is_staff or u.is_superuser)(view_func)

# For superuser-only views
def superuser_required(view_func):
    return user_passes_test(lambda u: u.is_superuser)(view_func)
```

### User Profiles
`UserProfile` is auto-created via signal when a `User` is created. Access via `user.profile`.

### Image Storage
Two separate S3 storage backends configured in `STORAGES`:
- `default` → `product-images` bucket
- `profile_images` → `profile-images` bucket (accessed via `storages["profile_images"]`)

Image URLs use `custom_domain` for public access:
`https://{PROJECT_ID}.supabase.co/storage/v1/object/public/{bucket}/{filename}`

### URL Structure
- Public pages: `/`, `/products/`, `/login/`, `/sign_up/`
- User pages: `/settings/`
- Dashboard (staff): `/dashboard/`, `/dashboard/products/`, `/dashboard/categories/`

## Key Conventions

### Single CSS File Policy
All custom styles go in `market_app/static/css/app.css`. Do NOT create additional CSS files. Supports light/dark themes via CSS variables.

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
- Dashboard templates in `market_app/templates/main/dashboard/`

### Views Pattern
- Function-based views with decorators
- Use `@staff_required` for dashboard/admin views (staff or superuser)
- Use `@login_required` for authenticated user views

### Testing Pattern
Tests mock S3 storage with `@patch('storages.backends.s3.S3Storage.save')`. Use `create_test_image()` helper from `tests.py` for image upload tests.

## Environment Variables
Required in `.env`:
```
SECRET_KEY, DATABASE_URL, SUPABASE_URL, SUPABASE_KEY, SUPABASE_S3_ACCESS_KEY, SUPABASE_S3_SECRET_KEY
```
