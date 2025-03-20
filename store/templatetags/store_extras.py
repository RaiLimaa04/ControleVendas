from django import template
from django.db.models import Sum

register = template.Library()

@register.filter
def subtract(value, arg):
    """Subtract the arg from the value."""
    try:
        return value - arg
    except (ValueError, TypeError):
        return value
    
@register.filter
def multiply(value, arg):
    """Multiply the value by the arg."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return value
    
@register.simple_tag
def get_total_payments(sale):
    """Get total payments for a sale."""
    total = sale.payments.aggregate(Sum('amount'))['amount__sum'] or 0
    return total