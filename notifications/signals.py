"""
Signals para automatizar notificaciones en eventos del sistema
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserNotificationPreference
from .services import NotificationFactory
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_user_notification_preferences(sender, instance, created, **kwargs):
    """Crear preferencias de notificación para usuarios nuevos"""
    if created:
        UserNotificationPreference.objects.create(
            user=instance,
            email_enabled=True,
            sms_enabled=False,
            whatsapp_enabled=False,
            push_enabled=True,
            order_notifications=True,
            shipping_notifications=True,
            promotional_notifications=True,
            support_notifications=True
        )
        logger.info(f"Preferencias de notificación creadas para usuario: {instance.username}")


# Signals para órdenes (cuando el modelo Order esté disponible)
try:
    from orders.models import Order
    
    @receiver(post_save, sender=Order)
    def send_order_notifications(sender, instance, created, **kwargs):
        """Enviar notificaciones cuando se crea o actualiza una orden"""
        if created:
            # Nueva orden creada
            NotificationFactory.send_multi_channel_notification(
                user=instance.user,
                notification_type='order_confirmation',
                subject=f'Confirmación de Pedido #{instance.id}',
                message=f'Hola {instance.user.first_name}, tu pedido #{instance.id} ha sido confirmado. Total: ${instance.total}',
                channels=['email', 'sms'],
                extra_data={
                    'order_id': instance.id,
                    'total': str(instance.total),
                    'items_count': instance.items.count()
                }
            )
        else:
            # Orden actualizada
            if hasattr(instance, '_state') and instance._state.fields_cache.get('status') != instance.status:
                NotificationFactory.send_multi_channel_notification(
                    user=instance.user,
                    notification_type='order_update',
                    subject=f'Actualización de Pedido #{instance.id}',
                    message=f'Tu pedido #{instance.id} ha cambiado a: {instance.get_status_display()}',
                    channels=['email'],
                    extra_data={
                        'order_id': instance.id,
                        'new_status': instance.status
                    }
                )
                
except ImportError:
    logger.info("Modelo Order no disponible - signals de órdenes deshabilitados")


# Signals para tickets de soporte
try:
    from support.models import SupportTicket
    
    @receiver(post_save, sender=SupportTicket)
    def send_support_notifications(sender, instance, created, **kwargs):
        """Enviar notificaciones para tickets de soporte"""
        if created:
            # Nuevo ticket creado
            NotificationFactory.send_multi_channel_notification(
                user=instance.user,
                notification_type='support_ticket',
                subject=f'Ticket de Soporte #{instance.ticket_number} Creado',
                message=f'Hola {instance.user.first_name}, hemos recibido tu ticket de soporte. Te contactaremos pronto.',
                channels=['email'],
                extra_data={
                    'ticket_id': instance.id,
                    'ticket_number': instance.ticket_number,
                    'priority': instance.priority
                }
            )
        else:
            # Ticket actualizado
            if hasattr(instance, '_state') and instance._state.fields_cache.get('status') != instance.status:
                NotificationFactory.send_multi_channel_notification(
                    user=instance.user,
                    notification_type='support_ticket',
                    subject=f'Actualización Ticket #{instance.ticket_number}',
                    message=f'Tu ticket #{instance.ticket_number} ha sido actualizado: {instance.get_status_display()}',
                    channels=['email'],
                    extra_data={
                        'ticket_id': instance.id,
                        'ticket_number': instance.ticket_number,
                        'new_status': instance.status
                    }
                )
                
except ImportError:
    logger.info("Modelo SupportTicket no disponible - signals de soporte deshabilitados")


# Signals para alertas de stock
try:
    from shop.models import Product
    
    @receiver(post_save, sender=Product)
    def send_stock_alerts(sender, instance, created, **kwargs):
        """Enviar alertas cuando el stock está bajo"""
        if not created and instance.stock <= 5:  # Stock crítico
            # Notificar a administradores
            admin_users = User.objects.filter(is_superuser=True)
            
            for admin in admin_users:
                NotificationFactory.send_multi_channel_notification(
                    user=admin,
                    notification_type='stock_alert',
                    subject=f'⚠️ Stock Crítico: {instance.name}',
                    message=f'ALERTA: El producto "{instance.name}" tiene solo {instance.stock} unidades en stock.',
                    channels=['email', 'whatsapp'],
                    extra_data={
                        'product_id': instance.id,
                        'product_name': instance.name,
                        'current_stock': instance.stock,
                        'category': instance.category.name if instance.category else 'Sin categoría'
                    }
                )
                
except ImportError:
    logger.info("Modelo Product no disponible - signals de stock deshabilitados")
