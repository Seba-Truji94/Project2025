from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def subtract(value, arg):
    """Resta dos números"""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def format_price(value):
    """Formatea precio con formato chileno (punto para miles)"""
    try:
        price = float(value)
        return f"${int(price):,}".replace(',', '.')
    except (ValueError, TypeError):
        return "$0"

@register.filter
def format_price_detailed(value):
    """Formatea precio con decimales si los tiene"""
    try:
        price = Decimal(str(value))
        if price % 1 == 0:
            # Sin decimales
            return f"${int(price):,}".replace(',', '.')
        else:
            # Con decimales
            return f"${price:,.2f}".replace(',', '.')
    except (ValueError, TypeError, Exception):
        return "$0"
