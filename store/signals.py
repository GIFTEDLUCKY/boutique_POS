# store/signals.py
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Product
from reports.models import PriceHistory
from boutique_POS.middleware import get_current_user  # Import the helper function


# store/signals.py

@receiver(pre_save, sender=Product)
def track_price_change(sender, instance, **kwargs):
    if instance.pk:  # Check if it's an existing product (not a new one)
        old_product = Product.objects.get(pk=instance.pk)

        # If the price has changed
        if old_product.cost_price != instance.cost_price or old_product.selling_price != instance.selling_price:
            # Get the current user safely
            current_user = get_current_user()

            PriceHistory.objects.create(
                product=instance,
                old_cp=old_product.cost_price,
                new_cp=instance.cost_price,
                old_sp=old_product.selling_price,
                new_sp=instance.selling_price,
                date_changed=timezone.now(),
                changed_by=current_user if current_user else None  # Use current_user if available, else None
            )
