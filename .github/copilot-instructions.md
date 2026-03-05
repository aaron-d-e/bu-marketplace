# BU Marketplace - Copilot Instructions

## Project Overview
**S.H.A.R.E Bear** - Django 6 e-commerce platform for Baylor University students to buy/sell used items. Users can browse products, submit AI-powered price inquiries, and manage their profiles. Staff users manage products and categories via an admin dashboard.

## Tech Stack
- **Django 6.0.2** with PostgreSQL (Supabase-hosted via `dj-database-url`)
- **Supabase S3-compatible storage** for images (two buckets: `product-images`, `profile-images`)
- **Bootstrap 5.3.8** (CDN) + **Crispy Forms** (`crispy-bootstrap5`) for frontend
- **Email-based auth** via custom `EmailBackend` - users log in with email, not username
- **Google Gemini API** (`gemini-2.5-flash`) for AI price quotes on sell inquiries
- **Vercel** for deployment with serverless functions
- **Pillow** for image processing (resize, format conversion)

## Commands

```bash
# Development
source .venv/bin/activate
python manage.py runserver              # http://127.0.0.1:8000

# First-time setup (new clone)
./scripts/setup_env.sh                  # Creates venv, installs deps
./scripts/setup_postgres_user.sh        # Creates local postgres user/db (if using local DB)

# Database
python manage.py makemigrations
python manage.py migrate
python manage.py dbshell                # PostgreSQL interactive shell

# Users
python manage.py create_user <username> <password> <email>
python manage.py create_user --admin <username> <password> <email>  # staff/superuser

# Tests
python manage.py test                                                              # all tests
python manage.py test market_app.tests.ProductImageModelTests                      # single class
python manage.py test market_app.tests.ProductImageModelTests.test_product_without_image  # single test

# Deployment (Vercel runs this)
./build.sh                              # uses uv, runs migrations, collectstatic
```

## Architecture

### Project Structure
```
main/                    # Django project config
├── settings.py          # DB, storage backends, auth, middleware
├── urls.py              # Root URL config (delegates to market_app)
└── wsgi.py              # WSGI entry point

market_app/              # Main application
├── models.py            # Product, Category, Inquiry, UserProfile
├── views.py             # All view functions
├── forms.py             # RegisterForm, EmailLoginForm, ProductForm, InquiryForm, etc.
├── backends.py          # EmailBackend for email-based authentication
├── utils.py             # Image processing utilities (resize_profile_image)
├── urls.py              # App URL patterns
├── templates/main/      # All templates
│   ├── base.html        # Master template with navbar, footer, JS
│   ├── dashboard/       # Admin dashboard templates
│   └── *.html           # Page templates
└── static/css/app.css   # Single CSS file (all custom styles)

api/index.py             # Vercel serverless entrypoint
```

### Data Models

**Product** - Items for sale
- `user` (FK→User), `title`, `description`, `category` (FK→Category), `price`, `image`, `sold`, timestamps

**Category** - Product categories
- `name`

**Inquiry** - User requests for AI price quotes when selling
- `user` (FK→User), `make`, `model`, `condition` (enum: new/used/like new/good/fair/poor), `price` (AI-generated), timestamps

**UserProfile** - Extended user data (auto-created via signal)
- `user` (OneToOne→User), `profile_image`, `updated_at`
- Methods: `get_initials()`, `delete_profile_image()`

### URL Routes

**Public pages:** `/`, `/products/`, `/products/<pk>/`, `/process/`, `/mission/`, `/leadership/`, `/policy/`, `/terms/`

**Auth:** `/login/`, `/logout/`, `/sign_up/`

**Authenticated users:** `/settings/` (profile), `/inquiry/` (AI quote)

**Staff dashboard:** `/dashboard/`, `/dashboard/products/`, `/dashboard/categories/` (full CRUD)

### Permission Model
```python
def staff_required(view_func):
    """Dashboard views - requires is_staff OR is_superuser"""
    return user_passes_test(lambda u: u.is_staff or u.is_superuser)(view_func)

# @login_required - any authenticated user
# @staff_required - dashboard/admin views only
```

### Authentication Flow
1. Registration requires `@baylor.edu` email (enforced in `RegisterForm.clean_email()`)
2. Login uses email + password via `EmailBackend` (not username)
3. `EmailBackend` does case-insensitive email lookup
4. Both `EmailBackend` and `ModelBackend` are configured (fallback)

### Storage Backends
Two Supabase S3 buckets in `settings.STORAGES`:
- `default` → `product-images` bucket (Product.image)
- `profile_images` → `profile-images` bucket (UserProfile.profile_image)

Image URLs use `custom_domain` for public access:
```
https://{PROJECT_ID}.supabase.co/storage/v1/object/public/{bucket}/{filename}
```

### AI Price Quote Flow
1. User submits `InquiryForm` with make, model, condition
2. `inquiry_view` calls Google Gemini API with prompt
3. Response parsed for price (50% of wholesale value)
4. Price saved to `Inquiry.price`, user redirected to success page

### Image Processing
- Profile images resized to max 500×500px via `utils.resize_profile_image()`
- Converted to JPEG, 85% quality
- Validation: JPEG/PNG/WebP only, max 2MB, max 4096×4096px

### Model Signals
`UserProfile` auto-created when `User` is created (`post_save` signal in `models.py`)

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
```django
{% extends 'main/base.html' %}
{% load static %}

{% block title %}Page Title{% endblock %}

{% block content %}
  {# Page content here #}
  {{ form|crispy }}  {# For forms #}
{% endblock %}
```

Available blocks: `title`, `content`, `fullwidth_content` (skips container), `extra_js`

### Views Pattern
- Function-based views with decorators
- Use `@staff_required` for dashboard/admin views
- Use `@login_required` for authenticated user views
- Use `messages.success/error()` for flash messages
- Dashboard auto-dismisses alerts after 2 seconds (JS in base.html)

### Form Conventions
- All forms use crispy forms with Bootstrap 5 template pack
- Image upload validation in form's `clean_*` methods
- Custom `EmailLoginForm` (not Django's `AuthenticationForm`)

## Environment Variables
Required in `.env`:
```
SECRET_KEY
DATABASE_URL              # Supabase PostgreSQL connection string
SUPABASE_URL
SUPABASE_KEY
SUPABASE_PROJECT_ID       # defaults to nvumdffvsysdmpruyhyu
SUPABASE_S3_ACCESS_KEY
SUPABASE_S3_SECRET_KEY
GOOGLE_API_KEY            # For Gemini AI price quotes
DEBUG                     # "true" for development
ALLOWED_HOSTS             # comma-separated, defaults to bu-marketplace.vercel.app
```

## Testing Patterns
Tests mock S3 storage to avoid external calls:
```python
@patch('storages.backends.s3.S3Storage.save')
def test_with_image(self, mock_save):
    mock_save.return_value = 'filename.jpg'
    # ... test code
```
Use `create_test_image()` helper from `tests.py` for image upload tests.
