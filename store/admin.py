from django.contrib import admin
from .models import Store, Supplier, Category, Product, Staff
from .models import StoreProduct



@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('user', 'store', 'role', 'created_at')
    search_fields = ('user__username', 'store__name', 'role')
    list_filter = ('store', 'role')

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'manager', 'created_at')
    search_fields = ('name', 'location', 'manager_name')
    list_filter = ('created_at',)

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('invoice_no', 'supplier_name', 'supplier_contact', 'description', 'created_at')
    search_fields = ('name', 'contact', 'invoice_no')
    list_filter = ('invoice_no',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id_no', 'name', 'description')
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'supplier', 'store', 'quantity', 'cost_price', 'selling_price', 'discount', 'discounted_price', 'assumed_profit', 'status')
    search_fields = ('name', 'category__name', 'supplier__name')
    list_filter = ('category', 'supplier', 'store', 'status')

    def assumed_profit(self, obj):
        """Method to display assumed profit in the admin"""
        # If assumed_profit is a calculated field, it should not be treated as a callable
        return obj.assumed_profit  # Assuming `assumed_profit` is a Decimal field or property
    assumed_profit.admin_order_field = 'assumed_profit'  # Allow ordering by this field in admin

    def discounted_price(self, obj):
        """Method to display discounted price in the admin"""
        # Assuming `discount` and `selling_price` are fields in the model.
        if obj.discount and obj.selling_price:
            discount_percentage = obj.discount / 100  # Assuming discount is in percentage
            discounted_price = obj.selling_price * (1 - discount_percentage)
            return discounted_price
        return obj.selling_price  # Return original selling price if no discount is applied
    discounted_price.admin_order_field = 'discounted_price'  # Allow ordering by this field in admin


@admin.register(StoreProduct)
class StoreProductAdmin(admin.ModelAdmin):
    list_display = ('store', 'product', 'quantity')
    search_fields = ('store__name', 'product__name')  # This allows searching by store name or product name
