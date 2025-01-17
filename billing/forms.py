from django import forms
from .models import Invoice, InvoiceItem

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['customer_name', 'customer_contact', 'total_amount', 'discount', 'tax', 'final_total']

# forms.py in your billing app
from django import forms
from store.models import Product

class SaleForm(forms.Form):
    product_id = forms.ModelChoiceField(queryset=Product.objects.all(), label='Product')
    quantity_sold = forms.IntegerField(min_value=1, label='Quantity Sold')
    customer_name = forms.CharField(max_length=255, label='Customer Name')
