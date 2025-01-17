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
    quantity = models.PositiveIntegerField()
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)  # Percentage
    status = models.BooleanField(default=True)  # Active = True, Inactive = False

    @property
    def assumed_profit(self):
        return self.selling_price - self.cost_price

    @property
    def discounted_price(self):
        return self.selling_price - (self.selling_price * self.discount / 100)

    def __str__(self):
        return self.name


from django.contrib.auth.models import User

class Staff(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    store = models.ForeignKey('Store', on_delete=models.CASCADE)
    role = models.CharField(max_length=255)
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

