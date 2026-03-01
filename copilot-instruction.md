# BU Marketplace - Copilot Instructions

## Project Overview
BU Marketplace is a Django-based e-commerce platform for Baylor University. Users can browse and buy products, while only admin users (superusers) can create/manage products.

---

## Tech Stack

### Backend
- **Django 6.0.2** - Python web framework
- **Supabase PostgreSQL** - Cloud-hosted PostgreSQL database
  - Connection via `dj-database-url` parsing `DATABASE_URL` env var
  - Connection pooling enabled (`conn_max_age=600`)

### Storage
- **Supabase S3-compatible Storage** - Product image hosting
  - Bucket: `product-images`
  - Integration: `django-storages` with `boto3`
  - Public read access enabled (`querystring_auth: False`)

### Frontend
- **Bootstrap 5.3.8** - CSS framework (CDN-loaded)
- **Crispy Forms + Bootstrap5** - Django form rendering
- **Custom CSS** - Baylor theme styling

---

## Project Structure

```
bu-marketplace/
├── main/                     # Django project configuration
│   ├── settings.py           # App settings, DB, S3, auth backends
│   ├── urls.py               # Root URL routing
│   ├── wsgi.py / asgi.py     # Server entry points
│
├── market_app/               # Main application
│   ├── models.py             # Product model
│   ├── views.py              # View functions (home, products, auth)
│   ├── urls.py               # App-specific routes
│   ├── forms.py              # RegisterForm, EmailLoginForm, ProductForm
│   ├── backends.py           # Custom EmailBackend for authentication
│   ├── admin.py              # Django admin configuration
│   ├── static/
│   │   └── css/
│   │       └── app.css       # ⚠️ SINGLE CSS FILE - all styles here
│   └── templates/
│       ├── main/
│       │   ├── base.html     # Master template with navbar
│       │   ├── home.html     # Home page
│       │   ├── products.html # Product listing
│       │   └── create_product.html
│       └── registration/
│           ├── login.html
│           └── sign_up.html
│
├── requirements.txt          # Python dependencies
├── db.sqlite3                # Local SQLite (dev fallback)
└── .env                      # Environment variables (not committed)
```

---

## Key Conventions

### 1. Single CSS File Policy
**All custom styles go in `market_app/static/css/app.css`**
- Do NOT create additional CSS files
- Use CSS custom properties for theme colors
- Bootstrap handles most styling; app.css is for Baylor branding

### 2. Baylor University Theme Colors
```css
:root {
  --bu-green: #154734;        /* Primary - navbar, buttons */
  --bu-green-hover: #1a5a42;  /* Hover state */
  --bu-gold: #FFB81C;         /* Accent - links, highlights */
  --white: #FFFFFF;
}
```

### 3. Template Inheritance
- `base.html` is the master template containing:
  - Navbar with Home, Products (authenticated only), Login/Logout
  - Bootstrap CSS/JS CDN imports
  - `{% block content %}` for page content
- All pages extend `base.html` using `{% extends 'main/base.html' %}`

### 4. Email-Based Authentication
- Custom `EmailBackend` in `backends.py` authenticates users by email
- Username is collected but email is the primary login credential
- Configured in `AUTHENTICATION_BACKENDS` in settings.py

---

## User Roles & Permissions

### Regular Users
- ✅ Sign up with username, email, password
- ✅ Login with email + password
- ✅ View all products on `/products/`
- ✅ View product details (images, price, description)
- ❌ **Cannot create products**
- ❌ **Cannot sell products**

### Admin Users (Superusers)
- ✅ All regular user capabilities
- ✅ Create products via `/create_product/`
- ✅ Access to Django admin panel at `/admin/`
- Create admins with: `python manage.py createsuperuser`

### Permission Enforcement
```python
# views.py - superuser_required decorator
def superuser_required(view_func):
    return user_passes_test(lambda u: u.is_superuser)(view_func)

@superuser_required
def create_product(request):
    # Only superusers can access this view
```

---

## Models

### Product Model
```python
class Product(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField(null=True)
    price = models.FloatField()
    image = models.ImageField(null=True)  # Stored in Supabase S3
    sold = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

---

## Supabase Integration

### Database Connection
```python
# settings.py
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600
    )
}
```

### S3-Compatible Storage
```python
# settings.py - Product images stored in Supabase Storage
STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "bucket_name": "product-images",
            "endpoint_url": "https://{PROJECT_ID}.supabase.co/storage/v1/s3",
            "access_key": os.getenv('SUPABASE_S3_ACCESS_KEY'),
            "secret_key": os.getenv('SUPABASE_S3_SECRET_KEY'),
            "default_acl": "public-read",
            "querystring_auth": False,
        },
    },
}
```

### Required Environment Variables
```env
SECRET_KEY=your-django-secret-key
DATABASE_URL=postgresql://user:pass@host:port/db
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_S3_ACCESS_KEY=your-s3-access-key
SUPABASE_S3_SECRET_KEY=your-s3-secret-key
```

---

## URL Routes

| Path | View | Description |
|------|------|-------------|
| `/` or `/home/` | `home` | Home page |
| `/products/` | `products` | Product listing (auth required to see) |
| `/create_product/` | `create_product` | Create product (superuser only) |
| `/login/` | `login_view` | Email-based login |
| `/sign_up/` | `sign_up` | User registration |
| `/logout/` | Django built-in | Logout (POST only) |
| `/admin/` | Django admin | Admin panel |

---

## Forms

### RegisterForm
- Fields: username, email, password1, password2
- Extends Django's `UserCreationForm`

### EmailLoginForm
- Fields: email, password
- Custom form that authenticates via `EmailBackend`

### ProductForm
- Fields: title, description, price, image
- Image field is optional

---

## Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser (admin)
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Collect static files (production)
python manage.py collectstatic
```

---

## Coding Guidelines

1. **Views**: Use function-based views with decorators for permissions
2. **Templates**: Always extend `base.html`, use `{% block content %}`
3. **Forms**: Use Crispy Forms with `{{ form|crispy }}` for consistent styling
4. **Static files**: Load with `{% load static %}` and `{% static 'path' %}`
5. **URLs**: Use named URLs with `{% url 'name' %}` in templates
6. **CSRF**: Always include `{% csrf_token %}` in forms
7. **Styling**: Add styles to `app.css` only, use BU theme colors
