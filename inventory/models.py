from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models, transaction
from django.contrib.auth import get_user_model
from store.models import Store, Product, StoreProduct
from django.utils import timezone
from django.conf import settings
import random

User = get_user_model()  # ✅ Ensure correct user model usage

# -------------------- Warehouse Stock Model --------------------
# models.py
from django.db import models

class WarehouseStock(models.Model):
    product = models.ForeignKey('store.Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)  # Warehouse-level quantity

    def __str__(self):
        return f"{self.product.name} - {self.quantity} in warehouse"



# -------------------- Requisition Model --------------------
def generate_unique_number():
    """Generate a unique 10-digit requisition number."""
    return str(random.randint(10**9, 10**10 - 1))  # 10-digit random number


class Requisition(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    requisition_number = models.CharField(
        max_length=10, 
        unique=True, 
        null=True, 
        blank=True, 
        editable=False, 
        default=generate_unique_number  # ✅ Use function directly
    )
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='requisitions')
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        permissions = [
            ("can_create_requisition", "Can create requisition"),
            ("can_view_requisition", "Can view requisition"),
        ]

    def update_status(self):
        """Update requisition status based on item approvals."""
        items = self.items.all()
        if all(item.status == 'Rejected' for item in items):
            self.status = 'Rejected'
        elif any(item.status == 'Approved' for item in items):
            self.status = 'Approved'
        else:
            self.status = 'Pending'
        self.save()

    def __str__(self):
        return f"Requisition {self.requisition_number} - {self.store.name}"


# -------------------- Requisition Item Model --------------------
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db import models

class RequisitionItem(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    requisition = models.ForeignKey(
        Requisition, on_delete=models.CASCADE, related_name='items', blank=True, null=True
    )
    product = models.ForeignKey(
        WarehouseStock,  # ✅ Change this from StoreProduct to WarehouseStock
        on_delete=models.CASCADE,
        related_name='requisition_items'
    )
    quantity_requested = models.PositiveIntegerField()
    approved_quantity = models.PositiveIntegerField(default=0, blank=True)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='Pending'
    )

    class Meta:
        permissions = [
            ("can_view_requisition_item", "Can view requisition item"),
        ]

    def clean(self):
        """Validate fields before saving."""
        errors = {}

        if not self.requisition:
            errors['requisition'] = _("Requisition must be selected before adding items.")

        # ✅ Check if warehouse stock exists
        if self.product.quantity < self.quantity_requested:
            errors['quantity_requested'] = _(
                f"Not enough stock in warehouse for {self.product.product.name}. "
                f"Available: {self.product.quantity}"
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """Run validation before saving."""
        self.full_clean()  # ✅ Ensures all validations run
        super().save(*args, **kwargs)
        self.requisition.update_status()  # ✅ Update requisition status when item status changes

    def __str__(self):
        return f"{self.product.product.name} - {self.quantity_requested} units"



import logging
from django.db import transaction
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.conf import settings
from store.models import Store, StoreProduct, Product
from .models import Requisition, WarehouseStock

logger = logging.getLogger(__name__)

class StockTransfer(models.Model):
    quantity = models.PositiveIntegerField()  # Ensure quantity is positive
    transfer_date = models.DateTimeField(default=timezone.now)
    destination_store = models.ForeignKey(Store, on_delete=models.CASCADE)
    warehouse_stock = models.ForeignKey(WarehouseStock, on_delete=models.CASCADE)
    requisition = models.ForeignKey(Requisition, on_delete=models.CASCADE)
    transferred_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='transfers'
    )
    
    # Reversal fields
    reversed_quantity = models.PositiveIntegerField(default=0)
    reversed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='reversals'
    )

    def __str__(self):
        product_name = self.warehouse_stock.product.name if self.warehouse_stock and self.warehouse_stock.product else "Unknown Product"
        return f"Transfer {self.id} - {product_name} to {self.destination_store}"

    def save(self, *args, **kwargs):
        self.full_clean()  # Validate model fields before saving
        with transaction.atomic():
            if not self.requisition or self.requisition.status.lower() != "approved":
                raise ValidationError("Requisition must be approved before stock can be transferred")

            # 🔴 NEW CHECK: Ensure all requisition items are approved
            if not all(item.status == "Approved" for item in self.requisition.items.all()):
                raise ValidationError("Stock transfer cannot proceed because some requisition items are not approved")

            if not self.warehouse_stock:
                raise ValidationError("No warehouse stock selected for transfer")

            product = getattr(self.warehouse_stock, 'product', None)
            if not product:
                raise ValidationError("No product linked to warehouse stock")

            # Transfer stock to destination store
            product_entry, created = Product.objects.get_or_create(
                name=product.name,
                store=self.destination_store,
                defaults={
                    "quantity": self.quantity,
                    "cost_price": product.cost_price,
                    "selling_price": product.selling_price,
                    "discount": product.discount,
                    "product_tax": product.product_tax,
                    "status": product.status,
                    "expiry_date": product.expiry_date,
                    "category": product.category,
                    "supplier": product.supplier,
                }
            )

            if not created:
                product_entry.quantity += self.quantity
                product_entry.save()

            # Ensure StoreProduct entry exists
            store_product, _ = StoreProduct.objects.get_or_create(
                product=product, store=self.destination_store, defaults={"quantity": 0}
            )
            store_product.quantity += self.quantity
            store_product.save()

        super().save(*args, **kwargs)


    def reverse_transfer(self, quantity, user):
        with transaction.atomic():
            if quantity <= 0 or quantity > (self.quantity - self.reversed_quantity):
                raise ValidationError("Invalid reversal quantity.")

            # ✅ Ensure self.product exists before using .product
            if not self.product:
                raise ValidationError("Stock transfer record is missing product details.")

            product_instance = self.product.product  # Assign before use

            store_product = StoreProduct.objects.filter(product=product_instance, store=self.destination_store).first()
            if not store_product or store_product.quantity < quantity:
                raise ValidationError("Not enough stock available in the store to reverse.")
            
            warehouse_stock = WarehouseStock.objects.filter(product=product_instance).first()
            if not warehouse_stock:
                raise ValidationError("No warehouse stock found for this product.")
            
            store_product.quantity -= quantity
            store_product.save()
            
            warehouse_stock.quantity += quantity
            warehouse_stock.save()
            
            self.reversed_quantity += quantity
            self.reversed_by = user
            self.save()

            logger.info(f"Reversed {quantity} units of {product_instance.name} back to warehouse.")
