from django.urls import path
from . import views


app_name = 'store'

urlpatterns = [
    # Store management URLs
    path('stores/', views.store_list, name='store_list'),
    path('stores/<int:store_id>/products/', views.product_list, name='store_product_list'),

    # Product-related URLs
    path('products/<int:store_id>/', views.product_list, name='user_product_list'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/edit/<int:pk>/', views.edit_product, name='edit_product'),
    path('products/delete/<int:pk>/', views.delete_product, name='delete_product'),
    path('search/', views.search_product, name='search_product'),
    path('products/', views.add_product, name='add_product'),
    path('products/export/', views.add_product, name='export_products'), 
   

    # Staff-related URLs
    path('add_staff/', views.add_staff, name='add_staff'),
    path('staff_list/', views.staff_list, name='staff_list'),

    path('categories/', views.category_list, name='category_list'),
    
    path('suppliers/add', views.add_supplier, name='add_supplier'),
    path('suppliers/edit/<int:pk>/', views.edit_supplier, name='edit_supplier'),
    path('suppliers/delete/<int:pk>/', views.delete_supplier, name='delete_supplier'),



    path('categories/add/', views.add_category, name='add_category'),
    path('edit_category/<int:category_id>/', views.edit_category, name='edit_category'),
    path('delete_category/', views.delete_category, name='delete_category'),



    path('add/', views.add_store, name='add_store'),
    path('edit/<int:pk>/', views.add_store, name='edit_store'),  # Reuse the add_store view
    path('delete/<int:pk>/', views.delete_store, name='delete_store'),

    path('export-to-products/', views.export_to_excel, name='export_to_excel'),
]
