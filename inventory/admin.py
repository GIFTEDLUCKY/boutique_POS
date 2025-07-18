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



@admin.register(Requisition)
class RequisitionAdmin(admin.ModelAdmin):
    list_display = ('requisition_number', 'store', 'added_by', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('store__name', 'added_by__username')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs  # Superusers can see all requisitions
        if hasattr(request.user, 'store'):  # Ensure user has a store
            return qs.filter(store__manager=request.user)
        return qs.none()  # Return an empty queryset if no store is assigned

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        # Check if 'status' field exists in the form base fields
        if 'status' in form.base_fields:
            # Make the 'status' field read-only for store managers
            if not request.user.is_superuser and hasattr(request.user, 'store'):
                form.base_fields['status'].disabled = True  # Disable the status field (grayed out)

        return form


# -------------------- RequisitionItem Admin --------------------

from django.contrib import admin
from .models import RequisitionItem
@admin.register(RequisitionItem)
class RequisitionItemAdmin(admin.ModelAdmin):
    list_display = ('requisition', 'product', 'quantity_requested', 'status')
    search_fields = ('product__name',)

    # Read-only status for store manager
    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return self.readonly_fields + ('status', 'approved_quantity')
        return self.readonly_fields

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        # Make status field read-only and apply gray color for store managers
        if not request.user.is_superuser:
            if 'status' in form.base_fields:
                form.base_fields['status'].widget.attrs['readonly'] = 'readonly'
                form.base_fields['status'].widget.attrs['style'] = 'background-color: #f0f0f0;'  # Grayed out

        return form

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs  # Superusers can see all requisition items
        return qs.filter(requisition__store__manager=request.user)


# -------------------- StockTransfer Admin --------------------
from django.contrib import admin, messages
from django.db import transaction
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

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs  
        return qs.filter(destination_store__manager=request.user)

    def save_model(self, request, obj, form, change):
        """Ensure product exists and update stock during transfer."""
        try:
            with transaction.atomic():
                # ✅ Ensure `warehouse_stock` is valid before accessing `product`
                if not obj.warehouse_stock or not obj.warehouse_stock.product:
                    self.message_user(request, "⚠ No product linked to warehouse stock.", level=messages.ERROR)
                    return

                product = obj.warehouse_stock.product
                quantity = obj.quantity
                destination_store = obj.destination_store

                # ✅ Check if warehouse has enough stock
                warehouse_stock = WarehouseStock.objects.filter(product=product).first()
                if not warehouse_stock or warehouse_stock.quantity < quantity:
                    self.message_user(
                        request, 
                        f"⚠ Not enough stock for {product.name} in warehouse. Transfer not saved.", 
                        level=messages.ERROR
                    )
                    return

                # ✅ Deduct from warehouse stock
                warehouse_stock.quantity -= quantity
                warehouse_stock.save()

                # ✅ Ensure product exists in destination store
                store_product, created = StoreProduct.objects.get_or_create(
                    product=product, store=destination_store,
                    defaults={'quantity': 0}
                )

                # ✅ Update quantity
                store_product.quantity += quantity
                store_product.save()

                # ✅ Save the transfer record
                super().save_model(request, obj, form, change)

                # ✅ Success message
                self.message_user(request, f"✅ {quantity} {product.name}(s) successfully transferred to {destination_store.name}!", level=messages.SUCCESS)

        except Exception as e:
            self.message_user(request, f"❌ Error: {str(e)}. Transfer failed.", level=messages.ERROR)
            logger.error(f"❌ Transfer Error: {str(e)}")


    @admin.action(description="Reverse selected stock transfers")
    def reverse_transfer(self, request, queryset):
        """Reverses stock transfer back to warehouse."""
        for transfer in queryset:
            try:
                with transaction.atomic():
                    # ✅ Ensure transfer.warehouse_stock exists before accessing product
                    if not transfer.warehouse_stock:
                        self.message_user(request, "⚠ Stock transfer record is missing warehouse stock details.", level=messages.ERROR)
                        continue

                    product_instance = transfer.warehouse_stock.product  # ✅ Corrected reference
                    reversed_quantity = transfer.reversed_quantity  # Ensure we're using the correct quantity

                    if reversed_quantity is None or reversed_quantity <= 0:
                        self.message_user(request, f"⚠ Invalid reversal quantity for {product_instance.name}.", level=messages.ERROR)
                        continue

                    # Get warehouse stock
                    warehouse_stock = WarehouseStock.objects.filter(product=product_instance).first()
                    if not warehouse_stock:
                        self.message_user(request, f"⚠ No warehouse stock found for {product_instance.name}.", level=messages.ERROR)
                        continue

                    # Get store product stock
                    store_product = StoreProduct.objects.filter(product=product_instance, store=transfer.destination_store).first()
                    if not store_product:
                        self.message_user(request, f"⚠ Product not found in {transfer.destination_store.name}.", level=messages.ERROR)
                        continue

                    # Ensure enough stock exists in the store for reversal
                    if store_product.quantity < reversed_quantity:
                        self.message_user(request, f"⚠ Not enough stock in {transfer.destination_store.name} to reverse {reversed_quantity} units.", level=messages.ERROR)
                        continue

                    # Perform reversal
                    print(f"🔄 Before Reversal: Store {store_product.store.name} Stock = {store_product.quantity}, Warehouse Stock = {warehouse_stock.quantity}")

                    store_product.quantity -= reversed_quantity
                    store_product.save()

                    warehouse_stock.quantity += reversed_quantity
                    warehouse_stock.save()

                    # Update the Product model (reduce quantity)
                    product_entry = Product.objects.filter(name=product_instance.name, store=transfer.destination_store).first()
                    if product_entry:
                        product_entry.quantity -= reversed_quantity
                        product_entry.save()
                        print(f"🛑 Product Model Updated: {product_entry.name} Quantity = {product_entry.quantity}")

                    print(f"✅ After Reversal: Store {store_product.store.name} Stock = {store_product.quantity}, Warehouse Stock = {warehouse_stock.quantity}")

                    # Log the reversal and mark as reversed
                    transfer.reversal_log = f"Reversed {reversed_quantity} {product_instance.name}(s) back to warehouse."
                    transfer.is_reversed = True  # Mark as reversed
                    transfer.save()

                    self.message_user(request, f"✅ Successfully reversed {reversed_quantity} {product_instance.name}(s) back to warehouse.", level=messages.SUCCESS)

            except Exception as e:
                self.message_user(request, f"❌ Error reversing stock transfer: {str(e)}", level=messages.ERROR)
