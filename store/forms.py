from django import forms
from .models import Product, Staff, Category, Supplier, Store

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'supplier', 'store', 'quantity', 'cost_price', 
                  'selling_price', 'discount', 'product_tax', 'status', 'expiry_date']

    category = forms.ModelChoiceField(queryset=Category.objects.all(), empty_label="Select Category")
    supplier = forms.ModelChoiceField(queryset=Supplier.objects.all(), empty_label="Select Supplier")
    store = forms.ModelChoiceField(queryset=Store.objects.all(), empty_label="Select Store")

    STATUS_CHOICES = [
        (True, 'Active'),
        (False, 'Inactive'),
    ]
    
    status = forms.ChoiceField(choices=STATUS_CHOICES, widget=forms.Select)

    product_tax = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        min_value=0,
        max_value=100,
        initial=0.0,
        label="Product Tax (%)",
        widget=forms.NumberInput(attrs={'placeholder': 'Enter tax %'})
    )

    expiry_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'placeholder': 'Select expiry date'}),
        label="Expiry Date"
    )




from django import forms
from .models import Staff
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from accounts.models import UserProfile

ROLE_CHOICES = [
    ('admin', 'Admin'),
    ('staff', 'Staff'),
    ('cashier', 'Cashier'),
# forms.py
]

from django.contrib.auth import get_user_model
from django import forms
from accounts.models import UserProfile
from .models import Staff

class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['user', 'store', 'role']
        widgets = {
            'store': forms.Select(attrs={'class': 'form-control'}),
            'role': forms.Select(choices=UserProfile.ROLE_CHOICES, attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        User = get_user_model()  # Dynamically fetch the custom user model
        self.fields['user'].queryset = User.objects.all()  # Use the custom user model

    def save(self, commit=True):
        # First, save the Staff instance
        staff = super().save(commit=False)

        if commit:
            staff.save()

        # Now, update the related UserProfile with store and role
        # Use get_or_create in case the UserProfile does not exist
        user_profile, created = UserProfile.objects.get_or_create(user=staff.user)

        # Update store and role fields
        if self.cleaned_data.get('store'):
            user_profile.store = self.cleaned_data['store']
        if self.cleaned_data.get('role'):
            user_profile.role = self.cleaned_data['role']

        # Save the UserProfile instance
        user_profile.save()

        return staff



class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['invoice_no', 'supplier_name', 'supplier_contact', 'description']
        widgets = {
            'invoice_no': forms.TextInput(attrs={'placeholder': 'Invoice No.'}),
            'supplier_name': forms.TextInput(attrs={'placeholder': 'Supplier Name'}),
            'supplier_contact': forms.TextInput(attrs={'placeholder': 'Supplier Contact'}),
            'description': forms.Textarea(attrs={'placeholder': 'Description', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set empty string for None values to allow placeholders
        for field in self.fields.values():
            if field.initial is None:
                field.initial = ""

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['id_no', 'name', 'description']
        widgets = {
            'id_no': forms.TextInput(attrs={'placeholder': 'Enter ID No.'}),
            'name': forms.TextInput(attrs={'placeholder': 'Enter Category Name'}),
            'description': forms.Textarea(attrs={'placeholder': 'Enter Category Description', 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set empty string for None values to allow placeholders
        for field in self.fields.values():
            if field.initial is None:
                field.initial = ""


from .models import Store

class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ['name', 'location', 'manager_name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter store name'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter location'}),
            'manager_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter manager name'}),
        }


from django import forms
from .models import TaxAndDiscount

class TaxAndDiscountForm(forms.ModelForm):
    class Meta:
        model = TaxAndDiscount
        fields = ['tax', 'discount']
        labels = {
            'tax': 'Tax (%)',
            'discount': 'Discount (%)',
        }
        widgets = {
            'tax': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'}),
        }
