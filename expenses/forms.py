from django import forms
from .models import Expenditure
from store.models import Store

class ExpenditureForm(forms.ModelForm):
    store = forms.ModelChoiceField(queryset=Store.objects.all(), required=True)
    category = forms.ChoiceField(choices=Expenditure.CATEGORY_CHOICES, required=True)
    receipt_attachment = forms.FileField(required=False)  # Allow empty uploads

    class Meta:
        model = Expenditure
        fields = ['amount', 'description', 'category', 'store', 'payment_method', 'receipt_attachment']



from django import forms
from .models import Revenue

class RevenueForm(forms.ModelForm):
    class Meta:
        model = Revenue
        fields = ['store', 'amount', 'payment_method', 'receipt_attachment', 'description']


    # If you want to make sure 'added_by' is populated with the current user, 
    # you can set it manually in the view, not in the form.
