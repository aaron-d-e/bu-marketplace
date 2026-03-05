"""
Backup of Admin Dashboard Views
Contains all dashboard-related view functions with graph/chart data and sidebar logic.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Count, Sum

# Note: These imports reference the main app models/forms
# from market_app.models import Product, Category
# from market_app.forms import ProductForm, CategoryForm


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
