from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    # Other paths...
    path('sales/', views.sales_view, name='sales_view'),

    path('invoice_success/', views.invoice_success, name='invoice_success'),
    path('', views.billing_page, name='billing_page'),
    path('create/', views.create_invoice, name='create_invoice'),
    path('edit_quantity/<int:cart_item_id>/', views.edit_quantity, name='edit_quantity'),
    
    path('delete_item/<int:cart_item_id>/', views.delete_item, name='delete_item'),

    path('billing/edit_quantity/<int:cart_item_id>/', views.edit_quantity, name='edit_quantity'),
    
    path('generate_invoice/<int:invoice_id>/', views.generate_invoice, name='generate_invoice'),
    
    path('invoice_receipt/<int:invoice_id>/', views.invoice_receipt, name='invoice_receipt'),

    
]
