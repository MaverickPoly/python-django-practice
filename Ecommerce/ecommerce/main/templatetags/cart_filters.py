from django import template

register = template.Library()

@register.filter
def multiply(quantity, price):
    """Multiply quantity by price."""
    return quantity * price

@register.filter
def cart_total_price(items):
    """Calculate the total price of all items in the cart."""
    return sum(item.quantity * item.product.price for item in items)