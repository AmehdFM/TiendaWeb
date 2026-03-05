from django.urls import path
from . import views

app_name = 'adminpanel'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.product_add, name='product_add'),
    path('products/update-stock/<int:product_id>/', views.update_stock, name='update_stock'),
    path('tags/', views.tag_list, name='tag_list'),
    path('tags/add/', views.tag_add, name='tag_add'),
    path('products/json/<int:product_id>/', views.product_detail_json, name='product_detail_json'),
    path('products/edit/<int:product_id>/', views.product_edit, name='product_edit'),
    path('tags/json/<int:tag_id>/', views.tag_detail_json, name='tag_detail_json'),
    path('tags/edit/<int:tag_id>/', views.tag_edit, name='tag_edit'),
    path('operations/', views.operation_list, name='operation_list'),
]
