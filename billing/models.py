from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from store.models import Product, Store  # Assuming you have the Product model in the store app

class Invoice(models.Model):
    invoice_number = models.CharField(max_length=20, unique=True)
    customer_name = models.CharField(max_length=100)
    customer_contact = models.CharField(max_length=100, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_total = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.customer_name}"


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.total_price = self.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - {self.quantity} pcs"



from django.db import models
from store.models import Product  # Assuming Product is in the store app
from django.contrib.auth.models import User

from django.db import models
from django.conf import settings
from store.models import Product, Store  # Assuming these are in the store app


# Invoice for Customers
class CustomerInvoice(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=20, unique=True)
    customer_name = models.CharField(max_length=100, blank=True)  # Made it optional
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.customer_name if self.customer_name else 'N/A'}"


# Transactions for a specific Customer Invoice
class TransactionInvoice(models.Model):
    customer_invoice = models.ForeignKey(
        'CustomerInvoice', on_delete=models.CASCADE, related_name='transactions'
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)  # Added this field
    store = models.ForeignKey(Store, on_delete=models.CASCADE)  # Added this field

    def __str__(self):
        return f"Transaction for {self.product.name} (Qty: {self.quantity})"


# A separate Cart model for temporary storage (if applicable)
class Cart(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart item for {self.product.name} - Quantity: {self.quantity}"
