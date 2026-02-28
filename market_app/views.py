from django.shortcuts import render, redirect
from .forms import RegisterForm, EmailLoginForm
from django.contrib.auth import login


def home(request):
    return render(request, 'main/home.html')


def sign_up(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
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
    from .models import Product
    products = Product.objects.all()
    return render(request, 'main/products.html', {'products': products})

def create_product(request):
    return render(request, 'main/create_product.html')