from django.contrib import admin
from .models import Expenditure, Revenue  # Import Revenue model

admin.site.register(Expenditure)
admin.site.register(Revenue)  # Register Revenue in Django admin
