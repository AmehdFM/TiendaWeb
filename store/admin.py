from django.contrib import admin
from .models import Tag, Product

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock')
    list_filter = ('tags',)
    search_fields = ('name', 'description')
    filter_horizontal = ('tags',)
