from django.apps import AppConfig


class ManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'management'
    verbose_name = 'Gestión Empresarial'
    
    def ready(self):
        """
        Método llamado cuando la aplicación está lista.
        Aquí se pueden registrar señales, etc.
        """
        pass
    verbose_name = 'Gestión Empresarial'
