from django.contrib import admin
from .models import CustomerInvoice, TransactionInvoice

from django.contrib import admin
from billing.models import CustomerInvoice, TransactionInvoice


# Register your models here.
@admin.register(CustomerInvoice)
class CustomerInvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'customer_name', 'total_amount', 'tax', 'discount', 'payment_method', 'created_at')  # Removed 'amount_paid'
    search_fields = ('invoice_number', 'customer_name')
    list_filter = ('created_at',)

class TransactionInvoiceAdmin(admin.ModelAdmin):
    list_display = ('customer_invoice', 'product', 'quantity', 'price', 'discount', 'subtotal', 'store', 'cart_id')  # Include 'cart'
    search_fields = ('cart',)  # You can add 'cart' to search fields if needed

if not admin.site.is_registered(CustomerInvoice):
    admin.site.register(CustomerInvoice, CustomerInvoiceAdmin)

if not admin.site.is_registered(TransactionInvoice):
    admin.site.register(TransactionInvoice, TransactionInvoiceAdmin)


# No need to check if models are registered, @admin.register() already handles it


from django.contrib import admin
from .models import Cart, CartItem

# Register the Cart model
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'store', 'created_at', 'total')
    list_filter = ('store', 'created_at')
    search_fields = ('user__username', 'store__name')

    def total(self, obj):
        return obj.total()
    total.short_description = "Cart Total"

# Register the CartItem model
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'subtotal')
    list_filter = ('cart', 'product')
    search_fields = ('cart__user__username', 'product__name')

    def subtotal(self, obj):
        return obj.subtotal()
    subtotal.short_description = "Item Subtotal"


