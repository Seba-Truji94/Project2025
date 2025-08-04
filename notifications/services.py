"""
Servicios de notificación para Email, SMS y WhatsApp
"""
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from .models import Notification, NotificationStatus, NotificationLog
from typing import Dict, Any, Optional

# Importaciones opcionales
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    requests = None

try:
    from twilio.rest import Client as TwilioClient
    HAS_TWILIO = True
except ImportError:
    HAS_TWILIO = False
    TwilioClient = None

logger = logging.getLogger(__name__)


class NotificationService:
    """Servicio base para notificaciones"""
    
    def __init__(self):
        self.providers = {
            'email': EmailService(),
            'sms': SMSService(),
            'whatsapp': WhatsAppService(),
        }
    
    def send_notification(self, notification: Notification) -> bool:
        """Enviar notificación usando el canal apropiado"""
        try:
            service = self.providers.get(notification.channel)
            if not service:
                raise ValueError(f"Canal no soportado: {notification.channel}")
            
            success = service.send(notification)
            
            if success:
                notification.mark_as_sent()
                self._log_notification(notification, "SENT", "Notificación enviada exitosamente")
            else:
                notification.mark_as_failed("Error en el envío")
                self._log_notification(notification, "FAILED", "Fallo en el envío")
                
            return success
            
        except Exception as e:
            logger.error(f"Error enviando notificación {notification.id}: {str(e)}")
            notification.mark_as_failed(str(e))
            self._log_notification(notification, "ERROR", str(e))
            return False
    
    def _log_notification(self, notification: Notification, action: str, details: str):
        """Registrar actividad de notificación"""
        NotificationLog.objects.create(
            notification=notification,
            action=action,
            details=details
        )


class EmailService:
    """Servicio de notificaciones por Email"""
    
    def send(self, notification: Notification) -> bool:
        """Enviar email"""
        try:
            # Usar el sistema de email de Django
            send_mail(
                subject=notification.subject,
                message=notification.message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[notification.recipient_email],
                fail_silently=False,
                html_message=self._render_html_template(notification)
            )
            return True
            
        except Exception as e:
            logger.error(f"Error enviando email: {str(e)}")
            return False
    
    def _render_html_template(self, notification: Notification) -> str:
        """Renderizar template HTML para email"""
        try:
            template_name = f"notifications/email/{notification.notification_type}.html"
            context = {
                'user': notification.user,
                'subject': notification.subject,
                'message': notification.message,
                'extra_data': notification.extra_data,
                'notification': notification,
            }
            return render_to_string(template_name, context)
        except:
            # Fallback a template genérico
            return f"""
            <html>
                <body>
                    <h2>{notification.subject}</h2>
                    <p>{notification.message}</p>
                    <hr>
                    <p><small>Galletas Kati - Las más deliciosas de Chile</small></p>
                </body>
            </html>
            """


