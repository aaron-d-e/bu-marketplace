import logging
import os
import re

from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegisterForm, EmailLoginForm, ProductForm, ProfilePictureForm, CategoryForm, InquiryForm
from .models import Product, Category, Inquiry
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Count, Sum
from .utils import resize_profile_image
from google import genai
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


def home(request):
    categories = Category.objects.all().order_by('name')
    products = Product.objects.filter(sold=False).order_by('-created_at')
    items_listed_count = products.count() or 0  # Demo placeholder
    inquiry_count = Inquiry.objects.count() or 128  # Demo placeholder
    total_sales_volume = Product.objects.filter(sold=True).aggregate(
        total=Sum('price')
    )['total'] or 0
    return render(request, 'main/home.html', {
        'categories': categories,
        'products': products,
        'items_listed_count': items_listed_count,
        'inquiry_count': inquiry_count,
        'total_sales_volume': total_sales_volume,
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
def user_items(request):
    inquiries = Inquiry.objects.filter(user=request.user).select_related('category').order_by('-created_at')
    return render(request, 'main/user_items.html', {'inquiries': inquiries})

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
                logger.exception('Quote generation failed for inquiry pk=%s', inquiry.pk)
                messages.error(request, 'We couldn’t get a quote right now. Please try again later.')
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
    category_id_raw = request.GET.get('category')
    selected_category_id = None
    if category_id_raw is not None:
        try:
            pk = int(category_id_raw)
            if Category.objects.filter(pk=pk).exists():
                selected_category_id = pk
        except (ValueError, TypeError):
            pass
    if selected_category_id is not None:
        products = Product.objects.filter(category_id=selected_category_id)
    else:
        products = Product.objects.all()
    return render(request, 'main/products.html', {
        'products': products,
        'categories': categories,
        'selected_category_id': selected_category_id,
    })


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'main/product_detail.html', {'product': product})


@login_required
def checkout(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if product.sold:
        messages.warning(request, 'That item has already been sold.')
        return redirect('product_detail', pk=pk)

    if request.method == 'POST':
        # Mock payment:w
        #: processing - mark product as sold
        product.sold = True
        product.save()
        request.session['purchase_title'] = product.title
        return redirect('purchase_thank_you')

    return render(request, 'main/checkout.html', {'product': product})


@login_required
def purchase_thank_you(request):
    title = request.session.pop('purchase_title', None)
    return render(request, 'main/purchase_thank_you.html', {'purchase_title': title})


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
    # Summary stats
    total_products = Product.objects.count()
    sold_products = Product.objects.filter(sold=True).count()
    available_products = total_products - sold_products
    total_revenue = Product.objects.filter(sold=True).aggregate(total=Sum('price'))['total'] or 0
    total_users = User.objects.count()
    total_categories = Category.objects.count()
    
    # Category distribution
    categories = Category.objects.annotate(
        product_count=Count('product')
    ).order_by('-product_count')
    
    context = {
        'total_products': total_products,
        'sold_products': sold_products,
        'available_products': available_products,
        'total_revenue': total_revenue,
        'total_users': total_users,
        'total_categories': total_categories,
        'categories': categories,
    }
    return render(request, 'main/dashboard/index.html', context)


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
