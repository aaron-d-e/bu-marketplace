from django.shortcuts import render


def home(request):
    return render(request, 'market_app/home.html')


def redirect(request):
    return render(request, 'market_app/redirect.html')