class SMSService:
    """Servicio de notificaciones por SMS"""
    
    def __init__(self):
        # Configuración para Twilio (ejemplo)
        self.account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', '')
        self.auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', '')
        self.from_number = getattr(settings, 'TWILIO_FROM_NUMBER', '')
        
        # Configuración alternativa para servicios locales chilenos
        self.sms_api_url = getattr(settings, 'SMS_API_URL', '')
        self.sms_api_key = getattr(settings, 'SMS_API_KEY', '')
    
    def send(self, notification: Notification) -> bool:
        """Enviar SMS"""
        try:
            if self.account_sid and self.auth_token:
                return self._send_via_twilio(notification)
            elif self.sms_api_url:
                return self._send_via_local_api(notification)
            else:
                logger.warning("SMS no configurado - simulando envío")
                return self._simulate_sms(notification)
                
        except Exception as e:
            logger.error(f"Error enviando SMS: {str(e)}")
            return False
    
    def _send_via_twilio(self, notification: Notification) -> bool:
        """Enviar SMS usando Twilio"""
        if not HAS_TWILIO:
            logger.warning("Twilio no instalado. Instalar: pip install twilio")
            return False
            
        try:
            from twilio.rest import Client
            
            client = Client(self.account_sid, self.auth_token)
            
            message = client.messages.create(
                body=notification.message,
                from_=self.from_number,
                to=notification.recipient_phone
            )
            
            notification.external_id = message.sid
            return True
            
        except Exception as e:
            logger.error(f"Error con Twilio: {str(e)}")
            return False
    
    def _send_via_local_api(self, notification: Notification) -> bool:
        """Enviar SMS usando API local chilena"""
        try:
            payload = {
                'to': notification.recipient_phone,
                'message': notification.message,
                'api_key': self.sms_api_key
            }
            
            response = requests.post(self.sms_api_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                notification.external_id = result.get('message_id', '')
                return True
            else:
                logger.error(f"Error API SMS: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error con API local SMS: {str(e)}")
            return False
    
    def _simulate_sms(self, notification: Notification) -> bool:
        """Simular envío de SMS para desarrollo"""
        logger.info(f"📱 SMS SIMULADO:")
        logger.info(f"Para: {notification.recipient_phone}")
        logger.info(f"Mensaje: {notification.message}")
        return True


class WhatsAppService:
    """Servicio de notificaciones por WhatsApp"""
    
    def __init__(self):
        # Configuración para WhatsApp Business API
        self.api_url = getattr(settings, 'WHATSAPP_API_URL', '')
        self.api_token = getattr(settings, 'WHATSAPP_API_TOKEN', '')
        self.from_number = getattr(settings, 'WHATSAPP_FROM_NUMBER', '')
        
        # Configuración para servicios como Twilio WhatsApp
        self.twilio_whatsapp = getattr(settings, 'TWILIO_WHATSAPP_ENABLED', False)
    
    def send(self, notification: Notification) -> bool:
        """Enviar mensaje de WhatsApp"""
        try:
            if self.twilio_whatsapp:
                return self._send_via_twilio_whatsapp(notification)
            elif self.api_url:
                return self._send_via_business_api(notification)
            else:
                logger.warning("WhatsApp no configurado - simulando envío")
                return self._simulate_whatsapp(notification)
                
        except Exception as e:
            logger.error(f"Error enviando WhatsApp: {str(e)}")
            return False
    
    def _send_via_twilio_whatsapp(self, notification: Notification) -> bool:
        """Enviar WhatsApp usando Twilio"""
        if not HAS_TWILIO:
            logger.warning("Twilio no instalado. Instalar: pip install twilio")
            return False
            
        try:
            from twilio.rest import Client
            
            client = Client(
                getattr(settings, 'TWILIO_ACCOUNT_SID', ''),
                getattr(settings, 'TWILIO_AUTH_TOKEN', '')
            )
            
            message = client.messages.create(
                body=notification.message,
                from_=f'whatsapp:{self.from_number}',
                to=f'whatsapp:{notification.recipient_phone}'
            )
            
            notification.external_id = message.sid
            return True
            
        except Exception as e:
            logger.error(f"Error con Twilio WhatsApp: {str(e)}")
            return False
    
    def _send_via_business_api(self, notification: Notification) -> bool:
        """Enviar WhatsApp usando Business API"""
        if not HAS_REQUESTS:
            logger.warning("Requests no instalado. Instalar: pip install requests")
            return False
            
        try:
            headers = {
                'Authorization': f'Bearer {self.api_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'messaging_product': 'whatsapp',
                'to': notification.recipient_phone,
                'text': {
                    'body': notification.message
                }
            }
            
            response = requests.post(
                f"{self.api_url}/messages",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                notification.external_id = result.get('messages', [{}])[0].get('id', '')
                return True
            else:
                logger.error(f"Error WhatsApp API: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error con WhatsApp Business API: {str(e)}")
            return False
    
    def _simulate_whatsapp(self, notification: Notification) -> bool:
        """Simular envío de WhatsApp para desarrollo"""
        logger.info(f"💬 WHATSAPP SIMULADO:")
        logger.info(f"Para: {notification.recipient_phone}")
        logger.info(f"Mensaje: {notification.message}")
        return True

    @staticmethod
    def test_configuration():
        """Probar la configuración del sistema"""
        results = {
            'email': True,  # Email siempre disponible con Django
            'sms': HAS_TWILIO or HAS_REQUESTS,
            'whatsapp': HAS_TWILIO or HAS_REQUESTS,
            'dependencies': {
                'requests': HAS_REQUESTS,
                'twilio': HAS_TWILIO,
            }
        }
        
        logger.info("🔍 Estado del sistema de notificaciones:")
        logger.info(f"  📧 Email: {'✅' if results['email'] else '❌'}")
        logger.info(f"  📱 SMS: {'✅' if results['sms'] else '❌'}")
        logger.info(f"  💚 WhatsApp: {'✅' if results['whatsapp'] else '❌'}")
        logger.info(f"  📦 Requests: {'✅' if HAS_REQUESTS else '❌'}")
        logger.info(f"  📞 Twilio: {'✅' if HAS_TWILIO else '❌'}")
        
        return results


class NotificationFactory:
    """Factory para crear notificaciones"""
    
    @staticmethod
    def create_notification(
        user,
        notification_type: str,
        channel: str,
        subject: str,
        message: str,
        extra_data: Optional[Dict[str, Any]] = None,
        recipient_email: str = "",
        recipient_phone: str = ""
    ) -> Notification:
        """Crear una nueva notificación"""
        
        # Usar datos del usuario si no se proporcionan
        if not recipient_email and hasattr(user, 'email'):
            recipient_email = user.email
            
        if not recipient_phone and hasattr(user, 'notification_preferences'):
            prefs = user.notification_preferences
            recipient_phone = prefs.phone_number if channel == 'sms' else prefs.whatsapp_number
        
        notification = Notification.objects.create(
            user=user,
            notification_type=notification_type,
            channel=channel,
            subject=subject,
            message=message,
            recipient_email=recipient_email,
            recipient_phone=recipient_phone,
            extra_data=extra_data or {}
        )
        
        return notification
    
    @staticmethod
    def send_multi_channel_notification(
        user,
        notification_type: str,
        subject: str,
        message: str,
        channels: list = None,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, bool]:
        """Enviar notificación por múltiples canales"""
        
        if channels is None:
            channels = ['email']  # Por defecto solo email
        
        results = {}
        service = NotificationService()
        
        for channel in channels:
            try:
                notification = NotificationFactory.create_notification(
                    user=user,
                    notification_type=notification_type,
                    channel=channel,
                    subject=subject,
                    message=message,
                    extra_data=extra_data
                )
                
                success = service.send_notification(notification)
                results[channel] = success
                
            except Exception as e:
                logger.error(f"Error creando notificación {channel}: {str(e)}")
                results[channel] = False
        
        return results
