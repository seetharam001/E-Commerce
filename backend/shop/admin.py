from django.contrib import admin
from .models import Category, Product, Variant, Review

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'image']

class VariantInline(admin.TabularInline):
    model = Variant
    extra = 1  # number of empty variant forms

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'image']
    inlines = [VariantInline]
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__username', 'comment']

admin.site.register(Review, ReviewAdmin)