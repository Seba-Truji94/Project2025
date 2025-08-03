"""
Middleware de seguridad personalizado para Galletas Kati
"""
import logging
import time
from datetime import datetime, timedelta
from django.http import HttpResponseForbidden, HttpResponse
from django.core.cache import cache
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import render
from django.contrib.auth.signals import user_login_failed
from django.dispatch import receiver
import json

logger = logging.getLogger('security')


class SecurityLogMiddleware(MiddlewareMixin):
    """Middleware para logging de actividades de seguridad"""
    
    def process_request(self, request):
        # Log de requests sospechosos
        suspicious_patterns = [
            '/admin/login',
            '/.env',
            '/wp-admin',
            '/phpmyadmin',
            '/config',
            '/../',
            '/etc/passwd',
            'eval(',
            '<script',
            'javascript:',
            'onload=',
            'onerror=',
        ]
        
        path = request.get_full_path().lower()
        for pattern in suspicious_patterns:
            if pattern in path:
                logger.warning(
                    f'Suspicious request detected: {request.method} {path} '
                    f'from IP: {self.get_client_ip(request)} '
                    f'User-Agent: {request.META.get("HTTP_USER_AGENT", "Unknown")}'
                )
                break
        
        # Log intentos de acceso a admin (después de autenticación)
        if '/admin/' in request.path and request.method == 'POST':
            user = getattr(request, 'user', None)
            username = getattr(user, 'username', 'Anonymous') if user else 'Anonymous'
            logger.info(
                f'Admin access attempt: {request.path} '
                f'from IP: {self.get_client_ip(request)} '
                f'User: {username}'
            )
        
        return None
    
    def get_client_ip(self, request):
        """Obtener IP real del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RateLimitMiddleware(MiddlewareMixin):
    """Middleware para rate limiting"""
    
    def process_request(self, request):
        if not getattr(settings, 'RATELIMIT_ENABLE', True):
            return None
        
        ip = self.get_client_ip(request)
        
        # Rate limiting para diferentes endpoints
        limits = {
            '/accounts/login/': getattr(settings, 'RATE_LIMIT_LOGIN', '5/m'),
            '/accounts/password-reset/': getattr(settings, 'RATE_LIMIT_PASSWORD_RESET', '3/h'),
            '/support/contact/': getattr(settings, 'RATE_LIMIT_CONTACT_FORM', '10/h'),
            '/admin/shop/taxconfiguration/': getattr(settings, 'RATE_LIMIT_ADMIN_TAX', '10/m'),
            '/admin/shop/discountcoupon/': getattr(settings, 'RATE_LIMIT_ADMIN_COUPONS', '15/m'),
            '/admin/shop/supplier/': getattr(settings, 'RATE_LIMIT_ADMIN_SUPPLIERS', '10/m'),
            '/admin/shop/productstock/': getattr(settings, 'RATE_LIMIT_ADMIN_STOCK', '20/m'),
            '/admin/shop/productsupplier/': getattr(settings, 'RATE_LIMIT_ADMIN_RELATIONS', '15/m'),
            '/management/': getattr(settings, 'RATE_LIMIT_MANAGEMENT', '30/m'),
            '/management/tax/': getattr(settings, 'RATE_LIMIT_MANAGEMENT_TAX', '15/m'),
            '/management/coupon/': getattr(settings, 'RATE_LIMIT_MANAGEMENT_COUPONS', '15/m'),
            '/management/supplier/': getattr(settings, 'RATE_LIMIT_MANAGEMENT_SUPPLIERS', '15/m'),
            '/management/stock/': getattr(settings, 'RATE_LIMIT_MANAGEMENT_STOCK', '20/m'),
            '/management/relations/': getattr(settings, 'RATE_LIMIT_MANAGEMENT_RELATIONS', '15/m'),
        }
        
        for path, limit in limits.items():
            if request.path.startswith(path):
                if self.is_rate_limited(ip, path, limit):
                    logger.warning(f'Rate limit exceeded for IP {ip} on {path}')
                    return HttpResponseForbidden(
                        '<h1>Too Many Requests</h1><p>Please try again later.</p>',
                        content_type='text/html'
                    )
        
        return None
    
    def get_client_ip(self, request):
        """Obtener IP real del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def is_rate_limited(self, ip, path, limit):
        """Verificar si la IP excede el rate limit"""
        try:
            requests, period = limit.split('/')
            requests = int(requests)
            
            # Convertir período a segundos
            if period.endswith('s'):
                seconds = int(period[:-1])
            elif period.endswith('m'):
                seconds = int(period[:-1]) * 60
            elif period.endswith('h'):
                seconds = int(period[:-1]) * 3600
            else:
                seconds = 60  # Default 1 minuto
            
            cache_key = f'rate_limit:{ip}:{path}'
            current_requests = cache.get(cache_key, 0)
            
            if current_requests >= requests:
                return True
            
            cache.set(cache_key, current_requests + 1, seconds)
            return False
            
        except (ValueError, AttributeError):
            return False


