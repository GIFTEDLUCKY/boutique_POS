from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    # Store management URLs
    path('stores/', views.store_list, name='store_list'),
    path('stores/<int:store_id>/products/', views.product_list, name='store_product_list'),

    # Product-related URLs
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/edit/<int:pk>/', views.edit_product, name='edit_product'),
    path('products/delete/<int:pk>/', views.delete_product, name='delete_product'),
    path('products/search/', views.search_product, name='search_product'),
    path('products/export/', views.export_to_excel, name='export_products'),

    # Staff-related URLs
    path('staff/add/', views.add_staff, name='add_staff'),
    path('staff/edit/<int:id>/', views.edit_staff, name='edit_staff'),
    path('staff/delete/<int:id>/', views.delete_staff, name='delete_staff'),
    path('staff/', views.staff_list, name='staff_list'),

    # Category management URLs
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.add_category, name='add_category'),
    path('categories/edit/<int:category_id>/', views.edit_category, name='edit_category'),
    path('categories/delete/<int:category_id>/', views.delete_category, name='delete_category'),  # <-- updated here


    # Supplier management URLs
    path('suppliers/add/', views.add_supplier, name='add_supplier'),
    path('suppliers/edit/<int:pk>/', views.edit_supplier, name='edit_supplier'),
    path('suppliers/delete/<int:pk>/', views.delete_supplier, name='delete_supplier'),

    # Store management URLs
    path('stores/add/', views.add_store, name='add_store'),
    path('stores/edit/<int:pk>/', views.edit_store, name='edit_store'),  # Corrected to use edit_store
    path('stores/delete/<int:pk>/', views.delete_store, name='delete_store'),

    # Export products
    path('export-to-products/', views.export_to_excel, name='export_to_excel'),


    path('manage-tax-discount/', views.manage_tax_discount, name='manage_tax_discount'),

    path('scan/', views.scan_barcode, name='scan_barcode'),
    path('scan-barcode/', views.handle_barcode, name='handle_barcode'),

    path('search-products/', views.search_products, name='search-products'),
]
