"""
Tareas asíncronas para envío de notificaciones usando Celery
"""
from celery import shared_task
from django.contrib.auth.models import User
from .models import Notification, NotificationQueue
from .services import NotificationService, NotificationFactory
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_notification_task(self, notification_id):
    """Tarea para enviar una notificación individual"""
    try:
        notification = Notification.objects.get(id=notification_id)
        service = NotificationService()
        success = service.send_notification(notification)
        
        if not success and notification.can_retry:
            # Reintentar después de un tiempo
            raise self.retry(countdown=60 * (notification.retry_count + 1))
        
        return success
        
    except Notification.DoesNotExist:
        logger.error(f"Notificación {notification_id} no encontrada")
        return False
    except Exception as e:
        logger.error(f"Error enviando notificación {notification_id}: {str(e)}")
        raise self.retry(exc=e, countdown=60)


@shared_task
def process_notification_queue():
    """Procesar cola de notificaciones pendientes"""
    pending_notifications = NotificationQueue.objects.filter(
        processed=False
    ).order_by('priority', 'scheduled_at')[:50]  # Procesar hasta 50 por vez
    
    processed_count = 0
    
    for queue_item in pending_notifications:
        try:
            # Enviar notificación
            send_notification_task.delay(queue_item.notification.id)
            
            # Marcar como procesado
            queue_item.processed = True
            queue_item.processed_at = timezone.now()
            queue_item.save()
            
            processed_count += 1
            
        except Exception as e:
            logger.error(f"Error procesando cola {queue_item.id}: {str(e)}")
    
    logger.info(f"Procesadas {processed_count} notificaciones de la cola")
    return processed_count


@shared_task
def send_bulk_notification(user_ids, notification_type, subject, message, channels=None):
    """Enviar notificación masiva a múltiples usuarios"""
    if channels is None:
        channels = ['email']
    
    users = User.objects.filter(id__in=user_ids)
    sent_count = 0
    
    for user in users:
        try:
            results = NotificationFactory.send_multi_channel_notification(
                user=user,
                notification_type=notification_type,
                subject=subject,
                message=message,
                channels=channels
            )
            
            if any(results.values()):  # Si al menos un canal fue exitoso
                sent_count += 1
                
        except Exception as e:
            logger.error(f"Error enviando notificación masiva a usuario {user.id}: {str(e)}")
    
    logger.info(f"Notificación masiva enviada a {sent_count}/{len(user_ids)} usuarios")
    return sent_count


@shared_task
def send_promotional_campaign(campaign_data):
    """Enviar campaña promocional"""
    subject = campaign_data.get('subject', 'Promoción Especial')
    message = campaign_data.get('message', '')
    channels = campaign_data.get('channels', ['email'])
    target_users = campaign_data.get('target_users', 'all')
    
    # Obtener usuarios objetivo
    if target_users == 'all':
        users = User.objects.filter(is_active=True)
    elif target_users == 'subscribers':
        users = User.objects.filter(
            is_active=True,
            notification_preferences__promotional_notifications=True
        )
    else:
        users = User.objects.filter(id__in=target_users)
    
    # Filtrar usuarios que permiten notificaciones promocionales
    users = users.filter(
        notification_preferences__promotional_notifications=True
    )
    
    sent_count = 0
    
    for user in users:
        try:
            # Verificar preferencias del usuario para cada canal
            prefs = getattr(user, 'notification_preferences', None)
            if not prefs:
                continue
            
            user_channels = []
            for channel in channels:
                if channel == 'email' and prefs.email_enabled:
                    user_channels.append('email')
                elif channel == 'sms' and prefs.sms_enabled:
                    user_channels.append('sms')
                elif channel == 'whatsapp' and prefs.whatsapp_enabled:
                    user_channels.append('whatsapp')
            
            if user_channels:
                results = NotificationFactory.send_multi_channel_notification(
                    user=user,
                    notification_type='promotion',
                    subject=subject,
                    message=message,
                    channels=user_channels,
                    extra_data=campaign_data.get('extra_data', {})
                )
                
                if any(results.values()):
                    sent_count += 1
                    
        except Exception as e:
            logger.error(f"Error enviando campaña a usuario {user.id}: {str(e)}")
    
    logger.info(f"Campaña promocional enviada a {sent_count} usuarios")
    return sent_count


@shared_task
def cleanup_old_notifications():
    """Limpiar notificaciones antiguas"""
    from django.utils import timezone
    from datetime import timedelta
    
    # Eliminar notificaciones enviadas hace más de 30 días
    cutoff_date = timezone.now() - timedelta(days=30)
    
    deleted_count = Notification.objects.filter(
        created_at__lt=cutoff_date,
        status__in=['sent', 'delivered', 'read']
    ).delete()[0]
    
    logger.info(f"Eliminadas {deleted_count} notificaciones antiguas")
    return deleted_count


@shared_task
def send_welcome_notification(user_id):
    """Enviar notificación de bienvenida a nuevo usuario"""
    try:
        user = User.objects.get(id=user_id)
        
        subject = f"¡Bienvenido a Galletas Kati, {user.first_name}!"
        message = f"""
        Hola {user.first_name},
        
        ¡Bienvenido a Galletas Kati! Estamos emocionados de tenerte como parte de nuestra familia.
        
        Descubre nuestras deliciosas galletas artesanales hechas con ingredientes naturales chilenos.
        
        ¡Disfruta de tu primera compra!
        
        Equipo Galletas Kati
        """
        
        NotificationFactory.send_multi_channel_notification(
            user=user,
            notification_type='welcome',
            subject=subject,
            message=message,
            channels=['email'],
            extra_data={
                'welcome_bonus': True,
                'first_purchase_discount': 10
            }
        )
        
        logger.info(f"Notificación de bienvenida enviada a {user.email}")
        return True
        
    except User.DoesNotExist:
        logger.error(f"Usuario {user_id} no encontrado para notificación de bienvenida")
        return False
    except Exception as e:
        logger.error(f"Error enviando bienvenida a usuario {user_id}: {str(e)}")
        return False


@shared_task
def send_order_status_update(order_id, new_status):
    """Enviar notificación de actualización de estado de orden"""
    try:
        from orders.models import Order
        order = Order.objects.get(id=order_id)
        
        status_messages = {
            'confirmed': 'Tu pedido ha sido confirmado y está siendo preparado.',
            'processing': 'Tu pedido está siendo preparado con mucho cariño.',
            'shipped': 'Tu pedido está en camino. ¡Pronto lo tendrás!',
            'delivered': '¡Tu pedido ha sido entregado! Esperamos que disfrutes nuestras galletas.',
            'cancelled': 'Tu pedido ha sido cancelado. Si tienes dudas, contáctanos.'
        }
        
        message = status_messages.get(new_status, f'Tu pedido ha sido actualizado a: {new_status}')
        
        NotificationFactory.send_multi_channel_notification(
            user=order.user,
            notification_type='order_update',
            subject=f'Actualización de Pedido #{order.id}',
            message=f"Hola {order.user.first_name}, {message}",
            channels=['email', 'sms'],
            extra_data={
                'order_id': order.id,
                'new_status': new_status,
                'tracking_number': getattr(order, 'tracking_number', '')
            }
        )
        
        return True
        
    except Exception as e:
        logger.error(f"Error enviando actualización de orden {order_id}: {str(e)}")
        return False
