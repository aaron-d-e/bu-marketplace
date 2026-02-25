from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('redirect/', views.redirect, name='redirect'),
    path('signup_page/', views.signup_page, name='signup_page'),
    path('login_page/', views.login_page, name='login_page'),
]
