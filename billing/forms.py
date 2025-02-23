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
    product_id = forms.ModelChoiceField(queryset=Product.objects.all(), label="Product")
    quantity_sold = forms.IntegerField(min_value=1, label="Quantity Sold")
    customer_name = forms.CharField(
        max_length=255,
        label="Customer Name",
        required=False,  # Allow blank input
        widget=forms.TextInput(attrs={"placeholder": "Enter customer name"}),
    )

    # Payment method field
    PAYMENT_METHOD_CHOICES = [
        ("Cash", "Cash"),
        ("Card", "Card"),
        ("Momo", "Momo"),
        ("Transfer", "Transfer"),
    ]
    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHOD_CHOICES,
        initial="Cash",
        label="Payment Method",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    def clean_customer_name(self):
        customer_name = self.cleaned_data.get("customer_name", "").strip()
        return customer_name if customer_name else "Customer"  # Default to "Customer"


# billing/forms.py
from django import forms
from .models import Cart

class CartForm(forms.ModelForm):
    class Meta:
        model = Cart
        fields = ['is_paid', 'store']
        widgets = {
            'is_paid': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'store': forms.Select(attrs={'class': 'form-select'}),
        }
