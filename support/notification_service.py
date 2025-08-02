from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import SupportNotification, SupportMessage
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """Servicio para gestionar notificaciones del sistema de soporte"""
    
    @staticmethod
    def notify_ticket_created(ticket):
        """Notificar creación de ticket"""
        # Notificar al usuario
        NotificationService._create_user_notification(
            ticket.user,
            ticket,
            'ticket_created',
            'Ticket creado exitosamente',
            f'Tu ticket #{ticket.ticket_number} ha sido creado y está siendo revisado por nuestro equipo.'
        )
        
        # Enviar email al usuario
        NotificationService._send_email_notification(
            ticket.user,
            'Ticket de Soporte Creado - Galletas Kati',
            'support/emails/ticket_created.html',
            {'ticket': ticket}
        )
    
    @staticmethod
    def notify_new_message(ticket, message, recipients=None):
        """Notificar nuevo mensaje en ticket"""
        if not recipients:
            # Notificar al usuario del ticket y al staff asignado
            recipients = [ticket.user]
            if ticket.assigned_to and ticket.assigned_to != message.sender:
                recipients.append(ticket.assigned_to)
        
        for recipient in recipients:
            if recipient != message.sender:  # No notificar al que envió el mensaje
                sender_name = message.sender.get_full_name() if message.sender else "Sistema"
                
                NotificationService._create_user_notification(
                    recipient,
                    ticket,
                    'new_message',
                    f'Nuevo mensaje en ticket #{ticket.ticket_number}',
                    f'{sender_name} ha enviado un nuevo mensaje en tu ticket.'
                )
                
                # Enviar email
                NotificationService._send_email_notification(
                    recipient,
                    f'Nuevo mensaje en ticket #{ticket.ticket_number} - Galletas Kati',
                    'support/emails/new_message.html',
                    {'ticket': ticket, 'message': message, 'recipient': recipient}
                )
    
    @staticmethod
    def notify_status_changed(ticket, old_status, new_status, changed_by):
        """Notificar cambio de estado"""
        status_names = dict(ticket.STATUS_CHOICES)
        old_status_name = status_names.get(old_status, old_status)
        new_status_name = status_names.get(new_status, new_status)
        
        # Crear mensaje de seguimiento automático
        SupportMessage.create_status_change_message(
            ticket, changed_by, old_status, new_status
        )
        
        # Notificar al usuario
        NotificationService._create_user_notification(
            ticket.user,
            ticket,
            'status_changed',
            f'Estado del ticket #{ticket.ticket_number} actualizado',
            f'El estado de tu ticket ha cambiado de "{old_status_name}" a "{new_status_name}".'
        )
        
        # Si el ticket se marca como resuelto, crear mensaje de cierre
        if new_status == 'resolved':
            SupportMessage.create_closure_message(ticket, changed_by)
            NotificationService.notify_ticket_resolved(ticket, changed_by)
        
        # Enviar email
        NotificationService._send_email_notification(
            ticket.user,
            f'Estado actualizado: Ticket #{ticket.ticket_number} - Galletas Kati',
            'support/emails/status_changed.html',
            {
                'ticket': ticket, 
                'old_status': old_status_name, 
                'new_status': new_status_name,
                'changed_by': changed_by
            }
        )
    
    @staticmethod
    def notify_ticket_resolved(ticket, resolved_by):
        """Notificar resolución de ticket"""
        NotificationService._create_user_notification(
            ticket.user,
            ticket,
            'ticket_resolved',
            f'Ticket #{ticket.ticket_number} resuelto',
            'Tu ticket ha sido marcado como resuelto. Revisa la respuesta de nuestro equipo.'
        )
        
        # Enviar email de resolución
        NotificationService._send_email_notification(
            ticket.user,
            f'Ticket Resuelto: #{ticket.ticket_number} - Galletas Kati',
            'support/emails/ticket_resolved.html',
            {'ticket': ticket, 'resolved_by': resolved_by}
        )
    
    @staticmethod
    def notify_ticket_assigned(ticket, assigned_to, assigned_by):
        """Notificar asignación de ticket"""
        # Crear mensaje de seguimiento
        old_assigned = getattr(ticket, '_original_assigned_to', None)
        SupportMessage.create_assignment_change_message(
            ticket, assigned_by, old_assigned, assigned_to
        )
        
        # Notificar al nuevo asignado
        if assigned_to:
            NotificationService._create_user_notification(
                assigned_to,
                ticket,
                'assigned',
                f'Ticket #{ticket.ticket_number} asignado a ti',
                f'Se te ha asignado el ticket "{ticket.subject}" para su atención.'
            )
            
            # Email al staff asignado
            NotificationService._send_email_notification(
                assigned_to,
                f'Ticket Asignado: #{ticket.ticket_number} - Galletas Kati',
                'support/emails/ticket_assigned.html',
                {'ticket': ticket, 'assigned_by': assigned_by}
            )
        
        # Notificar al usuario del ticket
        assigned_name = assigned_to.get_full_name() if assigned_to else "nuestro equipo"
        NotificationService._create_user_notification(
            ticket.user,
            ticket,
            'assigned',
            f'Ticket #{ticket.ticket_number} asignado',
            f'Tu ticket ha sido asignado a {assigned_name} para su atención personalizada.'
        )
    
    @staticmethod
    def _create_user_notification(user, ticket, notification_type, title, message):
        """Crear notificación en base de datos"""
        try:
            return SupportNotification.create_notification(
                user=user,
                ticket=ticket,
                notification_type=notification_type,
                title=title,
                message=message
            )
        except Exception as e:
            logger.error(f"Error creando notificación: {e}")
            return None
    
    @staticmethod
    def _send_email_notification(user, subject, template, context):
        """Enviar notificación por email"""
        try:
            if not user.email:
                logger.warning(f"Usuario {user.username} no tiene email configurado")
                return False
            
            html_message = render_to_string(template, context)
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@galletaskati.com'),
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False
            )
            
            logger.info(f"Email enviado a {user.email}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Error enviando email a {user.email}: {e}")
            return False
    
    @staticmethod
    def get_unread_notifications(user, limit=10):
        """Obtener notificaciones no leídas del usuario"""
        return SupportNotification.objects.filter(
            user=user, 
            is_read=False
        ).order_by('-created_at')[:limit]
    
    @staticmethod
    def mark_notifications_as_read(user, ticket=None):
        """Marcar notificaciones como leídas"""
        notifications = SupportNotification.objects.filter(user=user, is_read=False)
        if ticket:
            notifications = notifications.filter(ticket=ticket)
        
        updated = notifications.update(is_read=True)
        logger.info(f"Marcadas {updated} notificaciones como leídas para {user.username}")
        return updated
