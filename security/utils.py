"""
Utilidades de seguridad
"""
import logging
import hashlib
import secrets
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.core.cache import cache
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.conf import settings

logger = logging.getLogger('security')


def generate_secure_token(length=32):
    """Generar token seguro"""
    return secrets.token_urlsafe(length)


def hash_sensitive_data(data):
    """Hash para datos sensibles"""
    return hashlib.sha256(data.encode()).hexdigest()


def log_security_event(event_type, user, ip_address, details=None):
    """Logging centralizado de eventos de seguridad"""
    logger.warning(
        f'SECURITY EVENT: {event_type} | '
        f'User: {user.username if user else "Anonymous"} | '
        f'IP: {ip_address} | '
        f'Details: {details or "N/A"} | '
        f'Time: {datetime.now()}'
    )


def check_password_strength(password):
    """Verificar fortaleza de contraseña"""
    score = 0
    feedback = []
    
    if len(password) >= 12:
        score += 1
    else:
        feedback.append("Usa al menos 12 caracteres")
    
    if any(c.islower() for c in password):
        score += 1
    else:
        feedback.append("Incluye letras minúsculas")
    
    if any(c.isupper() for c in password):
        score += 1
    else:
        feedback.append("Incluye letras mayúsculas")
    
    if any(c.isdigit() for c in password):
        score += 1
    else:
        feedback.append("Incluye números")
    
    if any(c in '!@#$%^&*(),.?":{}|<>' for c in password):
        score += 1
    else:
        feedback.append("Incluye caracteres especiales")
    
    strength_levels = {
        0: "Muy débil",
        1: "Débil", 
        2: "Moderada",
        3: "Buena",
        4: "Fuerte",
        5: "Muy fuerte"
    }
    
    return {
        'score': score,
        'strength': strength_levels[score],
        'feedback': feedback
    }


def axes_lockout_response(request, credentials, *args, **kwargs):
    """Respuesta personalizada para bloqueos de Axes"""
    context = {
        'title': 'Cuenta Bloqueada',
        'message': 'Su cuenta ha sido bloqueada temporalmente debido a múltiples intentos de inicio de sesión fallidos.',
        'contact_support': True
    }
    
    # Log del bloqueo
    log_security_event(
        'ACCOUNT_LOCKOUT',
        None,
        request.META.get('REMOTE_ADDR'),
        f"Credentials attempted: {credentials.get('username', 'Unknown')}"
    )
    
    return HttpResponse(
        render_to_string('security/lockout.html', context, request),
        status=403
    )


def validate_file_upload(uploaded_file):
    """Validar archivos subidos"""
    # Verificar extensión
    allowed_extensions = getattr(settings, 'ALLOWED_IMAGE_EXTENSIONS', []) + \
                        getattr(settings, 'ALLOWED_DOCUMENT_EXTENSIONS', [])
    
    file_extension = uploaded_file.name.lower().split('.')[-1]
    if f'.{file_extension}' not in allowed_extensions:
        raise ValueError(f"Tipo de archivo no permitido: .{file_extension}")
    
    # Verificar tamaño
    max_size = getattr(settings, 'MAX_UPLOAD_SIZE', 5242880)  # 5MB default
    if uploaded_file.size > max_size:
        raise ValueError(f"Archivo muy grande. Máximo: {max_size/1024/1024:.1f}MB")
    
    return True


def sanitize_input(input_data):
    """Sanitizar entrada de usuario"""
    if isinstance(input_data, str):
        # Remover caracteres peligrosos
        dangerous_chars = ['<', '>', '"', "'", '&', 'javascript:', 'eval(', 'expression(']
        for char in dangerous_chars:
            input_data = input_data.replace(char, '')
    
    return input_data


def check_suspicious_activity(user, ip_address):
    """Detectar actividad sospechosa"""
    cache_key = f'user_activity:{user.id}:{ip_address}'
    activity_count = cache.get(cache_key, 0)
    
    # Si hay más de 50 acciones en 5 minutos, es sospechoso
    if activity_count > 50:
        log_security_event(
            'SUSPICIOUS_ACTIVITY',
            user,
            ip_address,
            f"High activity count: {activity_count}"
        )
        return True
    
    cache.set(cache_key, activity_count + 1, 300)  # 5 minutos
    return False


class SecurityAudit:
    """Clase para auditorías de seguridad"""
    
    @staticmethod
    def check_weak_passwords():
        """Verificar usuarios con contraseñas débiles"""
        weak_users = []
        for user in User.objects.filter(is_active=True):
            # Verificar si la contraseña parece débil (esto es una aproximación)
            if user.check_password('password') or \
               user.check_password('123456') or \
               user.check_password(user.username):
                weak_users.append(user)
        
        return weak_users
    
    @staticmethod
    def check_inactive_superusers():
        """Verificar superusuarios inactivos"""
        cutoff_date = datetime.now() - timedelta(days=90)
        return User.objects.filter(
            is_superuser=True,
            last_login__lt=cutoff_date
        )
    
    @staticmethod
    def check_duplicate_emails():
        """Verificar emails duplicados"""
        from django.db.models import Count
        return User.objects.values('email').annotate(
            count=Count('email')
        ).filter(count__gt=1, email__isnull=False).exclude(email='')
    
    @staticmethod
    def generate_security_report():
        """Generar reporte de seguridad completo"""
        return {
            'weak_passwords': SecurityAudit.check_weak_passwords(),
            'inactive_superusers': SecurityAudit.check_inactive_superusers(),
            'duplicate_emails': SecurityAudit.check_duplicate_emails(),
            'timestamp': datetime.now()
        }
