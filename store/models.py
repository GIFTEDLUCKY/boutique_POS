from django.db import models
from django.conf import settings
class TestModel(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Store(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    manager_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey('Category', on_delete=models.CASCADE, default=1)
    supplier = models.ForeignKey('Supplier', on_delete=models.CASCADE, default=1)
    store = models.ForeignKey('Store', on_delete=models.CASCADE, default=1)
    quantity = models.PositiveIntegerField()  # Tracks current stock
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)  # Product Discount (%) 
    product_tax = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)  # Product Tax (%) 
    status = models.BooleanField(default=True)  # Active = True, Inactive = False
    expiry_date = models.DateField(null=True, blank=True)  # Optional expiry date field

    @property
    def assumed_profit(self):
        """Calculates assumed profit per unit (excluding tax)."""
        discounted_price = self.selling_price - (self.selling_price * self.discount / 100)
        return discounted_price - self.cost_price

    @property
    def discounted_price(self):
        """Calculates discounted price per unit."""
        return self.selling_price - (self.selling_price * self.discount / 100)

    @property
    def taxed_price(self):
        """Calculates price after applying product tax on the discounted price."""
        return self.discounted_price + (self.discounted_price * self.product_tax / 100)

    @property
    def is_stock_low(self):
        """Checks if stock is low (10 units or fewer)."""
        return self.quantity <= 10

    def reduce_stock(self, quantity_sold):
        """
        Reduces the stock when a product is sold.
        Args:
            quantity_sold (int): The quantity of product sold.
        Raises:
            ValueError: If quantity_sold exceeds available stock.
        """
        if self.quantity < quantity_sold:
            raise ValueError(f"Insufficient stock for product '{self.name}'. Available: {self.quantity}, Requested: {quantity_sold}.")
        self.quantity -= quantity_sold
        self.save()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']  # Order products alphabetically by name




from django.contrib.auth.models import User
ROLE_CHOICES = [
    ('admin', 'Admin'),
    ('staff', 'Staff'),
    ('cashier', 'Cashier'),
]

class Staff(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    store = models.ForeignKey('Store', on_delete=models.CASCADE)
    role = models.CharField(max_length=255, choices=ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.store.name}'
    
    
class Supplier(models.Model):
    invoice_no = models.CharField(max_length=225, unique=True)
    supplier_name = models.CharField(max_length=255)
    supplier_contact = models.CharField(max_length=15)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.supplier_name
    
    

from django.db import models

class Category(models.Model):
    id_no = models.CharField(max_length=100, unique=True)  # ID No.
    name = models.CharField(max_length=255)  # Category Name
    description = models.TextField()  # Description

    def __str__(self):
        return self.name


class StoreProduct(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product.name} - {self.store.name}"


from django.core.exceptions import ValidationError

class TaxAndDiscount(models.Model):
    name = models.CharField(max_length=50, default="Default Settings")  # Optional, to distinguish settings
    tax = models.DecimalField(max_digits=5, decimal_places=2, default=0.0, help_text="Tax percentage (e.g., 10 for 10%)")
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.0, help_text="Discount percentage (e.g., 5 for 5%)")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}: Tax {self.tax}%, Discount {self.discount}%"

    def clean(self):
        if self.tax < 0 or self.tax > 100:
            raise ValidationError("Tax must be between 0 and 100.")
        if self.discount < 0 or self.discount > 100:
            raise ValidationError("Discount must be between 0 and 100.")

    def save(self, *args, **kwargs):
        self.full_clean()  # Ensure validation is run before saving
        super().save(*args, **kwargs)


