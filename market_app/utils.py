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
    
    # Generate filename with .jpg extension
    original_name = getattr(image_file, 'name', 'profile.jpg')
    base_name = original_name.rsplit('.', 1)[0] if '.' in original_name else original_name
    
    # Create new InMemoryUploadedFile
    return InMemoryUploadedFile(
        file=output,
        field_name='profile_image',
        name=f"{base_name}.jpg",
        content_type='image/jpeg',
        size=sys.getsizeof(output),
        charset=None
    )
