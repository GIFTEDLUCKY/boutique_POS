from django import forms
from .models import PriceHistory

class PriceHistoryForm(forms.ModelForm):
    class Meta:
        model = PriceHistory
        fields = ['product', 'old_cp', 'new_cp', 'old_sp', 'new_sp', 'date_changed']
