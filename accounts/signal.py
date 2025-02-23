from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, UserProfile

# Create UserProfile when a CustomUser is created
@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

# Save the UserProfile when the CustomUser is saved (optional, but ensures the profile is updated)
@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    # This will save the associated profile after the user is saved
    instance.userprofile.save()
