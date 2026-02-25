from django.shortcuts import render, redirect
from django.contrib.auth.models import User


def home(request):
    return render(request, 'market_app/home.html')


def redirect(request):
    return render(request, 'market_app/redirect.html')

def signup_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        if username and email and password:
            User.objects.create_user(username=username, email=email, password=password)
            return redirect('home')
    return render(request, 'market_app/signup_page.html')

def login_page(request):
    return render(request, 'market_app/login_page.html')