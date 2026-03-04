from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Product, Category, Inquiry, ProductCondition

ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp']
MAX_IMAGE_SIZE = 2 * 1024 * 1024  # 2MB


class RegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        # the two passwords check that each other are identical
        fields = ['username', 'email', 'password1', 'password2']
        
    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if not email.endswith('@baylor.edu'):
            raise forms.ValidationError('Please use a Baylor email address.')
        return email

# form that connects to the inquiry model
class InquiryForm(forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = ['make', 'model', 'year', 'category', 'condition']

        def clean_condition(self):
            condition = self.cleaned_data.get('condition')
            if condition not in ProductCondition.values:
                raise forms.ValidationError('Invalid condition.')
            return condition

class EmailLoginForm(forms.Form):
    """Login with email and password (uses EmailBackend)."""
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'autocomplete': 'email'}))
    password = forms.CharField(
        label='Password',
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}),
    )

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user = None
        super().__init__(*args, **kwargs)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        if email is not None and password:
            self.user = authenticate(self.request, email=email, password=password)
            if self.user is None:
                raise forms.ValidationError('Invalid email or password.')
            if not self.user.is_active:
                raise forms.ValidationError('This account is inactive.')
        return self.cleaned_data


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'category', 'description', 'price', 'image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].required = False
        self.fields['category'].queryset = Category.objects.all().order_by('name')


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']


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