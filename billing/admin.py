from django.contrib import admin
from .models import CustomerInvoice, TransactionInvoice


# Register your models here.
@admin.register(CustomerInvoice)



class CustomerInvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'customer_name', 'total_amount', 'tax', 'discount', 'payment_method', 'created_at')  # Removed 'amount_paid'
    search_fields = ('invoice_number', 'customer_name')
    list_filter = ('created_at',)

class TransactionInvoiceAdmin(admin.ModelAdmin):
    list_display = ('customer_invoice', 'product', 'quantity', 'price', 'discount', 'subtotal', 'store')  # Updated 'total' to 'subtotal'

if not admin.site.is_registered(CustomerInvoice):
    admin.site.register(CustomerInvoice, CustomerInvoiceAdmin)

if not admin.site.is_registered(TransactionInvoice):
    admin.site.register(TransactionInvoice, TransactionInvoiceAdmin)