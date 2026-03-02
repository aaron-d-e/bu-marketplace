from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('sign_up/', views.sign_up, name='sign_up'),
    path('login/', views.login_view, name='login'),
    path('products/', views.products, name='products'),
    path('products/<int:pk>/edit/', views.edit_product, name='edit_product'),
    path('products/<int:pk>/delete/', views.delete_product, name='delete_product'),
    path('create_product/', views.create_product, name='create_product'),
    path('settings/', views.settings_view, name='settings'),
    path('leadership/', views.leadership, name='leadership'),
    path('mission/', views.mission, name='mission'),
    path('policy/', views.policy, name='policy'),
    path('terms/', views.terms, name='terms'),
]
