from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('sign_up/', views.sign_up, name='sign_up'),
    path('login/', views.login_view, name='login'),
    path('products/', views.products, name='products'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('settings/', views.settings_view, name='settings'),
    path('leadership/', views.leadership, name='leadership'),
    path('mission/', views.mission, name='mission'),
    path('policy/', views.policy, name='policy'),
    path('terms/', views.terms, name='terms'),
    path('process/', views.process_view, name='process'),
    path('inquiry/', views.inquiry_view, name='inquiry'),
    path('inquiry/success/<int:inquiry_id>/', views.inquiry_success, name='inquiry_success'),
    path('inquiry/<int:inquiry_id>/video/', views.inquiry_video, name='inquiry_video'),

    # Admin dashboard (products + categories CRUD)
    path('dashboard/', views.dashboard_index, name='admin_dashboard'),
    path('dashboard/products/', views.dashboard_products, name='dashboard_products'),
    path('dashboard/products/new/', views.dashboard_product_create, name='dashboard_product_create'),
    path('dashboard/products/<int:pk>/edit/', views.dashboard_product_edit, name='dashboard_product_edit'),
    path('dashboard/products/<int:pk>/delete/', views.dashboard_product_delete, name='dashboard_product_delete'),
    path('dashboard/categories/', views.dashboard_categories, name='dashboard_categories'),
    path('dashboard/categories/add/', views.category_create, name='category_create'),
    path('dashboard/categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('dashboard/categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
]
