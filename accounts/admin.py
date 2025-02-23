# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        ('Store Information', {'fields': ('store',)}),
    )

admin.site.register(CustomUser, CustomUserAdmin)

from django.contrib import admin
from .models import UserProfile

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'store', 'role')
    fields = ('user', 'store', 'role')  # Allow admin to change store and role

admin.site.register(UserProfile, UserProfileAdmin)


from django.contrib import admin

# Customize the admin panel branding
admin.site.site_header = "GLIMS Inventory Administration"
admin.site.site_title = "GLIMS Inventory Admin"
admin.site.index_title = "Welcome to GLIMS Inventory Management"
