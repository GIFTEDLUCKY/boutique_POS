from django.contrib import admin
from django.contrib.admin import AdminSite

class MyAdminSite(AdminSite):
    site_header = 'GLIMS Inventory'  # This will change the header name
    site_title = 'GLIMS Inventory Admin'  # This changes the title in the browser tab
    index_title = 'Welcome to GLIMS Inventory Admin'  # This will change the title of the homepage

# Register the custom admin site
admin_site = MyAdminSite(name='myadmin')
