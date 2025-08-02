"""
Signals para logging de eventos de seguridad
"""
import logging
from django.contrib.auth.signals import user_login_failed, user_logged_in, user_logged_out
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from .utils import log_security_event

logger = logging.getLogger('security')


@receiver(user_login_failed)
def log_failed_login(sender, credentials, request, **kwargs):
    """Log intentos de login fallidos"""
    username = credentials.get('username', 'Unknown')
    ip_address = request.META.get('REMOTE_ADDR', 'Unknown')
    
    log_security_event(
        'LOGIN_FAILED',
        None,
        ip_address,
        f"Username attempted: {username}"
    )


@receiver(user_logged_in)
def log_successful_login(sender, request, user, **kwargs):
    """Log logins exitosos"""
    ip_address = request.META.get('REMOTE_ADDR', 'Unknown')
    
    log_security_event(
        'LOGIN_SUCCESS',
        user,
        ip_address,
        "User logged in successfully"
    )


@receiver(user_logged_out)
def log_logout(sender, request, user, **kwargs):
    """Log cuando usuarios salen del sistema"""
    ip_address = request.META.get('REMOTE_ADDR', 'Unknown')
    
    log_security_event(
        'LOGOUT',
        user,
        ip_address,
        "User logged out"
    )


@receiver(post_save, sender=User)
def log_user_changes(sender, instance, created, **kwargs):
    """Log cambios en usuarios"""
    if created:
        log_security_event(
            'USER_CREATED',
            instance,
            'System',
            f"New user created: {instance.username}"
        )
    else:
        log_security_event(
            'USER_MODIFIED',
            instance,
            'System',
            f"User modified: {instance.username}"
        )
