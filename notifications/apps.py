from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notifications'
    verbose_name = 'Sistema de Notificaciones'

    def ready(self):
        try:
            # Importar signals solo si es posible
            import notifications.signals
        except ImportError as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"No se pudieron cargar los signals de notificaciones: {e}")
            logger.warning("Para funcionalidad completa, instala: pip install twilio celery redis")
