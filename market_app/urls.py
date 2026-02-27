from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup_page/', views.signup_page, name='signup_page'),
    path('login_page/', views.login_page, name='login_page'),
    path('successful_login/', views.successful_login, name='successful_login'),
    path('create_product/', views.create_product, name='create_product'),
    path('view_products/', views.view_products, name='view_products'),
    path('view_all_products/', views.view_all_products, name='view_all_products'),
]
