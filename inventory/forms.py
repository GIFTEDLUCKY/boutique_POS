from django import forms
from django.db.models import Min
from store.models import Product  
from .models import WarehouseStock  

class WarehouseStockForm(forms.ModelForm):
    # Get unique product IDs by selecting the lowest product_id for each product name
    unique_product_ids = (
        Product.objects.values('name')  # Group by name
        .annotate(product_id=Min('id'))  # Get the lowest product_id per name
        .values_list('product_id', flat=True)  # Extract product_id values
    )

    # Ensure Product queryset only has distinct product names
    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(id__in=unique_product_ids).order_by('name'),
        label="Select Product",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    quantity = forms.IntegerField(
        min_value=1, 
        label="Quantity to Add",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = WarehouseStock
        fields = ['product', 'quantity']



from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction
from .models import StockTransfer, WarehouseStock, Requisition, RequisitionItem


class StockTransferForm(forms.ModelForm):
    requisition = forms.ModelChoiceField(
        queryset=Requisition.objects.filter(status="Approved"),
        required=True,
    )

    product = forms.ModelChoiceField(
        queryset=WarehouseStock.objects.none(),  # Will be set dynamically
        label="Select Product",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    quantity = forms.IntegerField(
        min_value=1,
        label="Quantity to Transfer",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = StockTransfer
        fields = ['requisition', 'product', 'quantity', 'destination_store']

    def __init__(self, *args, **kwargs):
        requisition_instance = kwargs.pop('requisition', None)
        super().__init__(*args, **kwargs)

        # Show only warehouse products with stock available
        self.fields['product'].queryset = WarehouseStock.objects.filter(quantity__gt=0).distinct('product')

        if requisition_instance:
            self.fields['requisition'].initial = requisition_instance
            self.fields['requisition'].queryset = Requisition.objects.filter(id=requisition_instance.id)
            self.fields['requisition'].widget.attrs['readonly'] = True

    def clean(self):
        cleaned_data = super().clean()
        requisition = cleaned_data.get("requisition")
        warehouse_stock = cleaned_data.get("product")
        quantity = cleaned_data.get("quantity")

        if not requisition:
            self.add_error("requisition", "Requisition is required.")

        if warehouse_stock and requisition:
            # Check if this product is approved for the requisition
            requisition_item = RequisitionItem.objects.filter(
                requisition=requisition,
                product=warehouse_stock.product,
                status="Approved"
            ).first()

            if not requisition_item:
                self.add_error("product", f"{warehouse_stock.product.name} is not approved for transfer.")

            elif requisition_item.approved_quantity < quantity:
                self.add_error("quantity", f"Cannot transfer more than approved quantity ({requisition_item.approved_quantity}).")

            # Check warehouse stock
            if warehouse_stock.quantity < quantity:
                self.add_error("quantity", f"Not enough stock for {warehouse_stock.product.name}.")

        return cleaned_data

    def save(self, commit=True):
        """
        Save the stock transfer safely and update WarehouseStock and RequisitionItem.
        """
        instance = super().save(commit=False)
        requisition = self.cleaned_data.get('requisition')
        warehouse_stock = self.cleaned_data.get('product')
        quantity = self.cleaned_data.get('quantity')

        if not warehouse_stock or not isinstance(warehouse_stock, WarehouseStock):
            raise ValidationError("Invalid product selection.")

        instance.product = warehouse_stock.product
        instance.requisition = requisition

        with transaction.atomic():
            # Decrease warehouse stock
            if instance.pk is None:  # New transfer
                if warehouse_stock.quantity < quantity:
                    raise ValidationError(f"Not enough stock for {warehouse_stock.product.name}.")
                warehouse_stock.quantity -= quantity
                warehouse_stock.save()

                # Decrease approved quantity
                requisition_item = RequisitionItem.objects.get(
                    requisition=requisition,
                    product=warehouse_stock.product
                )
                requisition_item.approved_quantity -= quantity
                requisition_item.save()
            else:
                # Existing transfer: handle edit carefully or call reverse_transfer()
                pass

            if commit:
                instance.save()

        return instance

    @staticmethod
    def reverse_transfer(stock_transfer: StockTransfer):
        """
        Reverse a transfer: restore warehouse stock and approved quantity.
        """
        with transaction.atomic():
            warehouse_stock = WarehouseStock.objects.get(product=stock_transfer.product)
            requisition_item = RequisitionItem.objects.get(
                requisition=stock_transfer.requisition,
                product=stock_transfer.product
            )

            warehouse_stock.quantity += stock_transfer.quantity
            warehouse_stock.save()

            requisition_item.approved_quantity += stock_transfer.quantity
            requisition_item.save()

            stock_transfer.delete()



# ================================
# Requisition Forms

from .models import Requisition, RequisitionItem

class RequisitionForm(forms.ModelForm):
    class Meta:
        model = Requisition
        fields = ['store', 'reason']  
    
    def __init__(self, *args, **kwargs):
        super(RequisitionForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


from django import forms
from .models import RequisitionItem, WarehouseStock, Requisition


class RequisitionItemForm(forms.ModelForm):
    requisition = forms.ModelChoiceField(
        queryset=Requisition.objects.all(),
        label="Select Requisition",
        required=True,
        error_messages={'required': 'Please select a requisition.'},
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    product = forms.ModelChoiceField(
        queryset=WarehouseStock.objects.none(),  # Will set dynamically
        label="Select Product",
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Select a Product",
        required=True,
        error_messages={'required': 'Please select a product.'},
    )

    quantity_requested = forms.IntegerField(
        label="Quantity Requested",
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        min_value=1,
        required=True,
        error_messages={'required': 'Please enter a valid quantity.'},
    )

    status = forms.ChoiceField(
    choices=RequisitionItem.STATUS_CHOICES,
    label="Status",
    widget=forms.Select(attrs={'class': 'form-control'}),
    required=True
    )

    approved_quantity = forms.IntegerField(
        label="Approved Quantity",
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        min_value=0,
        required=True
    )

    class Meta:
        model = RequisitionItem
        fields = ['requisition','product', 'quantity_requested']

    def __init__(self, *args, **kwargs):
        store_id = kwargs.pop('store_id', None)
        super().__init__(*args, **kwargs)

        # If store_id is provided (normal forms), filter by store
        if store_id:
            self.fields['product'].queryset = WarehouseStock.objects.filter(
                store_product__store_id=store_id
            ).distinct()
        else:
            # Admin or no store_id: show all WarehouseStock
            self.fields['product'].queryset = WarehouseStock.objects.all()

        # Apply Bootstrap styling
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def clean_product(self):
        product = self.cleaned_data.get('product')
        if not product:
            raise forms.ValidationError("Please select a product.")
        return product

    def clean_quantity_requested(self):
        qty = self.cleaned_data.get('quantity_requested')
        if qty is None or qty <= 0:
            raise forms.ValidationError("Please enter a valid quantity.")
        return qty

    

    

from django import forms

class RequisitionSearchForm(forms.Form):
    requisition_number = forms.CharField(
        label="Requisition Number",
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter requisition number'})
    )
