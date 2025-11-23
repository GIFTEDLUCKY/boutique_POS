from django.contrib import admin
from .models import WarehouseStock, Requisition, RequisitionItem, StockTransfer
from store.models import StoreProduct

from django.contrib import admin
from django.db.models import Min
from store.models import Product
from .models import WarehouseStock
from .forms import WarehouseStockForm

class WarehouseStockAdmin(admin.ModelAdmin):
    form = WarehouseStockForm  # Use the corrected form in Django Admin

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "product":
            unique_product_ids = (
                Product.objects.values('name')
                .annotate(product_id=Min('id'))
                .values_list('product_id', flat=True)
            )
            kwargs["queryset"] = Product.objects.filter(id__in=unique_product_ids).order_by('name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(WarehouseStock, WarehouseStockAdmin)


# -------------------- Requisition Admin --------------------
@admin.register(Requisition)
class RequisitionAdmin(admin.ModelAdmin):
    list_display = ('requisition_number', 'store', 'added_by', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('store__name', 'added_by__username')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs  # Superusers see all
        # Staff can see requisitions for their store only
        if hasattr(request.user, 'store'):
            return qs.filter(store=request.user.store)
        return qs.none()

    def get_exclude(self, request, obj=None):
        exclude = super().get_exclude(request, obj) or []
        return exclude + ['store', 'added_by']

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Read-only status for staff
        if 'status' in form.base_fields and not request.user.is_superuser:
            form.base_fields['status'].disabled = True
        return form

    def save_model(self, request, obj, form, change):
        """Set store and added_by automatically on creation"""
        if not change or not obj.pk:
            obj.added_by = request.user
            if hasattr(request.user, 'store'):
                obj.store = request.user.store
        super().save_model(request, obj, form, change)


# -------------------- RequisitionItem Admin --------------------
from django.contrib import admin
from .models import RequisitionItem
from .forms import RequisitionItemForm

@admin.register(RequisitionItem)
class RequisitionItemAdmin(admin.ModelAdmin):
    form = RequisitionItemForm  # <-- use your custom form
    list_display = ('requisition', 'product', 'quantity_requested', 'status')

    search_fields = ('product__name',)

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return self.readonly_fields + ('status', 'approved_quantity')
        return self.readonly_fields

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not request.user.is_superuser and 'status' in form.base_fields:
            form.base_fields['status'].widget.attrs['readonly'] = 'readonly'
            form.base_fields['status'].widget.attrs['style'] = 'background-color: #f0f0f0;'
        return form

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Staff can see items for their store's requisitions
        if hasattr(request.user, 'store'):
            return qs.filter(requisition__store=request.user.store)
        return qs.none()


# -------------------- StockTransfer Admin --------------------
from django.contrib import admin, messages
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import StockTransfer, WarehouseStock
from store.models import Product, StoreProduct
import logging

# Define logger
logger = logging.getLogger(__name__)

@admin.register(StockTransfer)
class StockTransferAdmin(admin.ModelAdmin):
    list_display = ('get_product_name', 'quantity', 'requisition', 'destination_store', 'transfer_date', 'reversed_quantity')
    search_fields = ('warehouse_stock__product__name',)
    actions = ["reverse_transfer"]

    def get_product_name(self, obj):
        if obj.warehouse_stock and obj.warehouse_stock.product:
            return obj.warehouse_stock.product.name
        return "Unknown Product"
    
    get_product_name.short_description = "Product Name"

    def save_model(self, request, obj, form, change):
        """Simply save the object; stock logic is in model."""
        super().save_model(request, obj, form, change)

    @admin.action(description="Reverse selected stock transfers")
    def reverse_transfer(self, request, queryset):
        for transfer in queryset:
            try:
                reversible_qty = transfer.quantity - transfer.reversed_quantity
                if reversible_qty <= 0:
                    self.message_user(
                        request, 
                        f"⚠ Transfer {transfer.id} has nothing left to reverse.",
                        level=messages.WARNING
                    )
                    continue

                # Trigger model reversal
                transfer.reverse_transfer(quantity=reversible_qty, user=request.user)

                self.message_user(
                    request,
                    f"✅ Successfully reversed {reversible_qty} units of {transfer.warehouse_stock.product.name} back to warehouse.",
                    level=messages.SUCCESS
                )
            except Exception as e:
                self.message_user(request, f"❌ Error reversing transfer {transfer.id}: {str(e)}", level=messages.ERROR)
