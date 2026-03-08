from django.contrib import admin
from .models import Tag, Product, ProductSize

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'total_stock')
    list_filter = ('tags',)
    search_fields = ('name', 'description')
    filter_horizontal = ('tags',)
    inlines = [ProductSizeInline]

@admin.register(ProductSize)
class ProductSizeAdmin(admin.ModelAdmin):
    list_display = ('product', 'name', 'stock')
    list_filter = ('product',)
