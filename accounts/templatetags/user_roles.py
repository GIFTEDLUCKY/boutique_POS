from django import template

register = template.Library()

@register.filter
def has_role(user, role_name):
    return user.groups.filter(name__in=[role_name, "Cashier"]).exists()

@register.filter
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()
