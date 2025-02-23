from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

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
    user = models.OneToOneField('accounts.CustomUser', on_delete=models.CASCADE)
    store = models.ForeignKey('store.Store', on_delete=models.SET_NULL, null=True, blank=True)  # Make store optional
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('cashier', 'Cashier'),
        ('staff', 'Staff'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, null=True, blank=True, default='staff')  # Make role optional

    def __str__(self):
        return f"{self.user.username} - {self.role}"
