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
from django.db import models, transaction
from django.conf import settings
from store.models import Store

def generate_sequential_number():
    """Generate the next sequential 10-digit requisition number."""
    last = Requisition.objects.order_by('-id').first()
    if last and last.requisition_number:
        last_num = int(last.requisition_number)
        next_num = last_num + 1
    else:
        next_num = 1
    return str(next_num).zfill(10)


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
        default=generate_sequential_number
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

    if not self.product:
        errors['product'] = _("Product must be selected.")
    else:
        if self.quantity_requested is not None and self.product.quantity < self.quantity_requested:
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
    quantity = models.PositiveIntegerField()
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
        """Handle forward transfer and automatic reversal if reversed_quantity increased."""
        is_update = self.pk is not None
        old_reversal_qty = 0
        if is_update:
            old = StockTransfer.objects.get(pk=self.pk)
            old_reversal_qty = old.reversed_quantity

        self.full_clean()  # Validate fields

        with transaction.atomic():
            self._forward_transfer()

            # Save the StockTransfer instance
            super().save(*args, **kwargs)

            # Handle automatic reversal if reversed_quantity increased
            new_reversal_qty = self.reversed_quantity
            if new_reversal_qty > old_reversal_qty:
                delta = new_reversal_qty - old_reversal_qty
                if not self.reversed_by:
                    raise ValidationError("Reversed by user must be set for reversal.")
                self._apply_reversal(delta, self.reversed_by)

    def _forward_transfer(self):
        """Perform the forward stock transfer to the store."""
        if not self.requisition or self.requisition.status.lower() != "approved":
            raise ValidationError("Requisition must be approved before stock can be transferred.")

        if not all(item.status == "Approved" for item in self.requisition.items.all()):
            raise ValidationError("Some requisition items are not approved; cannot transfer stock.")

        if not self.warehouse_stock or not self.warehouse_stock.product:
            raise ValidationError("No warehouse stock selected or linked to a product.")

        product = self.warehouse_stock.product
        qty = self.quantity

        # Check warehouse stock availability
        if self.warehouse_stock.quantity < qty:
            raise ValidationError(f"Not enough stock for {product.name} in warehouse.")

        # Deduct from warehouse
        self.warehouse_stock.quantity -= qty
        self.warehouse_stock.save()

        # Add to store
        store_product, _ = StoreProduct.objects.get_or_create(product=product, store=self.destination_store, defaults={"quantity": 0})
        store_product.quantity += qty
        store_product.save()

        # Ensure Product table entry is updated
        product_entry, created = Product.objects.get_or_create(
            name=product.name,
            store=self.destination_store,
            defaults={
                "quantity": qty,
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
            product_entry.quantity += qty
            product_entry.save()

    def _apply_reversal(self, quantity, user):
        """Apply reversal of stock back to warehouse and deduct from store."""
        if quantity <= 0 or quantity > (self.quantity - self.reversed_quantity):
            raise ValidationError("Invalid reversal quantity.")

        product = self.warehouse_stock.product

        # Deduct from store
        store_product = StoreProduct.objects.filter(product=product, store=self.destination_store).first()
        if not store_product or store_product.quantity < quantity:
            raise ValidationError("Not enough stock in store to reverse.")

        store_product.quantity -= quantity
        store_product.save()

        # Update warehouse stock
        self.warehouse_stock.quantity += quantity
        self.warehouse_stock.save()

        # Update Product table
        product_entry = Product.objects.filter(name=product.name, store=self.destination_store).first()
        if product_entry:
            product_entry.quantity -= quantity
            product_entry.save()

        # Track reversal
        self.reversed_quantity += quantity
        self.reversed_by = user
        super().save(update_fields=['reversed_quantity', 'reversed_by'])

        logger.info(f"Reversed {quantity} units of {product.name} back to warehouse.")
