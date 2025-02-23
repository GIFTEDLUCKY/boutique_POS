from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.exceptions import ValidationError
from store.models import Product, Store  # Assuming you have the Product model in the store app
from decimal import Decimal


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
    invoice = models.ForeignKey('CustomerInvoice', related_name='invoice_items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)


    def save(self, *args, **kwargs):
        self.total_price = self.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - {self.quantity} pcs"


import random
import string
from django.conf import settings
from django.db import models

# Function to generate a random invoice number
def generate_invoice_number():
    return "INV" + ''.join(random.choices(string.digits, k=6))

class CustomerInvoice(models.Model):
    invoice_number = models.CharField(
        max_length=20,
        unique=True,  # Ensure every invoice number is unique
        default=generate_invoice_number  # Automatically generate an invoice number
    )
    customer_name = models.CharField(max_length=100)  # Match varchar(100) in MySQL
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set timestamp
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=100)  # Match varchar(50) in MySQL
    tax = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2)
    final_total = models.DecimalField(max_digits=10, decimal_places=2)  # Add this field

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.customer_name}"

    class Meta:
        db_table = "billing_customerinvoice"  # Ensure it matches the MySQL table name



# Transactions for a specific Customer Invoice


#==============================================================================
# TAKING A VERY FRESH APPROACH TO FIXING THE ISSUE OF CART ITEM NOT SHOWING IN THE INVOICE_RECEIPT

# A separate Cart model for temporary storage (if applicable)

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    store = models.ForeignKey('store.Store', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)  # Mark as paid after checkout

    def __str__(self):
        return f"Cart for {self.user.username} at {self.store.name}"

    def total(self):
        return sum(item.subtotal() for item in self.cart_items.all())

    # Method to get the cashier's full name (you can customize this as needed)
    def cashier_name(self):
        return f"{self.user.first_name} {self.user.last_name}"  # Adjust if you have full_name or other attributes in your user model


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='cart_items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def subtotal(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.quantity} of {self.product.name}"
    



from django.core.exceptions import ValidationError
from django.utils.timezone import now
from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal

class TransactionInvoice(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('Cash', 'Cash'),
        ('Card', 'Card'),
        ('Momo', 'Momo'),
        ('Transfer', 'Transfer'),
    ]

    customer_invoice = models.ForeignKey(
        'CustomerInvoice',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    
    prorated_discount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))  # ✅ Added Back
    prorated_tax = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))  # ✅ Added Back
    
    adjusted_final_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    cart_id = models.CharField(max_length=255, blank=True, null=True)

    customer_name = models.CharField(max_length=255, blank=True, null=True)
    payment_method = models.CharField(
        max_length=100, choices=PAYMENT_METHOD_CHOICES, default='Cash'
    )
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return f"Transaction for {self.product.name} (Qty: {self.quantity}) - {self.payment_method}"

    def fetch_global_rates(self):
        """Fetch global discount and tax rates from the store's TaxAndDiscount model."""
        from store.models import TaxAndDiscount
        try:
            tax_discount = TaxAndDiscount.objects.first()
            return (
                Decimal(tax_discount.discount) if tax_discount else Decimal("0.00"),
                Decimal(tax_discount.tax) if tax_discount else Decimal("0.00")
            )
        except TaxAndDiscount.DoesNotExist:
            return Decimal("0.00"), Decimal("0.00")

    def calculate_prorated_values(self):
        """Applies product-specific and global discount/tax correctly."""
        global_discount_rate, global_tax_rate = self.fetch_global_rates()

        # Convert to Decimal
        price_decimal = Decimal(self.price)
        quantity_decimal = Decimal(self.quantity)

        # **Total cost before any discounts**
        total_price = price_decimal * quantity_decimal  # ✅ Correct total price

        # **Product-specific discount (5% of total)**
        product_discount = (Decimal(self.product.discount_rate) / Decimal("100")) * total_price if hasattr(self.product, 'discount_rate') else Decimal("0.00")

        # **Apply product discount first**
        discounted_price = total_price - product_discount

        # **Apply global discount on the discounted total**
        global_discount = (global_discount_rate / Decimal("100")) * discounted_price
        final_discounted_price = discounted_price - global_discount

        # **Product-specific tax (5% of discounted price)**
        product_tax = (Decimal(self.product.tax_rate) / Decimal("100")) * discounted_price if hasattr(self.product, 'tax_rate') else Decimal("0.00")

        # **Apply global tax on final discounted price**
        global_tax = (global_tax_rate / Decimal("100")) * final_discounted_price

        # **Total tax includes both product-specific and global tax**
        total_tax = product_tax + global_tax

        # **Save calculated values (Including Prorated Fields)**
        self.discount = product_discount + global_discount  
        self.prorated_discount = product_discount  # ✅ Added Back
        self.prorated_tax = total_tax  # ✅ Added Back
        self.tax = total_tax
        self.adjusted_final_price = final_discounted_price + total_tax

    def save(self, *args, **kwargs):
        if not self.pk:
            product = self.product
            if product.quantity < self.quantity:
                raise ValidationError(f"Insufficient stock for product: {product.name}")
            product.quantity -= self.quantity
            product.save()

        self.calculate_prorated_values()
        super().save(*args, **kwargs)



