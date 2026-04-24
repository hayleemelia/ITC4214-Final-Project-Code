from decimal import Decimal
from catalog.models import MenuItem


def build_cart_items(cart):
    cart_items = []
    total = Decimal('0.00')

    for item_id, quantity in cart.items():
        try:
            item = MenuItem.objects.get(id=item_id, is_available=True)
            subtotal = item.price * quantity
            total += subtotal

            cart_items.append({
                'item': item,
                'quantity': quantity,
                'subtotal': subtotal,
            })

        except MenuItem.DoesNotExist:
            continue

    return cart_items, total