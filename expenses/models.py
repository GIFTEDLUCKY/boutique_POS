from django.db import models
from store.models import Store
from django.conf import settings
from PIL import Image, UnidentifiedImageError
import os

class Expenditure(models.Model):
    CATEGORY_CHOICES = [
        ('rent', 'Rent'),
        ('salary', 'Salary'),
        ('utilities', 'Utilities'),
        ('inventory', 'Inventory'),
        ('others', 'Others'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('mobile_money', 'Mobile Money'),
        ('card', 'Card Payment'),
        ('other', 'Other'),
    ]

    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash')
    receipt_attachment = models.FileField(upload_to='receipts/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Expenditure: {self.category} - {self.amount} on {self.date_added} via {self.payment_method}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Save the file first

        if self.receipt_attachment:
            img_path = self.receipt_attachment.path
            try:
                # Open the image
                img = Image.open(img_path)

                # Convert non-JPEG formats to JPEG
                if img.format not in ["JPEG", "JPG"]:
                    new_path = os.path.splitext(img_path)[0] + ".jpg"
                    img = img.convert("RGB")  # Convert to JPEG-compatible mode

                # Resize & compress
                img.thumbnail((1080, 1080))
                img.save(new_path, format="JPEG", quality=70, optimize=True)

                # Replace old file with new one if format was changed
                if new_path != img_path:
                    os.remove(img_path)  # Delete original file
                    self.receipt_attachment.name = new_path.split("media/")[-1]  # Update file path in model
                    super().save(update_fields=["receipt_attachment"])  # Save updated path

            except UnidentifiedImageError:
                print(f"❌ Skipping non-image file: {img_path}")  # Ignore PDFs, text files, etc.
            except Exception as e:
                print(f"❌ Error compressing image: {e}")


# Apply the same logic to the Revenue model

class Revenue(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('mobile_money', 'Mobile Money'),
        ('card', 'Card Payment'),
        ('other', 'Other'),
    ]

    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash')
    receipt_attachment = models.FileField(upload_to='receipts/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    date_added = models.DateField(auto_now_add=True)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Revenue for {self.store.name} - {self.amount} added on {self.date_added} via {self.payment_method}"

from PIL import Image, UnidentifiedImageError
import os

def save(self, *args, **kwargs):
    super().save(*args, **kwargs)

    if self.receipt_attachment:
        img_path = self.receipt_attachment.path
        try:
            # Open the image
            img = Image.open(img_path)
            
            # Convert non-JPEG formats to JPEG
            if img.format not in ["JPEG", "JPG"]:
                new_path = os.path.splitext(img_path)[0] + ".jpg"
                img = img.convert("RGB")  # Convert to JPEG-compatible mode

            # Resize & compress
            img.thumbnail((1080, 1080))
            img.save(new_path, format="JPEG", quality=70, optimize=True)

            # Replace old file with new one if format was changed
            if new_path != img_path:
                os.remove(img_path)  # Delete original file
                self.receipt_attachment.name = new_path.split("media/")[-1]  # Update file path in model
                super().save(update_fields=["receipt_attachment"])  # Save updated path

        except UnidentifiedImageError:
            print(f"❌ Skipping non-image file: {img_path}")  # Ignore PDFs, text files, etc.
        except Exception as e:
            print(f"❌ Error compressing image: {e}")
