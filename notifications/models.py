"""
Modelos para el sistema de notificaciones multi-canal
Soporta Email, SMS y WhatsApp
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class NotificationChannel(models.TextChoices):
    """Tipos de canales de notificación"""
    EMAIL = 'email', 'Email'
    SMS = 'sms', 'SMS'
    WHATSAPP = 'whatsapp', 'WhatsApp'
    PUSH = 'push', 'Push Notification'


class NotificationStatus(models.TextChoices):
    """Estados de las notificaciones"""
    PENDING = 'pending', 'Pendiente'
    SENT = 'sent', 'Enviado'
    DELIVERED = 'delivered', 'Entregado'
    FAILED = 'failed', 'Fallido'
    READ = 'read', 'Leído'


class NotificationType(models.TextChoices):
    """Tipos de notificaciones"""
    ORDER_CONFIRMATION = 'order_confirmation', 'Confirmación de Pedido'
    ORDER_UPDATE = 'order_update', 'Actualización de Pedido'
    SHIPPING_UPDATE = 'shipping_update', 'Actualización de Envío'
    STOCK_ALERT = 'stock_alert', 'Alerta de Stock'
    PROMOTION = 'promotion', 'Promoción'
    SUPPORT_TICKET = 'support_ticket', 'Ticket de Soporte'
    PAYMENT_SUCCESS = 'payment_success', 'Pago Exitoso'
    PAYMENT_FAILED = 'payment_failed', 'Pago Fallido'
    WELCOME = 'welcome', 'Bienvenida'
    PASSWORD_RESET = 'password_reset', 'Recuperación de Contraseña'


class NotificationTemplate(models.Model):
    """Plantillas de notificaciones para cada canal"""
    name = models.CharField(max_length=100, verbose_name="Nombre")
    notification_type = models.CharField(
        max_length=50, 
        choices=NotificationType.choices,
        verbose_name="Tipo de Notificación"
    )
    channel = models.CharField(
        max_length=20,
        choices=NotificationChannel.choices,
        verbose_name="Canal"
    )
    subject = models.CharField(max_length=200, verbose_name="Asunto", blank=True)
    template_body = models.TextField(verbose_name="Cuerpo del Mensaje")
    is_active = models.BooleanField(default=True, verbose_name="Activa")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Plantilla de Notificación"
        verbose_name_plural = "Plantillas de Notificaciones"
        unique_together = ['notification_type', 'channel']

    def __str__(self):
        return f"{self.name} - {self.get_channel_display()}"


class UserNotificationPreference(models.Model):
    """Preferencias de notificación por usuario"""
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='notification_preferences'
    )
    
    # Canales habilitados
    email_enabled = models.BooleanField(default=True, verbose_name="Email habilitado")
    sms_enabled = models.BooleanField(default=False, verbose_name="SMS habilitado")
    whatsapp_enabled = models.BooleanField(default=False, verbose_name="WhatsApp habilitado")
    push_enabled = models.BooleanField(default=True, verbose_name="Push habilitado")
    
    # Tipos de notificaciones habilitadas
    order_notifications = models.BooleanField(default=True, verbose_name="Notificaciones de Pedidos")
    shipping_notifications = models.BooleanField(default=True, verbose_name="Notificaciones de Envío")
    promotional_notifications = models.BooleanField(default=True, verbose_name="Notificaciones Promocionales")
    support_notifications = models.BooleanField(default=True, verbose_name="Notificaciones de Soporte")
    
    # Información de contacto
    phone_number = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    whatsapp_number = models.CharField(max_length=20, blank=True, verbose_name="WhatsApp")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Preferencia de Notificación"
        verbose_name_plural = "Preferencias de Notificaciones"

    def __str__(self):
        return f"Preferencias de {self.user.username}"


class Notification(models.Model):
    """Modelo principal de notificaciones"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    
    # Información básica
    notification_type = models.CharField(
        max_length=50,
        choices=NotificationType.choices,
        verbose_name="Tipo"
    )
    channel = models.CharField(
        max_length=20,
        choices=NotificationChannel.choices,
        verbose_name="Canal"
    )
    
    # Contenido
    subject = models.CharField(max_length=200, verbose_name="Asunto")
    message = models.TextField(verbose_name="Mensaje")
    
    # Metadatos
    recipient_email = models.EmailField(blank=True, verbose_name="Email Destinatario")
    recipient_phone = models.CharField(max_length=20, blank=True, verbose_name="Teléfono Destinatario")
    
    # Estado
    status = models.CharField(
        max_length=20,
        choices=NotificationStatus.choices,
        default=NotificationStatus.PENDING,
        verbose_name="Estado"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado")
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name="Enviado")
    delivered_at = models.DateTimeField(null=True, blank=True, verbose_name="Entregado")
    read_at = models.DateTimeField(null=True, blank=True, verbose_name="Leído")
    
    # Información adicional
    external_id = models.CharField(max_length=100, blank=True, verbose_name="ID Externo")
    error_message = models.TextField(blank=True, verbose_name="Mensaje de Error")
    retry_count = models.IntegerField(default=0, verbose_name="Intentos de Reenvío")
    max_retries = models.IntegerField(default=3, verbose_name="Máximo Intentos")
    
    # Datos adicionales (JSON)
    extra_data = models.JSONField(default=dict, blank=True, verbose_name="Datos Adicionales")

    class Meta:
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.user.username} - {self.get_channel_display()}"

    def mark_as_sent(self):
        """Marcar como enviado"""
        self.status = NotificationStatus.SENT
        self.sent_at = timezone.now()
        self.save()

    def mark_as_delivered(self):
        """Marcar como entregado"""
        self.status = NotificationStatus.DELIVERED
        self.delivered_at = timezone.now()
        self.save()

    def mark_as_failed(self, error_message=""):
        """Marcar como fallido"""
        self.status = NotificationStatus.FAILED
        self.error_message = error_message
        self.retry_count += 1
        self.save()

    def mark_as_read(self):
        """Marcar como leído"""
        if self.status != NotificationStatus.READ:
            self.status = NotificationStatus.READ
            self.read_at = timezone.now()
            self.save()

    @property
    def can_retry(self):
        """Verificar si se puede reintentar"""
        return self.retry_count < self.max_retries and self.status == NotificationStatus.FAILED


class NotificationLog(models.Model):
    """Log de actividades de notificaciones"""
    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name='logs'
    )
    action = models.CharField(max_length=50, verbose_name="Acción")
    details = models.TextField(verbose_name="Detalles")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Timestamp")
    
    class Meta:
        verbose_name = "Log de Notificación"
        verbose_name_plural = "Logs de Notificaciones"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.notification.id} - {self.action}"


class NotificationQueue(models.Model):
    """Cola de notificaciones para procesamiento en batch"""
    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name='queue_entries'
    )
    priority = models.IntegerField(default=5, verbose_name="Prioridad")  # 1 = alta, 5 = normal, 10 = baja
    scheduled_at = models.DateTimeField(default=timezone.now, verbose_name="Programado para")
    processed = models.BooleanField(default=False, verbose_name="Procesado")
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name="Procesado en")
    
    class Meta:
        verbose_name = "Cola de Notificación"
        verbose_name_plural = "Cola de Notificaciones"
        ordering = ['priority', 'scheduled_at']

    def __str__(self):
        return f"Cola: {self.notification.id} - Prioridad {self.priority}"
