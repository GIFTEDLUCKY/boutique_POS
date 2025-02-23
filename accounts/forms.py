from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser  # If you're using a custom user model

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']  # Include all necessary fields

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        # Check if the passwords match
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("The passwords do not match.")

        return cleaned_data
