from django.contrib.auth.models import Group
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(m2m_changed, sender=User.groups.through)
def give_staff_admin_access(sender, instance, action, **kwargs):
    """
    Automatically give admin access (is_staff=True)
    to users in the 'staff' group.
    """
    if action in ["post_add", "post_remove", "post_clear"]:
        # If the user is in 'staff' group, grant them admin access
        if instance.groups.filter(name="staff").exists():
            instance.is_staff = True
        else:
            instance.is_staff = False
        instance.save()
