from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegisterForm, EmailLoginForm, ProductForm, ProfilePictureForm, CategoryForm, InquiryForm
from .models import Product, Category, Inquiry
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages
from .utils import resize_profile_image
import os
import re
from google import genai
from dotenv import load_dotenv
load_dotenv()

# initialize google genai client

def superuser_required(view_func):
    return user_passes_test(lambda u: u.is_superuser)(view_func)

def home(request):
    categories = Category.objects.all().order_by('name')
    products = Product.objects.filter(sold=False).order_by('-created_at')
    return render(request, 'main/home.html', {
        'categories': categories,
        'products': products,
    })


def sign_up(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            authed_user = authenticate(
                request,
                email=user.email,
                password=form.cleaned_data.get('password1'),
            )
            if authed_user is not None:
                login(request, authed_user)
            else:
                # Fallback to avoid ValueError if authentication fails unexpectedly.
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('home')
    else:
        form = RegisterForm()

    return render(request, 'registration/sign_up.html', {'form': form})


@login_required
def inquiry_view(request):
    if request.method == 'POST':
        form = InquiryForm(request.POST)
        if form.is_valid():
            inquiry = form.save(commit=False)
            inquiry.user = request.user
            inquiry.save()

            try:
                client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))
                prompt = (
                    f"Generate me a price quote for the following product. Find the wholesale value and return me 50% of that value in a single number without any text or symbols attached)."
                    f"Product: {inquiry.make} {inquiry.model}"
                    f"Condition: {inquiry.condition}"
                    f"Category: {inquiry.category}"
                    f"Once again, reply with a single number without any text or symbols attached. Dont attach a dollar sign. Use a single number."
                )
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                client.close()
                response_text = response.text.strip()
                # Parse price: allow digits, optional decimal, strip any extra text
                match = re.search(r'[\d,]+\.?\d*', response_text.replace(',', ''))
                if match:
                    inquiry.price = int(float(match.group()))
                    inquiry.save()
                return redirect('inquiry_success', inquiry_id=inquiry.pk)
            except Exception as e:
                messages.error(request, f'Error getting quote: {e}')
    else:
        form = InquiryForm()
    return render(request, 'main/inquiry.html', {'form': form})


@login_required
def inquiry_success(request, inquiry_id):
    inquiry = get_object_or_404(Inquiry, pk=inquiry_id, user=request.user)
    return render(request, 'main/inquiry_success.html', {'inquiry': inquiry})


@login_required
def inquiry_video(request, inquiry_id):
    inquiry = get_object_or_404(Inquiry, pk=inquiry_id, user=request.user)
    return render(request, 'main/inquiry_video.html', {'inquiry': inquiry})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = EmailLoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.user)
            return redirect('home')
    else:
        form = EmailLoginForm(request)

    return render(request, 'registration/login.html', {'form': form})

def products(request):
    categories = Category.objects.all().order_by('name')
    category_id = request.GET.get('category')
    if category_id:
        products = Product.objects.filter(category_id=category_id)
    else:
        products = Product.objects.all()
    return render(request, 'main/products.html', {
        'products': products,
        'categories': categories,
        'selected_category_id': category_id,
    })


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'main/product_detail.html', {'product': product})



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


def leadership(request):
    return render(request, 'main/leadership.html')


def mission(request):
    return render(request, 'main/mission.html')


def policy(request):
    return render(request, 'main/policy.html')


def terms(request):
    return render(request, 'main/terms.html')


def process_view(request):
    return render(request, 'main/process.html')


# --- Admin dashboard (staff-like CRUD for products and categories) ---

def staff_required(view_func):
    """Allow staff or superuser (for non-technical editors)."""
    return user_passes_test(lambda u: u.is_staff or u.is_superuser)(view_func)


@staff_required
def dashboard_index(request):
    return render(request, 'main/dashboard/index.html')


@staff_required
def dashboard_products(request):
    product_list = Product.objects.select_related('category').order_by('-created_at')
    return render(request, 'main/dashboard/products.html', {'products': product_list})


@staff_required
def dashboard_product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.user = request.user
            product.save()
            messages.success(request, 'Product created.')
            return redirect('dashboard_products')
    else:
        form = ProductForm()
    return render(request, 'main/dashboard/product_create.html', {'form': form})


@staff_required
def dashboard_product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated.')
            return redirect('dashboard_products')
    else:
        form = ProductForm(instance=product)
    return render(request, 'main/dashboard/product_edit.html', {'form': form, 'product': product})


@staff_required
def dashboard_product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted.')
        return redirect('dashboard_products')
    return render(request, 'main/dashboard/product_confirm_delete.html', {'product': product})


@staff_required
def dashboard_categories(request):
    category_list = Category.objects.order_by('name')
    return render(request, 'main/dashboard/categories.html', {'categories': category_list})


@staff_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created.')
            return redirect('dashboard_categories')
    else:
        form = CategoryForm()
    return render(request, 'main/dashboard/category_form.html', {'form': form, 'title': 'Add Category'})


@staff_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated.')
            return redirect('dashboard_categories')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'main/dashboard/category_form.html', {'form': form, 'category': category, 'title': 'Edit Category'})


@staff_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted.')
        return redirect('dashboard_categories')
    return render(request, 'main/dashboard/category_confirm_delete.html', {'category': category})
