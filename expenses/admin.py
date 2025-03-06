from django.contrib import admin
from .models import Expenditure, Revenue

# -------------------- Expenditure Admin --------------------
class ExpenditureAdmin(admin.ModelAdmin):
    list_display = ('category', 'amount', 'payment_method', 'date_added', 'store')  # Correct fields
    search_fields = ('category', 'amount', 'description', 'store__name')  # You can search by category, amount, description, and store name
    list_filter = ('category', 'payment_method', 'date_added', 'store')  # Filter by these fields
    ordering = ('-date_added',)  # Order by date in descending order

# -------------------- Revenue Admin --------------------
class RevenueAdmin(admin.ModelAdmin):
    list_display = ('amount', 'payment_method', 'date_added', 'store')  # Correct fields
    search_fields = ('amount', 'description', 'store__name')  # You can search by amount, description, and store name
    list_filter = ('payment_method', 'date_added', 'store')  # Filter by these fields
    ordering = ('-date_added',)  # Order by date in descending order

# Register models with their customized admin classes
admin.site.register(Expenditure, ExpenditureAdmin)
admin.site.register(Revenue, RevenueAdmin)
