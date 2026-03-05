# Admin Dashboard Backup

This directory contains backup copies of the admin dashboard code including graphs/charts and sidebar functionality.

## Contents

| File | Description |
|------|-------------|
| `views_dashboard.py` | All dashboard view functions including `staff_required` decorator, stats aggregation, and category distribution logic |
| `dashboard_base.html` | Base template with sidebar navigation (Overview, Products, Categories links) and Chart.js CDN include |
| `dashboard_index.html` | Main dashboard template with stat cards and Chart.js doughnut charts (Product Status, Category Distribution) |
| `dashboard_sidebar.css` | All CSS for sidebar layout, stat cards, category bars, and dark mode overrides |

## Original Locations

- Views: `market_app/views.py` (lines 128-247)
- Templates: `market_app/templates/main/dashboard/`
- CSS: `market_app/static/css/app.css` (lines 1663-1856)

## Dependencies

- Django (django.shortcuts, django.contrib.auth, django.db.models)
- Chart.js 4.4.1 (CDN)
- Bootstrap 5 (CDN)
- CSS variables from app.css (--bu-green, --bu-gold, --card-bg, etc.)
