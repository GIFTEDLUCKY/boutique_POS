from django.db import models
from django.utils import timezone
from django.conf import settings
from store.models import Product
from decimal import Decimal

class PriceHistory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='price_history')
    old_cp = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    new_cp = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    old_sp = models.DecimalField(max_digits=10, decimal_places=2)
    new_sp = models.DecimalField(max_digits=10, decimal_places=2)
    final_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    date_changed = models.DateTimeField(default=timezone.now)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.new_sp is not None and self.product:
            discount = self.product.discount or Decimal('0.00')
            tax = self.product.product_tax or Decimal('0.00')
            discounted_price = self.new_sp - (self.new_sp * (discount / 100))
            taxed_price = discounted_price + (discounted_price * (tax / 100))
            self.final_price = round(taxed_price, 2)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Price change for {self.product.name} on {self.date_changed}"

    class Meta:
        ordering = ['-date_changed']
