from django import forms
from .models import Product, Staff

# Product Form
from .models import Product, Category, Supplier, Store


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'supplier', 'store', 'quantity', 'cost_price', 'selling_price', 'discount', 'status']

    # Set the category, supplier, and store to pre-fill with default values
    category = forms.ModelChoiceField(queryset=Category.objects.all(), empty_label="Select Category")
    supplier = forms.ModelChoiceField(queryset=Supplier.objects.all(), empty_label="Select Supplier")
    store = forms.ModelChoiceField(queryset=Store.objects.all(), empty_label="Select Store")

    STATUS_CHOICES = [
        (True, 'Active'),
        (False, 'Inactive'),
    ]
    
    status = forms.ChoiceField(choices=STATUS_CHOICES, widget=forms.Select)


# Staff Form
class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['user', 'store', 'role']

        widgets = {
            'store': forms.Select(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
        }


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