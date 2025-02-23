from django import template

register = template.Library()

@register.filter
def is_cashier(user):
    return user.groups.filter(name='Cashier').exists()
