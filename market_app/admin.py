from django.contrib import admin
from .models import Category, Product, Inquiry


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', )
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price', 'sold', 'user', 'created_at')
    list_filter = ('category', 'sold')
    search_fields = ('title',)

@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ('make', 'model', 'years_of_use', 'category', 'condition', 'user', 'created_at')
    list_filter = ('category', 'condition')
    search_fields = ('make', 'model')
