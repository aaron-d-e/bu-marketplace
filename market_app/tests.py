from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from unittest.mock import patch, MagicMock
from io import BytesIO
from PIL import Image

from .models import Product


def create_test_image(name='test.jpg', size=(100, 100), format='JPEG'):
    """Create a test image file for upload testing."""
    file = BytesIO()
    image = Image.new('RGB', size, color='red')
    image.save(file, format=format)
    file.seek(0)
    return SimpleUploadedFile(name, file.read(), content_type=f'image/{format.lower()}')


class ProductImageModelTests(TestCase):
    """Test Product model image field behavior."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )

    def test_product_without_image(self):
        """Product can be created without an image."""
        product = Product.objects.create(
            user=self.user,
            title='No Image Product',
            price=10.00
        )
        self.assertFalse(product.image)
        self.assertEqual(product.title, 'No Image Product')

    def test_product_image_field_accepts_null(self):
        """Image field accepts null values."""
        product = Product.objects.create(
            user=self.user,
            title='Null Image',
            price=5.00,
            image=None
        )
        self.assertIsNone(product.image.name)

    @patch('storages.backends.s3.S3Storage.save')
    def test_product_with_image_saves_filename(self, mock_save):
        """Product stores image filename when uploaded."""
        mock_save.return_value = 'test_image.jpg'
        
        image = create_test_image('test_image.jpg')
        product = Product.objects.create(
            user=self.user,
            title='With Image',
            price=20.00,
            image=image
        )
        self.assertTrue(mock_save.called)


class ProductImageURLTests(TestCase):
    """Test image URL generation for Supabase storage."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )

    def test_image_url_format_is_supabase_public(self):
        """Image URL uses Supabase public object path."""
        product = Product(
            user=self.user,
            title='URL Test',
            price=15.00
        )
        # Simulate a saved image name (as stored in DB)
        product.image.name = 'test-photo.jpg'
        
        url = product.image.url
        self.assertIn('supabase.co/storage/v1/object/public/product-images', url)
        self.assertIn('test-photo.jpg', url)

    def test_image_url_does_not_use_s3_endpoint(self):
        """Image URL should not use S3 endpoint for public access."""
        product = Product(
            user=self.user,
            title='S3 Check',
            price=15.00
        )
        product.image.name = 'photo.jpg'
        
        url = product.image.url
        self.assertNotIn('/storage/v1/s3/', url)


class ProductImageUploadViewTests(TestCase):
    """Test create_product view with image uploads."""

    def setUp(self):
        self.client = Client()
        self.superuser = User.objects.create_superuser(
            username='admin', password='adminpass123', email='admin@test.com'
        )
        self.regular_user = User.objects.create_user(
            username='regular', password='regularpass123'
        )

    def test_create_product_requires_superuser(self):
        """Non-superusers cannot access create_product."""
        self.client.login(username='regular', password='regularpass123')
        response = self.client.get(reverse('create_product'))
        self.assertNotEqual(response.status_code, 200)

    def test_superuser_can_access_create_product(self):
        """Superusers can access create_product page."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('create_product'))
        self.assertEqual(response.status_code, 200)

    @patch('storages.backends.s3.S3Storage.save')
    def test_create_product_with_image_upload(self, mock_save):
        """Superuser can create product with image."""
        mock_save.return_value = 'uploaded_image.jpg'
        
        self.client.login(username='admin', password='adminpass123')
        image = create_test_image('uploaded_image.jpg')
        
        response = self.client.post(reverse('create_product'), {
            'title': 'New Product',
            'price': '25.00',
            'description': 'A test product',
            'image': image,
        })
        
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.assertTrue(Product.objects.filter(title='New Product').exists())
        mock_save.called

    @patch('storages.backends.s3.S3Storage.save')
    def test_create_product_without_image(self, mock_save):
        """Product can be created without an image."""
        self.client.login(username='admin', password='adminpass123')
        
        response = self.client.post(reverse('create_product'), {
            'title': 'No Image Product',
            'price': '15.00',
            'description': 'Product without image',
        })
        
        self.assertEqual(response.status_code, 302)
        product = Product.objects.get(title='No Image Product')
        self.assertFalse(product.image)
        mock_save.assert_not_called()


class ProductsPageRenderingTests(TestCase):
    """Test products page template rendering with images."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )

    def test_products_page_renders_without_images(self):
        """Products page loads when products have no images."""
        Product.objects.create(
            user=self.user, title='No Image', price=10.00
        )
        response = self.client.get(reverse('products'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No Image')

    def test_products_page_renders_with_image_url(self):
        """Products page includes image URL in HTML."""
        product = Product.objects.create(
            user=self.user, title='Has Image', price=20.00
        )
        product.image.name = 'test-product.jpg'
        product.save()
        
        response = self.client.get(reverse('products'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'test-product.jpg')

    def test_products_page_no_crash_on_empty_image(self):
        """Page doesn't crash when image field is empty string."""
        product = Product.objects.create(
            user=self.user, title='Empty Image', price=5.00
        )
        product.image = ''
        product.save()
        
        response = self.client.get(reverse('products'))
        self.assertEqual(response.status_code, 200)


class ImageFieldEdgeCaseTests(TestCase):
    """Test edge cases for image handling."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )

    def test_product_image_bool_false_when_empty(self):
        """Empty image evaluates to False in boolean context."""
        product = Product.objects.create(
            user=self.user, title='Empty', price=10.00
        )
        self.assertFalse(bool(product.image))

    def test_product_image_bool_true_when_set(self):
        """Image with name evaluates to True in boolean context."""
        product = Product.objects.create(
            user=self.user, title='Has Image', price=10.00
        )
        product.image.name = 'exists.jpg'
        self.assertTrue(bool(product.image))

    @patch('storages.backends.s3.S3Storage.save')
    def test_multiple_products_same_image_name(self, mock_save):
        """Multiple products can reference same image name."""
        mock_save.return_value = 'shared.jpg'
        
        for i in range(3):
            product = Product.objects.create(
                user=self.user,
                title=f'Product {i}',
                price=10.00
            )
            product.image.name = 'shared.jpg'
            product.save()
        
        products = Product.objects.filter(image='shared.jpg')
        self.assertEqual(products.count(), 3)
