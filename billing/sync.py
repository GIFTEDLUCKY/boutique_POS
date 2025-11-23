import os
import requests
from decimal import Decimal
from django.utils import timezone

# Only setup Django if this script is run directly
if __name__ == "__main__":
    import django
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "boutique_POS.settings")

    django.setup()

from billing.models import TransactionInvoice

SYNC_URL = "https://giftedlucky.pythonanywhere.com/billing/api/sync/sales/"




def full_sync():
    unsynced_sales = TransactionInvoice.objects.filter(is_synced=False)
    if not unsynced_sales.exists():
        print("No unsynced transactions found.")
        return

    print(f"Found {unsynced_sales.count()} unsynced transactions.")
    for transaction in unsynced_sales:
        payload = {
            "id": transaction.id,
            "product": transaction.product.id,
            "quantity": str(transaction.quantity),
            "price": str(transaction.price),
            "subtotal": str(transaction.subtotal),
            "discount": str(transaction.discount),
            "tax": str(transaction.tax),
            "store": transaction.store.id,
            "user": transaction.user.id,
            "created_at": transaction.created_at.isoformat(),
            "cart_id": transaction.cart_id,
            "customer_invoice": transaction.customer_invoice.id if transaction.customer_invoice else None,
        }
        try:
            response = requests.post(SYNC_URL, json=payload, timeout=10)
            if response.status_code in (200, 201):
                transaction.is_synced = True
                transaction.save(update_fields=["is_synced"])
                print(f"Transaction {transaction.id} synced successfully!")
            else:
                print(f"Failed to sync transaction {transaction.id}. Status: {response.status_code}")
        except requests.RequestException as e:
            print(f"Error syncing transaction {transaction.id}: {e}")

# Only run full_sync if script is run standalone
if __name__ == "__main__":
    full_sync()