class SecurityHeadersMiddleware(MiddlewareMixin):
    """Middleware para headers de seguridad adicionales"""
    
    def process_response(self, request, response):
        # Headers de seguridad adicionales
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        # HSTS (HTTP Strict Transport Security)
        if request.is_secure():
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        
        # Nota: CSP ahora es manejado por django-csp middleware
        # El CSP personalizado ha sido removido en favor de django-csp
        
        return response


class IPWhitelistMiddleware(MiddlewareMixin):
    """Middleware para whitelist de IPs en admin (solo producción)"""
    
    def process_request(self, request):
        # Solo aplicar en producción y para rutas de admin
        if settings.DEBUG or not request.path.startswith('/admin/'):
            return None
        
        ip = self.get_client_ip(request)
        whitelist = getattr(settings, 'ADMIN_IP_WHITELIST', [])
        
        if whitelist and ip not in whitelist:
            logger.warning(f'Admin access denied for IP {ip} - not in whitelist')
            return HttpResponseForbidden(
                '<h1>Access Denied</h1><p>Your IP is not authorized to access this area.</p>',
                content_type='text/html'
            )
        
        return None
    
    def get_client_ip(self, request):
        """Obtener IP real del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class AdminModulesAccessMiddleware(MiddlewareMixin):
    """Middleware para controlar acceso a módulos de administración avanzados"""
    
    def process_request(self, request):
        # Rutas que requieren permisos especiales de superusuario
        restricted_admin_paths = [
            '/admin/shop/taxconfiguration/',
            '/admin/shop/discountcoupon/',
            '/admin/shop/couponusage/',
            '/admin/shop/supplier/',
            '/admin/shop/productstock/',
            '/admin/shop/productsupplier/',
            '/management/',  # Nuevo módulo de gestión empresarial
        ]
        
        # Verificar si la ruta actual necesita permisos especiales
        is_restricted_path = any(
            request.path.startswith(path) for path in restricted_admin_paths
        )
        
        if not is_restricted_path:
            return None
        
        # Solo verificar si el usuario está autenticado
        user = getattr(request, 'user', None)
        if not user or not hasattr(user, 'is_authenticated'):
            # El usuario aún no está autenticado, dejar que Django maneje la autenticación
            return None
        
        if not user.is_authenticated:
            logger.warning(
                f'Unauthorized access attempt to {request.path} '
                f'from IP: {self.get_client_ip(request)}'
            )
            return None  # Django manejará la redirección al login
        
        # Verificar si es superusuario para módulos críticos
        critical_paths = [
            '/admin/shop/taxconfiguration/',
            '/admin/shop/discountcoupon/',
            '/admin/shop/supplier/',
            '/management/',  # Todo el módulo de gestión requiere superusuario
        ]
        
        is_critical_path = any(
            request.path.startswith(path) for path in critical_paths
        )
        
        if is_critical_path and not user.is_superuser:
            logger.warning(
                f'Non-superuser access denied to {request.path} '
                f'for user: {user.username} '
                f'from IP: {self.get_client_ip(request)}'
            )
            return HttpResponseForbidden(
                '''
                <h1>🔒 Acceso Restringido</h1>
                <p><strong>Solo los superusuarios pueden acceder a esta sección.</strong></p>
                <p>Este módulo contiene funcionalidades críticas del negocio:</p>
                <ul>
                    <li>🏷️ Configuración de impuestos</li>
                    <li>🎫 Gestión de cupones de descuento</li>
                    <li>🏭 Administración de proveedores</li>
                    <li>⚙️ Panel de gestión empresarial</li>
                    <li>📊 Reportes financieros avanzados</li>
                </ul>
                <p>Contacta al administrador del sistema si necesitas acceso.</p>
                <br>
                <a href="/admin/" style="background: #007cba; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px;">
                    ← Volver al Panel Principal
                </a>
                <a href="/" style="background: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; margin-left: 10px;">
                    🏠 Ir al Inicio
                </a>
                ''',
                content_type='text/html'
            )
        
        # Para otras rutas administrativas, verificar que sea staff
        if not user.is_staff:
            logger.warning(
                f'Non-staff access denied to {request.path} '
                f'for user: {user.username} '
                f'from IP: {self.get_client_ip(request)}'
            )
            return HttpResponseForbidden(
                '''
                <h1>🚫 Acceso Denegado</h1>
                <p><strong>No tienes permisos para acceder a esta sección administrativa.</strong></p>
                <p>Necesitas permisos de personal (staff) para acceder a:</p>
                <ul>
                    <li>📦 Gestión de stock</li>
                    <li>🔗 Relaciones producto-proveedor</li>
                    <li>👥 Seguimiento de uso de cupones</li>
                </ul>
                <br>
                <a href="/" style="background: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px;">
                    ← Volver al Inicio
                </a>
                ''',
                content_type='text/html'
            )
        
        # Log de acceso exitoso a módulos administrativos
        logger.info(
            f'Admin module access granted: {request.path} '
            f'for user: {user.username} (superuser: {user.is_superuser}) '
            f'from IP: {self.get_client_ip(request)}'
        )
        
        return None
    
    def get_client_ip(self, request):
        """Obtener IP real del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
