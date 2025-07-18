from django.contrib import admin
from .models import PriceHistory

@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'old_cp', 'new_cp', 'old_sp', 'new_sp', 'final_price', 'date_changed', 'changed_by')
    list_filter = ('product', 'changed_by', 'date_changed')
    search_fields = ('product__name', 'changed_by__username')
    ordering = ('-date_changed',)
