# Products Page Frontend

This document covers the products page sidebar layout and product detail modal.

## Layout Structure

The products page uses a sidebar layout matching the admin dashboard pattern:

```
┌─────────────────────────────────────────────┐
│ Navbar                                      │
├────────────┬────────────────────────────────┤
│ Sidebar    │ Main Content                   │
│            │                                │
│ - Search   │ ┌─────┐ ┌─────┐ ┌─────┐       │
│ - All      │ │ Card│ │ Card│ │ Card│       │
│ - Cat 1    │ └─────┘ └─────┘ └─────┘       │
│ - Cat 2    │                                │
│            │                                │
└────────────┴────────────────────────────────┘
```

### Template Inheritance

```
main/base.html
  └── main/products/base.html  (adds sidebar layout)
        └── main/products.html  (product grid + modal)
```

### Key Files

| File | Purpose |
|------|---------|
| `templates/main/products/base.html` | Sidebar layout, search input, category nav |
| `templates/main/products.html` | Product grid, modal HTML, modal JS |
| `static/css/app.css` | All styles (`.products-*` and `.product-modal-*` classes) |

## Sidebar

The sidebar contains:

1. **Header** - "Shop" title
2. **Search** - Client-side filtering of product cards
3. **Category Links** - Filter products by category (server-side via URL params)

### CSS Classes

| Class | Purpose |
|-------|---------|
| `.products-layout` | Flex container for sidebar + main |
| `.products-sidebar` | Fixed-width sidebar (260px) |
| `.products-sidebar-header` | "Shop" heading |
| `.products-sidebar-search` | Search input wrapper |
| `.products-sidebar-nav` | Category links container |
| `.products-sidebar-link` | Individual category link |
| `.products-sidebar-link.active` | Currently selected category |
| `.products-main` | Main content area |

## Product Detail Modal

Clicking a product card opens a modal overlay with full product details.

### Behavior

- **Open**: Click any product card
- **Close**: Click X button, click overlay backdrop, or press ESC key
- Body scroll is disabled while modal is open

### JavaScript API

```javascript
// Open modal with product data from card element
openProductModal(cardElement)

// Close modal
closeProductModal()
```

### Data Attributes

Product cards include data attributes for modal population:

```html
<div class="product-card"
     data-product-id="1"
     data-product-title="Product Name"
     data-product-price="29.99"
     data-product-description="Full description..."
     data-product-category="Electronics"
     data-product-image="/path/to/image.jpg">
```

### CSS Classes

| Class | Purpose |
|-------|---------|
| `.product-modal-overlay` | Full-screen backdrop |
| `.product-modal-overlay.active` | Visible state |
| `.product-modal` | Modal container |
| `.product-modal-close` | X button |
| `.product-modal-content` | Flex row for image + details |
| `.product-modal-image` | Left side image container |
| `.product-modal-placeholder` | "No Image" fallback |
| `.product-modal-details` | Right side text content |
| `.product-modal-price` | Price display |
| `.product-modal-title` | Product title |
| `.product-modal-category` | Category badge |
| `.product-modal-description` | Full description |

## Responsive Design

### Desktop (>768px)
- Sidebar: 260px fixed width on left
- Modal: 50/50 image/details split

### Mobile (≤768px)
- Sidebar: Full width, horizontal scrolling category links
- Modal: Stacked layout (image on top, details below)

## Dark Mode

All components support dark mode via `[data-theme="dark"]` selectors:

- Sidebar uses gold accent colors instead of green
- Modal inherits card background from CSS variables
- Placeholders use darker gradient backgrounds
