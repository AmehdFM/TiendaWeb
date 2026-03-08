from django.urls import path
from . import views

app_name = 'adminpanel'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Products
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.product_add, name='product_add'),
    path('products/update-stock/<int:product_id>/', views.update_stock, name='update_stock'),
    path('products/json/<int:product_id>/', views.product_detail_json, name='product_detail_json'),
    path('products/edit/<int:product_id>/', views.product_edit, name='product_edit'),

    # Tags
    path('tags/', views.tag_list, name='tag_list'),
    path('tags/add/', views.tag_add, name='tag_add'),
    path('tags/json/<int:tag_id>/', views.tag_detail_json, name='tag_detail_json'),
    path('tags/edit/<int:tag_id>/', views.tag_edit, name='tag_edit'),

    # Operations
    path('operations/', views.operation_list, name='operation_list'),

    # Wholesale Clients
    path('mayoristas/', views.wholesale_list, name='wholesale_list'),
    path('mayoristas/agregar/', views.wholesale_add, name='wholesale_add'),
    path('mayoristas/<int:client_id>/', views.wholesale_detail, name='wholesale_detail'),
    path('mayoristas/<int:client_id>/editar/', views.wholesale_edit, name='wholesale_edit'),
    path('mayoristas/<int:client_id>/json/', views.wholesale_detail_json, name='wholesale_detail_json'),
    path('mayoristas/<int:client_id>/compra/', views.wholesale_purchase_add, name='wholesale_purchase_add'),
    path('mayoristas/tallas/<int:product_id>/', views.wholesale_sizes_json, name='wholesale_sizes_json'),

    # Physical Stores
    path('tiendas/', views.physical_store_list, name='physical_store_list'),
    path('tiendas/agregar/', views.physical_store_add, name='physical_store_add'),
    path('tiendas/<int:store_id>/', views.physical_store_detail, name='physical_store_detail'),
    path('tiendas/<int:store_id>/editar/', views.physical_store_edit, name='physical_store_edit'),
    path('tiendas/<int:store_id>/json/', views.physical_store_detail_json, name='physical_store_detail_json'),
    path('tiendas/<int:store_id>/inventario/', views.store_inventory_update, name='store_inventory_update'),
    path('tiendas/<int:store_id>/inventario/<int:inventory_id>/eliminar/', views.store_inventory_delete, name='store_inventory_delete'),
]
