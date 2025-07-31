from django.db.models import Sum, Count
from .models import Cart, SessionCart


def cart(request):
    """Context processor para hacer el carrito disponible en todas las templates"""
    if request.user.is_authenticated:
        cart_obj, created = Cart.objects.get_or_create(user=request.user)
        
        # Estadísticas del usuario
        from orders.models import Order
        user_orders = Order.objects.filter(user=request.user)
        
        # Total gastado (órdenes entregadas)
        user_total_spent = user_orders.filter(
            status='delivered'
        ).aggregate(total=Sum('total'))['total'] or 0
        
        # Número total de órdenes
        total_orders = user_orders.count()
        
        # Órdenes pendientes
        pending_orders = user_orders.filter(
            status__in=['pending', 'confirmed', 'processing', 'shipped']
        ).count()
        
        # Promedio de gasto por orden (solo órdenes entregadas)
        delivered_orders_count = user_orders.filter(status='delivered').count()
        avg_order_value = (user_total_spent / delivered_orders_count) if delivered_orders_count > 0 else 0
        
        # Formatear valores
        formatted_total_spent = f"${int(user_total_spent):,}".replace(',', '.')
        formatted_avg_order = f"${int(avg_order_value):,}".replace(',', '.')
        
        # Ahorro estimado vs envío individual (si el carrito supera $15.000)
        cart_value = cart_obj.total_price
        free_shipping_threshold = 15000
        shipping_savings = 3000 if cart_value >= free_shipping_threshold else 0
        formatted_shipping_savings = f"${shipping_savings:,}".replace(',', '.')
        
        return {
            'cart': cart_obj,
            'cart_items_count': cart_obj.total_items,
            'cart_total': cart_obj.formatted_total_price,
            'user_total_spent': formatted_total_spent,
            'user_total_orders': total_orders,
            'user_pending_orders': pending_orders,
            'user_avg_order': formatted_avg_order,
            'shipping_savings': formatted_shipping_savings,
            'qualifies_free_shipping': cart_value >= free_shipping_threshold,
        }
    else:
        session_cart = SessionCart(request)
        cart_value = session_cart.get_total_price()
        free_shipping_threshold = 15000
        shipping_savings = 3000 if cart_value >= free_shipping_threshold else 0
        formatted_shipping_savings = f"${shipping_savings:,}".replace(',', '.')
        
        return {
            'cart': session_cart,
            'cart_items_count': len(session_cart),
            'cart_total': f"${int(session_cart.get_total_price()):,}".replace(',', '.'),
            'user_total_spent': "$0",
            'user_total_orders': 0,
            'user_pending_orders': 0,
            'user_avg_order': "$0",
            'shipping_savings': formatted_shipping_savings,
            'qualifies_free_shipping': cart_value >= free_shipping_threshold,
        }
