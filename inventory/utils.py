from django.db import transaction
from .models import StockTransfer, WarehouseStock, RequisitionItem

def reverse_transfer(stock_transfer):
    """
    Reverse a stock transfer: restore warehouse stock and requisition item approved quantity,
    then delete the transfer record.
    """
    with transaction.atomic():
        # Restore warehouse stock
        ws = WarehouseStock.objects.get(product=stock_transfer.product)
        ws.quantity += stock_transfer.quantity
        ws.save()

        # Restore requisition item approved quantity
        ri = RequisitionItem.objects.get(
            requisition=stock_transfer.requisition,
            product=stock_transfer.product
        )
        ri.approved_quantity += stock_transfer.quantity
        ri.save()

        # Delete the transfer record
        stock_transfer.delete()
