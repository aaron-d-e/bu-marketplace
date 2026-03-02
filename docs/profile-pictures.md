# Profile Pictures Implementation Guide

This document provides comprehensive implementation details for the profile picture feature in BU Marketplace.

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Supabase Storage Setup](#supabase-storage-setup)
4. [Django Storage Configuration](#django-storage-configuration)
5. [UserProfile Model](#userprofile-model)
6. [Image Processing](#image-processing)
7. [Forms](#forms)
8. [Views](#views)
9. [Templates](#templates)
10. [CSS Styling](#css-styling)
11. [Security Considerations](#security-considerations)
12. [Testing](#testing)

---

## Overview

The profile picture feature allows authenticated users to:
- **Upload** a profile picture from the Settings page
- **Replace** an existing profile picture with a new one
- **Remove** their profile picture entirely

The profile picture (or user initials fallback) displays in the navbar next to the username.

### Key Features
- Image validation: JPEG, PNG, WebP formats only
- Maximum file size: 2MB
- Automatic resizing to 500x500 pixels maximum
- Initials fallback when no picture is uploaded
- Supabase S3-compatible storage

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Request                            │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Settings View (POST)                         │
│  - Validates form                                               │
│  - Processes image with Pillow                                  │
│  - Saves to UserProfile                                         │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Django Storages (S3Storage)                    │
│  - Uploads to Supabase S3-compatible endpoint                   │
│  - Returns public URL via custom_domain                         │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                 Supabase Storage Bucket                         │
│  Bucket: profile-images                                         │
│  Policy: SELECT (public read)                                   │
│  URL: https://{PROJECT_ID}.supabase.co/storage/v1/object/       │
│       public/profile-images/{filename}                          │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

1. User selects image file in Settings page
2. Form submitted to `settings_view`
3. `ProfilePictureForm` validates file type and size
4. Image resized using Pillow (max 500x500)
5. Resized image saved to `UserProfile.profile_image`
6. Django Storages uploads to Supabase `profile-images` bucket
7. Database stores the filename/path
8. Template renders image URL using `profile_image.url`

---

## Supabase Storage Setup

### Bucket Configuration

The `profile-images` bucket should be configured in Supabase with:

**Bucket Settings:**
- Name: `profile-images`
- Public: Yes (for public read access)
- File size limit: 2MB

**Storage Policies:**

```sql
-- Policy: Allow public read access (SELECT)
CREATE POLICY "Public read access for profile images"
ON storage.objects
FOR SELECT
USING (bucket_id = 'profile-images');

-- Policy: Allow authenticated users to upload their own images (INSERT)
-- Note: This is handled server-side via S3 keys, but for reference:
CREATE POLICY "Users can upload profile images"
ON storage.objects
FOR INSERT
WITH CHECK (bucket_id = 'profile-images');

-- Policy: Allow users to update/delete their own images
CREATE POLICY "Users can manage their profile images"
ON storage.objects
FOR UPDATE
USING (bucket_id = 'profile-images');

CREATE POLICY "Users can delete their profile images"
ON storage.objects
FOR DELETE
USING (bucket_id = 'profile-images');
```

### S3 Credentials

The same S3 credentials used for `product-images` work for `profile-images`:
- `SUPABASE_S3_ACCESS_KEY`
- `SUPABASE_S3_SECRET_KEY`

These are set in your `.env` file and provide full access to all buckets.

---

## Django Storage Configuration

### settings.py Configuration

Add a dedicated storage backend for profile images:

```python
# main/settings.py

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "bucket_name": "product-images",
            "endpoint_url": f"https://{SUPABASE_PROJECT_ID}.supabase.co/storage/v1/s3",
            "access_key": os.getenv('SUPABASE_S3_ACCESS_KEY'),
            "secret_key": os.getenv('SUPABASE_S3_SECRET_KEY'),
            "region_name": "us-east-1",
            "default_acl": "public-read",
            "querystring_auth": False,
            "custom_domain": f"{SUPABASE_PROJECT_ID}.supabase.co/storage/v1/object/public/product-images",
        },
    },
    "profile_images": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "bucket_name": "profile-images",
            "endpoint_url": f"https://{SUPABASE_PROJECT_ID}.supabase.co/storage/v1/s3",
            "access_key": os.getenv('SUPABASE_S3_ACCESS_KEY'),
            "secret_key": os.getenv('SUPABASE_S3_SECRET_KEY'),
            "region_name": "us-east-1",
            "default_acl": "public-read",
            "querystring_auth": False,
            "custom_domain": f"{SUPABASE_PROJECT_ID}.supabase.co/storage/v1/object/public/profile-images",
        },
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}
```

### Using the Storage Backend

Reference the storage in your model:

```python
from django.core.files.storage import storages

def get_profile_storage():
    return storages["profile_images"]

class UserProfile(models.Model):
    profile_image = models.ImageField(
        storage=get_profile_storage,
        upload_to='',  # Files go to bucket root
        null=True,
        blank=True
    )
```

---

## UserProfile Model

### Model Definition

```python
# market_app/models.py

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.files.storage import storages


def get_profile_storage():
    """Return the profile_images storage backend."""
    return storages["profile_images"]


class UserProfile(models.Model):
    """Extended user profile with profile picture support."""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    profile_image = models.ImageField(
        storage=get_profile_storage,
        upload_to='',
        null=True,
        blank=True
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

    def get_initials(self):
        """Generate initials for avatar fallback."""
        if self.user.first_name and self.user.last_name:
            return f"{self.user.first_name[0]}{self.user.last_name[0]}".upper()
        elif self.user.first_name:
            return self.user.first_name[:2].upper()
        else:
            return self.user.username[:2].upper()

    def delete_profile_image(self):
        """Delete the profile image from storage and clear the field."""
        if self.profile_image:
            # Delete from Supabase storage
            self.profile_image.delete(save=False)
            self.profile_image = None
            self.save()


# Signal to auto-create UserProfile when User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Ensure profile exists for existing users
    if not hasattr(instance, 'profile'):
        UserProfile.objects.create(user=instance)
```

### Migration

After adding the model, create and apply migrations:

```bash
python manage.py makemigrations market_app
python manage.py migrate
```

### Creating Profiles for Existing Users

Run this one-time command to create profiles for existing users:

```python
# In Django shell: python manage.py shell
from django.contrib.auth.models import User
from market_app.models import UserProfile

for user in User.objects.all():
    UserProfile.objects.get_or_create(user=user)
```

---

## Image Processing

### Resizing Logic

Images are resized before upload using Pillow:

```python
# market_app/utils.py (create this file)

from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys


def resize_profile_image(image_file, max_size=(500, 500)):
    """
    Resize an uploaded image to fit within max_size while maintaining aspect ratio.
    Returns an InMemoryUploadedFile ready for saving.
    """
    img = Image.open(image_file)
    
    # Convert to RGB if necessary (handles PNG with transparency)
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    
    # Calculate new dimensions maintaining aspect ratio
    img.thumbnail(max_size, Image.Resampling.LANCZOS)
    
    # Save to BytesIO
    output = BytesIO()
    img.save(output, format='JPEG', quality=85, optimize=True)
    output.seek(0)
    
    # Create new InMemoryUploadedFile
    return InMemoryUploadedFile(
        file=output,
        field_name='profile_image',
        name=f"{image_file.name.rsplit('.', 1)[0]}.jpg",
        content_type='image/jpeg',
        size=sys.getsizeof(output),
        charset=None
    )
```

### Why JPEG Output?

- Consistent format regardless of input
- Smaller file sizes than PNG
- No transparency needed for profile pictures
- Better compression with quality=85

---

## Forms

### ProfilePictureForm

```python
# market_app/forms.py

from django import forms
from django.core.exceptions import ValidationError


ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp']
MAX_IMAGE_SIZE = 2 * 1024 * 1024  # 2MB


class ProfilePictureForm(forms.Form):
    """Form for uploading profile pictures."""
    profile_image = forms.ImageField(
        required=True,
        widget=forms.FileInput(attrs={
            'accept': 'image/jpeg,image/png,image/webp',
            'class': 'profile-image-input',
            'id': 'profile-image-input'
        })
    )

    def clean_profile_image(self):
        image = self.cleaned_data.get('profile_image')
        
        if not image:
            raise ValidationError('Please select an image.')
        
        # Validate content type
        if image.content_type not in ALLOWED_IMAGE_TYPES:
            raise ValidationError(
                'Invalid image format. Please upload a JPEG, PNG, or WebP image.'
            )
        
        # Validate file size
        if image.size > MAX_IMAGE_SIZE:
            raise ValidationError(
                f'Image too large. Maximum size is 2MB (yours: {image.size / 1024 / 1024:.1f}MB).'
            )
        
        return image
```

---

## Views

### Updated Settings View

```python
# market_app/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ProfilePictureForm
from .utils import resize_profile_image


@login_required
def settings_view(request):
    user_profile = request.user.profile
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'upload':
            form = ProfilePictureForm(request.POST, request.FILES)
            if form.is_valid():
                # Delete old image if exists
                if user_profile.profile_image:
                    user_profile.profile_image.delete(save=False)
                
                # Resize and save new image
                image = form.cleaned_data['profile_image']
                resized_image = resize_profile_image(image)
                
                # Generate unique filename
                filename = f"user_{request.user.id}_{resized_image.name}"
                user_profile.profile_image.save(filename, resized_image)
                
                messages.success(request, 'Profile picture updated successfully!')
                return redirect('settings')
            else:
                # Form has errors, will be displayed in template
                pass
        
        elif action == 'remove':
            if user_profile.profile_image:
                user_profile.delete_profile_image()
                messages.success(request, 'Profile picture removed.')
            return redirect('settings')
    
    else:
        form = ProfilePictureForm()
    
    return render(request, 'main/settings.html', {
        'form': form,
        'profile': user_profile,
    })
```

---

## Templates

### settings.html (Profile Picture Section)

```html
<!-- market_app/templates/main/settings.html -->
{% extends 'main/base.html' %}
{% load static %}

{% block title %}Settings{% endblock %}

{% block content %}
<div class="settings-container">
    <div class="settings-header">
        <h1>Settings</h1>
    </div>

    <!-- Profile Picture Card -->
    <div class="settings-card">
        <h2>Profile Picture</h2>
        
        <div class="profile-picture-section">
            <div class="profile-picture-preview">
                {% if profile.profile_image %}
                    <img src="{{ profile.profile_image.url }}" 
                         alt="Profile picture" 
                         class="profile-picture-img">
                {% else %}
                    <div class="profile-initials-large">
                        {{ profile.get_initials }}
                    </div>
                {% endif %}
            </div>
            
            <div class="profile-picture-actions">
                <!-- Upload Form -->
                <form method="post" enctype="multipart/form-data" class="upload-form">
                    {% csrf_token %}
                    <input type="hidden" name="action" value="upload">
                    
                    <label for="profile-image-input" class="btn-upload">
                        {% if profile.profile_image %}
                            Change Picture
                        {% else %}
                            Upload Picture
                        {% endif %}
                    </label>
                    {{ form.profile_image }}
                    
                    {% if form.profile_image.errors %}
                        <div class="field-error">
                            {{ form.profile_image.errors.0 }}
                        </div>
                    {% endif %}
                </form>
                
                <!-- Remove Form -->
                {% if profile.profile_image %}
                <form method="post" class="remove-form">
                    {% csrf_token %}
                    <input type="hidden" name="action" value="remove">
                    <button type="submit" class="btn-remove">
                        Remove
                    </button>
                </form>
                {% endif %}
                
                <p class="upload-hint">
                    JPEG, PNG, or WebP. Max 2MB.
                </p>
            </div>
        </div>
    </div>

    <!-- Account Info Card (existing) -->
    <div class="settings-card">
        <h2>Account</h2>
        <div class="settings-row">
            <span class="settings-label">Username</span>
            <span class="settings-value">{{ user.username }}</span>
        </div>
        <div class="settings-row">
            <span class="settings-label">Email</span>
            <span class="settings-value">{{ user.email }}</span>
        </div>
        {% if user.is_staff %}
        <div class="settings-row">
            <span class="settings-label">Role</span>
            <span class="staff-badge">Staff</span>
        </div>
        {% endif %}
    </div>

    <!-- Theme Card (existing) -->
    <div class="settings-card">
        <h2>Appearance</h2>
        <div class="settings-row">
            <span class="settings-label">Theme</span>
            <div class="theme-toggle-group">
                <button class="theme-btn" data-theme="light">Light</button>
                <button class="theme-btn" data-theme="dark">Dark</button>
            </div>
        </div>
    </div>
</div>

<script>
    // Auto-submit on file selection
    document.getElementById('profile-image-input').addEventListener('change', function() {
        if (this.files.length > 0) {
            this.closest('form').submit();
        }
    });

    // Theme toggle (existing functionality)
    const themeButtons = document.querySelectorAll('.theme-btn');
    const currentTheme = localStorage.getItem('theme') || 'light';
    
    themeButtons.forEach(btn => {
        if (btn.dataset.theme === currentTheme) {
            btn.classList.add('active');
        }
        btn.addEventListener('click', () => {
            const theme = btn.dataset.theme;
            document.documentElement.setAttribute('data-theme', theme);
            localStorage.setItem('theme', theme);
            themeButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        });
    });
</script>
{% endblock %}
```

### base.html (Navbar Avatar)

Update the user dropdown trigger in `base.html`:

```html
<!-- In the navbar, replace the user-dropdown-trigger button -->
<button class="user-dropdown-trigger" id="user-menu-trigger">
    {% if user.profile.profile_image %}
        <img src="{{ user.profile.profile_image.url }}" 
             alt="" 
             class="navbar-avatar">
    {% else %}
        <span class="navbar-initials">{{ user.profile.get_initials }}</span>
    {% endif %}
    <span class="user-dropdown-name">{{ user.username }}</span>
    <span class="user-dropdown-arrow">▼</span>
</button>
```

---

## CSS Styling

Add these styles to `market_app/static/css/app.css`:

```css
/* ===== NAVBAR AVATAR ===== */

.navbar-avatar {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    object-fit: cover;
    border: 2px solid rgba(255, 255, 255, 0.3);
}

.navbar-initials {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--bu-gold) 0%, #e6a619 100%);
    color: #154734;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: -0.02em;
}

[data-theme="dark"] .navbar-initials {
    background: linear-gradient(135deg, #FFB81C 0%, #e6a619 100%);
    color: #0d1a14;
}

/* ===== SETTINGS PROFILE PICTURE ===== */

.profile-picture-section {
    display: flex;
    align-items: center;
    gap: 2rem;
    padding: 1.5rem 1.25rem;
}

.profile-picture-preview {
    flex-shrink: 0;
}

.profile-picture-img {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    object-fit: cover;
    border: 3px solid var(--bu-green);
}

[data-theme="dark"] .profile-picture-img {
    border-color: var(--bu-gold);
}

.profile-initials-large {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 80px;
    height: 80px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--bu-gold) 0%, #e6a619 100%);
    color: #154734;
    font-size: 1.75rem;
    font-weight: 600;
    letter-spacing: -0.02em;
}

[data-theme="dark"] .profile-initials-large {
    background: linear-gradient(135deg, #FFB81C 0%, #e6a619 100%);
    color: #0d1a14;
}

.profile-picture-actions {
    flex: 1;
}

.upload-form {
    display: inline-block;
}

.profile-image-input {
    display: none;
}

.btn-upload {
    display: inline-block;
    padding: 0.5rem 1rem;
    background: var(--bu-green);
    color: #FFFFFF;
    border-radius: 8px;
    font-size: 0.875rem;
    font-weight: 500;
    cursor: pointer;
    transition: background-color 0.2s ease;
}

.btn-upload:hover {
    background: var(--bu-green-hover);
}

[data-theme="dark"] .btn-upload {
    background: var(--bu-gold);
    color: #0d1a14;
}

[data-theme="dark"] .btn-upload:hover {
    background: #e6a619;
}

.btn-remove {
    display: inline-block;
    padding: 0.5rem 1rem;
    background: transparent;
    color: #dc2626;
    border: 1px solid #dc2626;
    border-radius: 8px;
    font-size: 0.875rem;
    font-weight: 500;
    cursor: pointer;
    margin-left: 0.5rem;
    transition: all 0.2s ease;
}

.btn-remove:hover {
    background: #dc2626;
    color: #FFFFFF;
}

.upload-hint {
    margin-top: 0.75rem;
    font-size: 0.8rem;
    color: var(--text-secondary);
}

.remove-form {
    display: inline-block;
}

@media (max-width: 576px) {
    .profile-picture-section {
        flex-direction: column;
        text-align: center;
        gap: 1rem;
    }
    
    .profile-picture-actions {
        width: 100%;
    }
}
```

---

## Security Considerations

### File Upload Security

1. **Content-Type Validation**: Only accept `image/jpeg`, `image/png`, `image/webp`
2. **File Size Limit**: Maximum 2MB enforced server-side
3. **Image Processing**: Re-encode images through Pillow to strip metadata and validate they're actual images
4. **Unique Filenames**: Use `user_{id}_{filename}` pattern to prevent filename collisions

### Supabase Security

1. **Bucket Policy**: Read-only public access; writes require S3 credentials
2. **S3 Keys**: Server-side only, never exposed to client
3. **HTTPS**: All Supabase URLs use HTTPS

### Django Security

1. **CSRF Protection**: All forms include `{% csrf_token %}`
2. **Authentication Required**: `@login_required` decorator on settings view
3. **User Isolation**: Users can only modify their own profile

---

## Testing

### Test Cases

```python
# market_app/tests.py (add these tests)

class UserProfileTests(TestCase):
    """Test UserProfile model and profile picture functionality."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', 
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

    def test_profile_created_with_user(self):
        """UserProfile is auto-created when User is created."""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsInstance(self.user.profile, UserProfile)

    def test_get_initials_with_full_name(self):
        """Initials generated from first and last name."""
        self.assertEqual(self.user.profile.get_initials(), 'TU')

    def test_get_initials_with_first_name_only(self):
        """Initials from first name when no last name."""
        self.user.last_name = ''
        self.user.save()
        self.assertEqual(self.user.profile.get_initials(), 'TE')

    def test_get_initials_with_username_only(self):
        """Initials from username when no names set."""
        self.user.first_name = ''
        self.user.last_name = ''
        self.user.save()
        self.assertEqual(self.user.profile.get_initials(), 'TE')

    def test_profile_image_null_by_default(self):
        """Profile image is null by default."""
        self.assertFalse(self.user.profile.profile_image)


class ProfilePictureFormTests(TestCase):
    """Test ProfilePictureForm validation."""

    def test_rejects_invalid_content_type(self):
        """Form rejects non-image content types."""
        fake_file = SimpleUploadedFile(
            "test.txt", 
            b"not an image", 
            content_type="text/plain"
        )
        form = ProfilePictureForm(files={'profile_image': fake_file})
        self.assertFalse(form.is_valid())

    def test_rejects_oversized_image(self):
        """Form rejects images over 2MB."""
        # Create a large fake image
        large_data = b'x' * (3 * 1024 * 1024)  # 3MB
        large_file = SimpleUploadedFile(
            "large.jpg",
            large_data,
            content_type="image/jpeg"
        )
        form = ProfilePictureForm(files={'profile_image': large_file})
        self.assertFalse(form.is_valid())

    def test_accepts_valid_image(self):
        """Form accepts valid JPEG image."""
        image = create_test_image('valid.jpg')
        form = ProfilePictureForm(files={'profile_image': image})
        self.assertTrue(form.is_valid())


class SettingsViewProfilePictureTests(TestCase):
    """Test settings view profile picture functionality."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@test.com'
        )
        self.client.login(username='testuser', password='testpass123')

    @patch('storages.backends.s3.S3Storage.save')
    def test_upload_profile_picture(self, mock_save):
        """User can upload profile picture."""
        mock_save.return_value = 'user_1_test.jpg'
        
        image = create_test_image('test.jpg')
        response = self.client.post(reverse('settings'), {
            'action': 'upload',
            'profile_image': image,
        })
        
        self.assertEqual(response.status_code, 302)
        self.user.profile.refresh_from_db()
        # Profile should have an image now
        mock_save.assert_called()

    @patch('storages.backends.s3.S3Storage.delete')
    def test_remove_profile_picture(self, mock_delete):
        """User can remove profile picture."""
        self.user.profile.profile_image = 'existing.jpg'
        self.user.profile.save()
        
        response = self.client.post(reverse('settings'), {
            'action': 'remove',
        })
        
        self.assertEqual(response.status_code, 302)
```

### Running Tests

```bash
python manage.py test market_app.tests.UserProfileTests
python manage.py test market_app.tests.ProfilePictureFormTests
python manage.py test market_app.tests.SettingsViewProfilePictureTests
```

---

## Troubleshooting

### Common Issues

**1. "Profile does not exist" error**
- Run the one-time migration for existing users (see UserProfile Model section)
- Ensure signals are properly connected

**2. Image not displaying**
- Verify `custom_domain` in storage config matches bucket name
- Check Supabase bucket is set to public
- Verify SELECT policy exists on bucket

**3. Upload fails silently**
- Check S3 credentials are correct
- Verify bucket name matches exactly (`profile-images`)
- Check Django logs for storage errors

**4. Image too large after resize**
- Reduce JPEG quality (currently 85)
- Reduce max dimensions (currently 500x500)

---

## Future Enhancements

1. **Image Cropping**: Add client-side cropping before upload
2. **Avatar Colors**: Generate consistent colors based on user ID for initials
3. **CDN Integration**: Add Cloudflare or similar CDN for faster image delivery
4. **Gravatar Fallback**: Use Gravatar as secondary fallback before initials
