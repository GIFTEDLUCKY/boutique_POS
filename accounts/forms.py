# account/forms.py
from django import forms
from store.models import Store  # Assuming your Store model is in the store app
# accounts/forms.py
from .models import CustomUser, UserProfile
from django.contrib.auth import get_user_model


CustomUser = get_user_model()  # Get the custom user model

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)
    store = forms.ModelChoiceField(queryset=Store.objects.all(), required=True, label="Store")

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'store']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password != password_confirm:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()

            # Create a UserProfile for the new user
            user_profile = UserProfile(user=user)
            user_profile.save()

        return user
