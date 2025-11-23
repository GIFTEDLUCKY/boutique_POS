from django import forms
from .models import PriceHistory

class PriceHistoryForm(forms.ModelForm):
    class Meta:
        model = PriceHistory
        fields = ['product', 'old_cp', 'new_cp', 'old_sp', 'new_sp', 'date_changed']  # keep old_cp, old_sp, date_changed for JS/display

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Preload related store for dropdown efficiency
        self.fields['product'].queryset = self.fields['product'].queryset.select_related('store')
        self.fields['product'].label_from_instance = lambda obj: f"{obj.name} ({obj.store.name})"

        # Make old_cp, old_sp, and date_changed readonly
        for field in ['old_cp', 'old_sp', 'date_changed']:
            self.fields[field].widget.attrs['readonly'] = True
            self.fields[field].widget.attrs['style'] = 'background-color:#f0f0f0;'
