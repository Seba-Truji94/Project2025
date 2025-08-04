"""
Administración del sistema de notificaciones
"""
from django.contrib import admin
from .models import (
    Notification, UserNotificationPreference, 
    NotificationTemplate, NotificationLog, NotificationQueue
)


@admin.register(UserNotificationPreference)
class UserNotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'email_enabled', 'sms_enabled', 'whatsapp_enabled',
        'order_notifications', 'promotional_notifications'
    ]
    list_filter = [
        'email_enabled', 'sms_enabled', 'whatsapp_enabled',
        'order_notifications', 'promotional_notifications'
    ]
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']


class NotificationLogInline(admin.TabularInline):
    model = NotificationLog
    readonly_fields = ['action', 'details', 'timestamp']
    extra = 0


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'notification_type', 'channel', 'status',
        'created_at', 'sent_at'
    ]
    list_filter = [
        'notification_type', 'channel', 'status', 'created_at'
    ]
    search_fields = ['user__username', 'user__email', 'subject', 'message']
    readonly_fields = [
        'id', 'created_at', 'sent_at', 'delivered_at', 'read_at',
        'external_id', 'retry_count'
    ]
    inlines = [NotificationLogInline]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('id', 'user', 'notification_type', 'channel', 'status')
        }),
        ('Contenido', {
            'fields': ('subject', 'message')
        }),
        ('Destinatarios', {
            'fields': ('recipient_email', 'recipient_phone')
        }),
        ('Estado y Timestamps', {
            'fields': ('created_at', 'sent_at', 'delivered_at', 'read_at')
        }),
        ('Metadatos', {
            'fields': ('external_id', 'retry_count', 'max_retries', 'error_message'),
            'classes': ('collapse',)
        }),
        ('Datos Adicionales', {
            'fields': ('extra_data',),
            'classes': ('collapse',)
        })
    )
    
    actions = ['mark_as_sent', 'mark_as_failed', 'retry_failed']
    
    def mark_as_sent(self, request, queryset):
        """Marcar notificaciones como enviadas"""
        count = 0
        for notification in queryset:
            notification.mark_as_sent()
            count += 1
        self.message_user(request, f'{count} notificaciones marcadas como enviadas')
    mark_as_sent.short_description = "Marcar como enviadas"
    
    def mark_as_failed(self, request, queryset):
        """Marcar notificaciones como fallidas"""
        count = 0
        for notification in queryset:
            notification.mark_as_failed("Marcado manualmente como fallido")
            count += 1
        self.message_user(request, f'{count} notificaciones marcadas como fallidas')
    mark_as_failed.short_description = "Marcar como fallidas"
    
    def retry_failed(self, request, queryset):
        """Reintentar notificaciones fallidas"""
        from .tasks import send_notification_task
        
        count = 0
        for notification in queryset.filter(status='failed'):
            if notification.can_retry:
                try:
                    send_notification_task.delay(str(notification.id))
                    count += 1
                except:
                    # Fallback sin Celery
                    from .services import NotificationService
                    service = NotificationService()
                    if service.send_notification(notification):
                        count += 1
        
        self.message_user(request, f'{count} notificaciones reenviadas')
    retry_failed.short_description = "Reintentar notificaciones fallidas"


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'notification_type', 'channel', 'is_active', 'updated_at'
    ]
    list_filter = ['notification_type', 'channel', 'is_active']
    search_fields = ['name', 'template_body']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'notification_type', 'channel', 'is_active')
        }),
        ('Contenido', {
            'fields': ('subject', 'template_body')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ['notification', 'action', 'timestamp']
    list_filter = ['action', 'timestamp']
    search_fields = ['notification__id', 'details']
    readonly_fields = ['notification', 'action', 'details', 'timestamp']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(NotificationQueue)
class NotificationQueueAdmin(admin.ModelAdmin):
    list_display = [
        'notification', 'priority', 'scheduled_at', 'processed', 'processed_at'
    ]
    list_filter = ['priority', 'processed', 'scheduled_at']
    readonly_fields = ['processed_at']
    
    actions = ['process_queue_items', 'reset_processed']
    
    def process_queue_items(self, request, queryset):
        """Procesar elementos de la cola manualmente"""
        from .tasks import send_notification_task
        
        count = 0
        for queue_item in queryset.filter(processed=False):
            try:
                send_notification_task.delay(str(queue_item.notification.id))
                queue_item.processed = True
                queue_item.save()
                count += 1
            except:
                pass
        
        self.message_user(request, f'{count} elementos de cola procesados')
    process_queue_items.short_description = "Procesar elementos seleccionados"
    
    def reset_processed(self, request, queryset):
        """Resetear estado procesado"""
        count = queryset.update(processed=False, processed_at=None)
        self.message_user(request, f'{count} elementos resetados para reprocesar')
    reset_processed.short_description = "Resetear para reprocesar"


# Personalización del admin site
admin.site.site_header = "Galletas Kati - Administración de Notificaciones"
admin.site.site_title = "Notificaciones Admin"
admin.site.index_title = "Panel de Administración de Notificaciones"
