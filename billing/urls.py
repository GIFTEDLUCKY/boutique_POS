from django.urls import path
from . import views
from .views import total_transaction_value
from .api_views import SyncSalesAPIView

app_name = 'billing'

urlpatterns = [
    # Core sales and invoice routes
    path('sales/', views.sales_view, name='sales_view'),
    path('reset-sales/', views.reset_sales_page, name='reset_sales'),
    path('create/', views.create_invoice, name='create_invoice'),
    path('checkout/', views.generate_invoice, name='generate_invoice'),
    path('generate_invoice/', views.generate_invoice),
    
    path('invoice_success/', views.invoice_success, name='invoice_success'),

    # Invoice receipt (unique route only)
    path('invoice_receipt/<int:invoice_id>/', views.invoice_receipt, name='invoice_receipt'),

    # Cart item management
    path('edit_quantity/<int:cart_item_id>/', views.edit_quantity, name='edit_quantity'),
    path('delete_item/<int:cart_item_id>/', views.delete_item, name='delete_item'),

    # Cart saving & management
    path('save-cart/', views.save_cart, name='save_cart'),
    path('save_cart_id/', views.save_cart_id, name='save_cart_id'),
    path('clear_cart/', views.clear_cart, name='clear_cart'),

    # Transactions
    path('transactions/all/', views.all_transactions, name='all_transactions'),
    path('transactions/list/', views.transactions_list, name='transactions_list'),
    path('filter_transactions/', views.filter_transactions, name='filter_transactions'),
    path('transaction/search/', views.transaction_search, name='transaction_search'),
    path('transactions/export/', views.export_transactions_to_excel, name='export_transactions_to_excel'),

    # Misc
    path('re_print_invoice/', views.re_print_invoice, name='re_print_invoice'),
    path('search_billing_product/', views.search_billing_product, name='search_billing_product'),
    path('search_product/', views.search_product, name='search_product'),

    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),


    #========================================================
    # Customer name and phone number
    path('customers/export/csv/', views.export_customers_csv, name='export_customers_csv'),
    path('customers/export/excel/', views.export_customers_excel, name='export_customers_excel'),
    path('customers/', views.customer_list, name='customer_list'),

    #=============================================================
    # Customer invoice 
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoice/<str:invoice_number>/', views.invoice_detail, name='invoice_detail'),
    path('export-excel/', views.export_invoices_excel, name='export_invoices_excel'),
    path('invoices/today/', views.invoice_list_today, name='invoice_list_today'),
    path('invoice/<int:invoice_id>/void/', views.void_invoice, name='void_invoice'),
    path('invoices/voided/', views.voided_invoices, name='voided_invoices'),

    path('api/sync/sales/', SyncSalesAPIView.as_view(), name='sync-sales'),

    
    # billing/urls.py
    path("open_drawer/<int:invoice_id>/", views.open_drawer_view, name="open_drawer"),

]
