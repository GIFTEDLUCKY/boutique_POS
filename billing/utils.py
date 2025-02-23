from django.db.models import Sum
from .models import TransactionInvoice

def get_total_transaction_value():
    total = TransactionInvoice.objects.aggregate(total=Sum('subtotal'))['total']
    return total if total is not None else 0



