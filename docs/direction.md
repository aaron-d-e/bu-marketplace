# Supabase Image Upload & Retrieval for Superuser Review

## Overview
Images uploaded to the Supabase `image` bucket are staged for superuser review before being added to product pages.

---

## 1. Setup

### Install Supabase Client
```bash
pip install supabase
```

### Environment Variables
Add to your `.env`:
```
SUPABASE_URL=your-project-url
SUPABASE_KEY=your-service-role-key
SUPABASE_BUCKET=image
```

---

## 2. Upload Image to Bucket

```python
from supabase import create_client
import os

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

def upload_image(file_path, file_name):
    """Upload image to pending review folder"""
    with open(file_path, "rb") as f:
        response = supabase.storage.from_("image").upload(
            path=f"pending_review/{file_name}",
            file=f,
            file_options={"content-type": "image/jpeg"}
        )
    return response
```

---

## 3. Retrieve Pending Images (Superuser Review)

```python
def get_pending_images():
    """List all images awaiting review"""
    response = supabase.storage.from_("image").list("pending_review")
    return response

def get_image_url(file_name):
    """Get public/signed URL for image preview"""
    url = supabase.storage.from_("image").get_public_url(f"pending_review/{file_name}")
    return url
```

---

## 4. Approve & Move to Product Images

```python
def approve_image(file_name, product_id):
    """Move approved image to products folder"""
    # Download from pending
    data = supabase.storage.from_("image").download(f"pending_review/{file_name}")
    
    # Upload to products folder
    supabase.storage.from_("image").upload(
        path=f"products/{product_id}/{file_name}",
        file=data,
        file_options={"content-type": "image/jpeg"}
    )
    
    # Delete from pending
    supabase.storage.from_("image").remove([f"pending_review/{file_name}"])
```

---

## 5. Reject Image

```python
def reject_image(file_name):
    """Remove rejected image from pending review"""
    supabase.storage.from_("image").remove([f"pending_review/{file_name}"])
```

---

## Workflow Summary

1. **User uploads image** → Goes to `image/pending_review/`
2. **Superuser reviews** → Fetches list from `pending_review/`
3. **Approve** → Moves to `image/products/{product_id}/`
4. **Reject** → Deletes from `pending_review/`

---

## Bucket Structure
```
image/
├── pending_review/    # New uploads awaiting approval
└── products/          # Approved images by product ID
    ├── {product_id}/
    └── ...
```
