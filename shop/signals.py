from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from orders.models import Order, OrderItem
from shop.models import Product, ProductStock


# Guardar el estado anterior de la orden antes de que se modifique
@receiver(pre_save, sender=Order)
def cache_old_order_status(sender, instance, **kwargs):
    """
    Guarda el estado anterior de la orden para detectar cambios
    """
    if instance.pk:
        try:
            old_order = Order.objects.get(pk=instance.pk)
            instance._old_status = old_order.status
        except Order.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=Order)
def handle_order_status_change(sender, instance, created, **kwargs):
    """
    Maneja los cambios de estado de las órdenes para actualizar el stock automáticamente
    """
    if created:
        # Nueva orden creada - reservar stock
        reserve_stock_for_order(instance)
    else:
        # Orden existente - manejar cambios de estado
        old_status = getattr(instance, '_old_status', None)
        
        if old_status and old_status != instance.status:
            handle_order_status_stock_update(instance, old_status, instance.status)


def reserve_stock_for_order(order):
    """
    Reserva stock cuando se crea una nueva orden
    """
    for item in order.items.all():
        product = item.product
        
        # Verificar que hay suficiente stock
        if product.stock >= item.quantity:
            # Guardar stock anterior
            previous_stock = product.stock
            
            # Reducir stock
            product.stock -= item.quantity
            product.save()
            
            # Registrar movimiento de stock
            ProductStock.objects.create(
                product=product,
                movement_type='sale',
                quantity=-item.quantity,  # Negativo porque es una salida
                previous_stock=previous_stock,
                new_stock=product.stock,
                reason=f'Venta - Pedido #{order.order_number}',
                reference=order.order_number,
                user=order.user
            )
        else:
            # Stock insuficiente - registrar alerta pero no bloquear la orden
            ProductStock.objects.create(
                product=product,
                movement_type='adjustment',
                quantity=0,
                previous_stock=product.stock,
                new_stock=product.stock,
                reason=f'ALERTA: Stock insuficiente para pedido #{order.order_number}. Solicitado: {item.quantity}, Disponible: {product.stock}',
                reference=order.order_number,
                user=order.user
            )


def handle_order_status_stock_update(order, old_status, new_status):
    """
    Maneja los cambios de stock según el cambio de estado de la orden
    """
    # Si la orden se cancela, devolver el stock
    if new_status == 'cancelled' and old_status in ['pending', 'confirmed', 'processing']:
        restore_stock_for_cancelled_order(order)
    
    # Si una orden cancelada se reactiva, volver a reservar stock
    elif old_status == 'cancelled' and new_status in ['pending', 'confirmed', 'processing']:
        reserve_stock_for_order(order)
    
    # Si la orden se entrega, confirmar la salida (ya está descontado, solo registrar)
    elif new_status == 'delivered' and old_status != 'delivered':
        confirm_delivery_stock_movement(order)


def restore_stock_for_cancelled_order(order):
    """
    Devuelve el stock cuando una orden se cancela
    """
    for item in order.items.all():
        product = item.product
        previous_stock = product.stock
        
        # Devolver stock
        product.stock += item.quantity
        product.save()
        
        # Registrar movimiento de stock
        ProductStock.objects.create(
            product=product,
            movement_type='return',
            quantity=item.quantity,  # Positivo porque es una devolución
            previous_stock=previous_stock,
            new_stock=product.stock,
            reason=f'Devolución por cancelación - Pedido #{order.order_number}',
            reference=order.order_number,
            user=order.user
        )


def confirm_delivery_stock_movement(order):
    """
    Registra la confirmación de entrega (el stock ya fue descontado)
    """
    for item in order.items.all():
        product = item.product
        
        # Solo registrar el movimiento de confirmación
        ProductStock.objects.create(
            product=product,
            movement_type='sale',
            quantity=0,  # Cero porque ya fue descontado
            previous_stock=product.stock,
            new_stock=product.stock,
            reason=f'Entrega confirmada - Pedido #{order.order_number}',
            reference=order.order_number,
            user=order.user
        )


# Manejar eliminación de órdenes (devolver stock)
@receiver(post_delete, sender=Order)
def handle_order_deletion(sender, instance, **kwargs):
    """
    Devuelve el stock cuando se elimina una orden
    """
    if instance.status not in ['cancelled', 'delivered']:
        # Solo devolver stock si la orden no estaba cancelada o entregada
        for item in instance.items.all():
            product = item.product
            previous_stock = product.stock
            
            # Devolver stock
            product.stock += item.quantity
            product.save()
            
            # Registrar movimiento de stock
            ProductStock.objects.create(
                product=product,
                movement_type='return',
                quantity=item.quantity,
                previous_stock=previous_stock,
                new_stock=product.stock,
                reason=f'Devolución por eliminación de orden #{instance.order_number}',
                reference=instance.order_number,
                user=instance.user
            )


# Funciones auxiliares para gestión manual de stock

def manual_stock_adjustment(product, new_stock, reason, user=None, reference=''):
    """
    Función auxiliar para ajustes manuales de stock
    """
    previous_stock = product.stock
    difference = new_stock - previous_stock
    
    # Actualizar stock del producto
    product.stock = new_stock
    product.save()
    
    # Determinar tipo de movimiento
    if difference > 0:
        movement_type = 'entry'
        quantity = difference
    elif difference < 0:
        movement_type = 'exit'
        quantity = difference  # Negativo
    else:
        movement_type = 'adjustment'
        quantity = 0
    
    # Registrar movimiento
    ProductStock.objects.create(
        product=product,
        movement_type=movement_type,
        quantity=quantity,
        previous_stock=previous_stock,
        new_stock=new_stock,
        reason=reason,
        reference=reference,
        user=user
    )
    
    return {
        'previous_stock': previous_stock,
        'new_stock': new_stock,
        'difference': difference,
        'movement_type': movement_type
    }


def bulk_stock_update(products_data, reason, user=None, reference=''):
    """
    Actualización masiva de stock
    products_data: lista de tuplas (product, new_stock)
    """
    results = []
    
    for product, new_stock in products_data:
        result = manual_stock_adjustment(product, new_stock, reason, user, reference)
        result['product'] = product
        results.append(result)
    
    return results


def check_low_stock_alerts():
    """
    Función para verificar productos con stock bajo
    """
    from django.core.mail import send_mail
    from django.conf import settings
    
    low_stock_products = Product.objects.filter(
        stock__lte=5,  # Stock crítico
        available=True
    )
    
    critical_stock_products = Product.objects.filter(
        stock=0,  # Sin stock
        available=True
    )
    
    if low_stock_products.exists() or critical_stock_products.exists():
        # Crear alertas o enviar emails
        alert_message = f"""
        ALERTA DE STOCK:
        - Productos con stock crítico (≤5): {low_stock_products.count()}
        - Productos sin stock: {critical_stock_products.count()}
        
        Productos críticos:
        """
        
        for product in low_stock_products:
            alert_message += f"\n- {product.name}: {product.stock} unidades"
        
        # Aquí podrías enviar email, crear notificaciones, etc.
        print(alert_message)  # Por ahora solo imprimir
        
        return {
            'low_stock_count': low_stock_products.count(),
            'critical_stock_count': critical_stock_products.count(),
            'low_stock_products': list(low_stock_products),
            'critical_stock_products': list(critical_stock_products)
        }
    
    return None
