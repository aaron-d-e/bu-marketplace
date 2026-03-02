from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegisterForm, EmailLoginForm, ProductForm, ProfilePictureForm
from .models import Product
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages
from .utils import resize_profile_image

def superuser_required(view_func):
    return user_passes_test(lambda u: u.is_superuser)(view_func)

def home(request):
    return render(request, 'main/home.html')


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
    products = Product.objects.all()
    return render(request, 'main/products.html', {'products': products})

@superuser_required
def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.user = request.user
            product.save()
            return redirect('products')
    else:
        form = ProductForm()
    return render(request, 'main/create_product.html', {'form': form})


@superuser_required
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully.')
            return redirect('products')
    else:
        form = ProductForm(instance=product)
    return render(request, 'main/edit_product.html', {'form': form, 'product': product})


@superuser_required
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted.')
        return redirect('products')
    return render(request, 'main/delete_product_confirm.html', {'product': product})


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