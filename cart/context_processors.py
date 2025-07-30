from .models import Cart, SessionCart


def cart(request):
    """Context processor para hacer el carrito disponible en todas las templates"""
    if request.user.is_authenticated:
        cart_obj, created = Cart.objects.get_or_create(user=request.user)
        return {
            'cart': cart_obj,
            'cart_items_count': cart_obj.total_items,
            'cart_total': cart_obj.formatted_total_price,
        }
    else:
        session_cart = SessionCart(request)
        return {
            'cart': session_cart,
            'cart_items_count': len(session_cart),
            'cart_total': f"${int(session_cart.get_total_price()):,}".replace(',', '.'),
        }
