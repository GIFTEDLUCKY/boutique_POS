from django.db import models
from store.models import Store  # Ensure you have a Store model
from django.conf import settings

class Expenditure(models.Model):
    CATEGORY_CHOICES = [
        ('rent', 'Rent'),
        ('salary', 'Salary'),
        ('utilities', 'Utilities'),
        ('inventory', 'Inventory'),
        ('others', 'Others'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('mobile_money', 'Mobile Money'),
        ('card', 'Card Payment'),
        ('other', 'Other'),
    ]

    store = models.ForeignKey(Store, on_delete=models.CASCADE)  # Link to store
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)  # User who recorded the expense
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)  # Expense category
    amount = models.DecimalField(max_digits=12, decimal_places=2)  # Amount spent
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash')  # Payment method
    receipt_attachment = models.FileField(upload_to='receipts/', blank=True, null=True)  # Receipt file upload
    description = models.TextField(blank=True, null=True)  # Additional details
    date_added = models.DateField(auto_now_add=True)  # Date when the expense was recorded

    def __str__(self):
        return f"Expenditure: {self.category} - {self.amount} on {self.date_added} via {self.payment_method}"



from django.db import models
from store.models import Store  # Assuming Store model exists
from django.conf import settings

class Revenue(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('mobile_money', 'Mobile Money'),
        ('card', 'Card Payment'),
        ('other', 'Other'),
    ]

    store = models.ForeignKey(Store, on_delete=models.CASCADE)  # Link to store
    amount = models.DecimalField(max_digits=12, decimal_places=2)  # Amount of money added
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash')  # Payment method
    receipt_attachment = models.FileField(upload_to='receipts/', blank=True, null=True)  # Receipt file upload
    description = models.TextField(blank=True, null=True)  # Description for the reason/purpose of deposit
    date_added = models.DateField(auto_now_add=True)  # Date when the money was added
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)  # User who added the revenue

    def __str__(self):
        return f"Revenue for {self.store.name} - {self.amount} added on {self.date_added} via {self.payment_method}"
