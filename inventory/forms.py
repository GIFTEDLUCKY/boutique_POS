from django import forms
from store.models import Product, StoreProduct  
from .models import WarehouseStock  

class WarehouseStockForm(forms.ModelForm):
    # Ensure only unique master products appear in the dropdown
    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(
            id__in=StoreProduct.objects.values_list('master_product_id', flat=True)
        ).distinct().order_by('name'),  
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
from .models import StockTransfer, WarehouseStock, Requisition, StoreProduct

class StockTransferForm(forms.ModelForm):
    requisition = forms.ModelChoiceField(
        queryset=Requisition.objects.filter(status="Approved"),
        required=False,
    )

    product = forms.ModelChoiceField(
        queryset=WarehouseStock.objects.none(),  # Set dynamically later
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

        # Fetch only unique products from WarehouseStock that have quantity available
        self.fields['product'].queryset = WarehouseStock.objects.filter(quantity__gt=0).distinct('product')

        if requisition_instance:
            self.fields['requisition'].initial = requisition_instance
            self.fields['requisition'].queryset = Requisition.objects.filter(id=requisition_instance.id)
            self.fields['requisition'].widget.attrs['readonly'] = True

    def clean(self):
        """Validate requisition and stock availability"""
        cleaned_data = super().clean()
        requisition = cleaned_data.get("requisition")
        product = cleaned_data.get("product")
        quantity = cleaned_data.get("quantity")

        if not requisition:
            self.add_error("requisition", "Requisition is required.")

        if product:
            # Validate stock availability in WarehouseStock
            warehouse_stock = WarehouseStock.objects.filter(product=product.product).first()

            if warehouse_stock and warehouse_stock.quantity >= quantity:
                # Stock is available
                pass
            else:
                self.add_error("quantity", f"Not enough stock for {product.product.name} in warehouse.")
        
        return cleaned_data

    def save(self, commit=True):
        """Explicitly set requisition and product before saving"""
        instance = super().save(commit=False)
        if self.cleaned_data.get('requisition'):
            instance.requisition = self.cleaned_data['requisition']

        if self.cleaned_data.get('product') and isinstance(self.cleaned_data['product'], WarehouseStock):
            instance.product = self.cleaned_data['product'].product  # Extract Product from WarehouseStock
        else:
            raise ValidationError("Invalid product selection: Must be a WarehouseStock instance.")

        if commit:
            instance.save()
        return instance


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
from django.db.models import Min
from .models import RequisitionItem, StoreProduct

class RequisitionItemForm(forms.ModelForm):
    product = forms.ModelChoiceField(
        queryset=StoreProduct.objects.none(),  # Initially empty
        label="Select Product",
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Select a Product",
    )

    class Meta:
        model = RequisitionItem
        fields = ['product', 'quantity_requested']

    def __init__(self, *args, **kwargs):
        store_id = kwargs.pop('store_id', None)  # Expecting store_id to be passed
        super().__init__(*args, **kwargs)

        if store_id:
            # Fetch distinct master_product_id entries linked to warehouse stock
            unique_products = StoreProduct.objects.filter(
                store_id=store_id
            ).exclude(warehouse_stock_id__isnull=True)  # Exclude NULL warehouse_stock

            unique_product_ids = (
                unique_products.values('master_product_id')
                .annotate(first_id=Min('id'))
                .values_list('first_id', flat=True)
            )

            # Apply the filtered product list to the queryset
            self.fields['product'].queryset = StoreProduct.objects.filter(id__in=unique_product_ids)

        # Apply Bootstrap styling
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    def clean_product(self):
        """Ensure a product is selected."""
        product = self.cleaned_data.get('product')
        if not product:
            raise forms.ValidationError("This field is required.")
        return product
