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
        
        # Log intentos de acceso a admin
        if '/admin/' in request.path and request.method == 'POST':
            logger.info(
                f'Admin access attempt: {request.path} '
                f'from IP: {self.get_client_ip(request)} '
                f'User: {getattr(request.user, "username", "Anonymous")}'
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
