from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.apps import apps  # ✅ Lazy import to prevent circular import issues

class CustomUser(AbstractUser):
    store = models.ForeignKey('store.Store', on_delete=models.SET_NULL, null=True, blank=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',  # Custom related name to avoid clash
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_permissions_set',  # Custom related name to avoid clash
        blank=True,
    )

    def __str__(self):
        return self.username


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # ✅ Use AUTH_USER_MODEL
    store = models.ForeignKey('store.Store', on_delete=models.SET_NULL, null=True, blank=True)  # ✅ Still referencing store, but see fix below

    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('cashier', 'Cashier'),
        ('staff', 'Staff'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, null=True, blank=True, default='staff')  # Make role optional

    def __str__(self):
        return f"{self.user.username} - {self.role}"

    def save(self, *args, **kwargs):
        """ Fix potential store import issues by ensuring Store model is loaded """
        if not self.store:
            Store = apps.get_model('store', 'Store')  # ✅ Lazy import of Store model
            self.store = Store.objects.first()  # Set a default store if necessary
        super().save(*args, **kwargs)
