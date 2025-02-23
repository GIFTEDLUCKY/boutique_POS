from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import TransactionInvoice

@receiver(post_save, sender=TransactionInvoice)
def update_stock(sender, instance, created, **kwargs):
    if created:
        # You don't need to update the stock here anymore
        pass
