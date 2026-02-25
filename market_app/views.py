from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login

def home(request):
    return render(request, 'market_app/home.html')


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
            return redirect('successful_login') # redirect to successful login page

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
            return redirect('successful_login')
        else:
            print("Invalid email or password")
    return render(request, 'market_app/login_page.html')

def successful_login(request):
    return render(request, 'successful_login.html')
