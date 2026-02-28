from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from market_app.models import Product


def home(request):
    featured = Product.objects.filter(sold=False).order_by('-created_at')[:6]
    total_listings = Product.objects.filter(sold=False).count()
    return render(request, 'market_app/home.html', {
        'featured': featured,
        'total_listings': total_listings,
    })


def browse(request):
    products = Product.objects.select_related('user').order_by('-created_at')
    return render(request, 'market_app/browse.html', {'products': products})


def redirect_page(request):
    return render(request, 'market_app/redirect_page.html')

def signup_page(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password')
        errors = []

           # if fields are empty 
        if not (username and email and password):
            errors.append('Username, email, and password are required.')
        else:
            # check if username or email already exists
            if User.objects.filter(username__iexact=username).exists():
                errors.append('A user with that username already exists.')
            if User.objects.filter(email__iexact=email).exists():
                errors.append('A user with that email already exists.')

        if not errors:
            # create user if no errors
            User.objects.create_user(username=username, email=email, password=password)
            messages.success(request, 'welcome_new_user')
            return redirect('home')

        return render(request, 'market_app/signup_page.html', {
            'errors': errors, # show errors on screen
        })
    return render(request, 'market_app/signup_page.html')

def login_page(request):
    if request.method == 'POST':
        # only take email and password into account - username should be in app only
        email = request.POST.get('email')
        password = request.POST.get('password')
        # authenticate user using email and password
        user = authenticate(request, email=email, password=password)
        if user is not None:
            # login user if authentication is successful
            login(request, user)
            return redirect('home')
        else:
            print("Invalid email or password")
    return render(request, 'market_app/login_page.html')

def successful_login(request):
    return render(request, 'market_app/successful_login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def settings_page(request):
    return render(request, 'market_app/settings_page.html')

@login_required
def create_product(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        price_raw = request.POST.get('price', '').strip()
        image_url = request.POST.get('image_url', '').strip() or None
        errors = []

        if not title:
            errors.append('Title is required.')

        if not price_raw:
            errors.append('Price is required.')
        else:
            try:
                price = float(price_raw)
            except ValueError:
                errors.append('Price must be a number.')
            else:
                if price <= 0:
                    errors.append('Price must be greater than 0.')

        if not errors:
            try:
                Product.objects.create(
                    user=request.user,
                    title=title,
                    description=description or '',
                    price=price,
                    image_url=image_url,
                )
                return redirect('view_products')
            except Exception as e:
                errors.append('Error creating product: ' + str(e))

        if errors:
            return render(request, 'market_app/create_product.html', {
                'errors': errors,
                'title': title,
                'description': description,
                'price': price_raw,
                'image_url': image_url,
            })

    return render(request, 'market_app/create_product.html')


@login_required
def view_products(request):
    products = Product.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'market_app/view_products.html', {'products': products})