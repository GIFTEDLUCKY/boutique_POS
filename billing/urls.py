from django.urls import path
from . import views


from .views import total_transaction_value


app_name = 'billing'

urlpatterns = [
    # Other paths...
    path('sales/', views.sales_view, name='sales_view'),
    path('reset-sales/', views.reset_sales_page, name='reset_sales'),

    path('invoice_success/', views.invoice_success, name='invoice_success'),
    
    path('create/', views.create_invoice, name='create_invoice'),
    path('edit_quantity/<int:cart_item_id>/', views.edit_quantity, name='edit_quantity'),
    
    path('delete_item/<int:cart_item_id>/', views.delete_item, name='delete_item'),

    path('billing/edit_quantity/<int:cart_item_id>/', views.edit_quantity, name='edit_quantity'),
    
    path('generate_invoice/<int:invoice_id>/', views.generate_invoice, name='generate_invoice'),
    
    path('invoice_receipt/<int:invoice_id>/', views.invoice_receipt, name='invoice_receipt'),


#==============================================================================
# TAKING A VERY FRESH APPROACH TO FIXING THE ISSUE OF CART ITEM NOT SHOWING IN THE INVOICE_RECEIPT

    path('checkout/', views.generate_invoice, name='checkout'),
    path('invoice_receipt/<int:invoice_id>/', views.invoice_receipt, name='invoice_receipt'),

    path("create_invoice/", views.create_invoice, name="create_invoice"),
    path("invoice_receipt/<int:invoice_id>/", views.invoice_receipt, name="invoice_receipt"),
    path('billing/invoice_receipt/<int:invoice_id>/', views.invoice_receipt, name='invoice_receipt'),
    path('save-cart/', views.save_cart, name='save_cart'),

    path('save_cart_id/', views.save_cart_id, name='save_cart_id'),

    path('clear_cart/', views.clear_cart, name='clear_cart'),

    
    path('transactions/all/', views.all_transactions, name='all_transactions'),
    path('transactions/list/', views.transactions_list, name='transactions_list'),
    path('filter_transactions/', views.filter_transactions, name='filter_transactions'),


    path('transaction/search/', views.transaction_search, name='transaction_search'),



    path('re_print_invoice/', views.re_print_invoice, name='re_print_invoice'),  # Correct path





]
