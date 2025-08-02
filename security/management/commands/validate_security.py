"""
Comando de gestión para validar la configuración de seguridad
"""
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.test import RequestFactory
from django.http import HttpResponse
import logging

class Command(BaseCommand):
    help = 'Valida la configuración de seguridad del proyecto'

    def add_arguments(self, parser):
        parser.add_argument(
            '--check-csp',
            action='store_true',
            help='Verifica la configuración de Content Security Policy',
        )
        parser.add_argument(
            '--check-external',
            action='store_true',
            help='Verifica la conectividad con recursos externos',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Mostrar información detallada',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== Validación de Seguridad ===\n'))
        
        # Verificar configuración básica
        self.check_basic_security()
        
        # Verificar CSP si se solicita
        if options['check_csp']:
            self.check_csp_configuration()
        
        # Verificar recursos externos si se solicita
        if options['check_external']:
            self.check_external_resources()
        
        self.stdout.write(self.style.SUCCESS('\n=== Validación Completada ==='))

    def check_basic_security(self):
        """Verificar configuración básica de seguridad"""
        self.stdout.write(self.style.HTTP_INFO('Verificando configuración básica...'))
        
        # Verificar DEBUG
        if settings.DEBUG:
            self.stdout.write(self.style.WARNING('⚠️  DEBUG está habilitado'))
        else:
            self.stdout.write(self.style.SUCCESS('✅ DEBUG está deshabilitado'))
        
        # Verificar SECRET_KEY
        if hasattr(settings, 'SECRET_KEY') and len(settings.SECRET_KEY) > 20:
            self.stdout.write(self.style.SUCCESS('✅ SECRET_KEY configurada'))
        else:
            self.stdout.write(self.style.ERROR('❌ SECRET_KEY débil o no configurada'))
        
        # Verificar ALLOWED_HOSTS
        if settings.ALLOWED_HOSTS and settings.ALLOWED_HOSTS != ['*']:
            self.stdout.write(self.style.SUCCESS('✅ ALLOWED_HOSTS configurado'))
        else:
            self.stdout.write(self.style.WARNING('⚠️  ALLOWED_HOSTS permisivo'))
        
        # Verificar Django Axes
        if 'axes' in settings.INSTALLED_APPS:
            self.stdout.write(self.style.SUCCESS('✅ Django Axes instalado'))
        else:
            self.stdout.write(self.style.WARNING('⚠️  Django Axes no encontrado'))
        
        # Verificar django-csp
        if 'csp' in settings.INSTALLED_APPS:
            self.stdout.write(self.style.SUCCESS('✅ django-csp instalado'))
        else:
            self.stdout.write(self.style.WARNING('⚠️  django-csp no encontrado'))

    def check_csp_configuration(self):
        """Verificar configuración de Content Security Policy"""
        self.stdout.write(self.style.HTTP_INFO('\nVerificando CSP...'))
        
        # Verificar formato nuevo de django-csp 4.0+
        if hasattr(settings, 'CONTENT_SECURITY_POLICY'):
            csp_config = getattr(settings, 'CONTENT_SECURITY_POLICY')
            self.stdout.write(self.style.SUCCESS('✅ CONTENT_SECURITY_POLICY configurado (formato 4.0+)'))
            
            if 'DIRECTIVES' in csp_config:
                directives = csp_config['DIRECTIVES']
                self.stdout.write(f'📋 Directivas configuradas: {list(directives.keys())}')
                
                # Verificar directivas importantes
                important_directives = ['default-src', 'script-src', 'style-src', 'font-src']
                for directive in important_directives:
                    if directive in directives:
                        sources = directives[directive]
                        self.stdout.write(f'  ✅ {directive}: {sources}')
                    else:
                        self.stdout.write(self.style.WARNING(f'  ⚠️  {directive} no configurado'))
                
                # Verificar si cdnjs.cloudflare.com está permitido
                style_src = directives.get('style-src', ())
                font_src = directives.get('font-src', ())
                
                if 'https://cdnjs.cloudflare.com' in style_src:
                    self.stdout.write(self.style.SUCCESS('✅ cdnjs.cloudflare.com permitido en style-src'))
                else:
                    self.stdout.write(self.style.WARNING('⚠️  cdnjs.cloudflare.com NO encontrado en style-src'))
                
                if 'https://cdnjs.cloudflare.com' in font_src:
                    self.stdout.write(self.style.SUCCESS('✅ cdnjs.cloudflare.com permitido en font-src'))
                else:
                    self.stdout.write(self.style.WARNING('⚠️  cdnjs.cloudflare.com NO encontrado en font-src'))
            
        else:
            # Verificar configuraciones CSP legadas
            legacy_settings = [
                'CSP_DEFAULT_SRC',
                'CSP_SCRIPT_SRC',
                'CSP_STYLE_SRC',
                'CSP_FONT_SRC',
                'CSP_IMG_SRC',
            ]
            
            legacy_found = False
            for setting_name in legacy_settings:
                if hasattr(settings, setting_name):
                    legacy_found = True
                    setting_value = getattr(settings, setting_name)
                    self.stdout.write(f'⚠️  {setting_name} (legacy): {setting_value}')
            
            if legacy_found:
                self.stdout.write(self.style.WARNING('⚠️  Usando configuración CSP legacy. Considerar migrar a CONTENT_SECURITY_POLICY'))
            else:
                self.stdout.write(self.style.ERROR('❌ No se encontró configuración CSP'))

    def check_external_resources(self):
        """Verificar recursos externos configurados"""
        self.stdout.write(self.style.HTTP_INFO('\nVerificando configuración de recursos externos...'))
        
        external_resources = [
            'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css',
            'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
            'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap',
        ]
        
        self.stdout.write('Recursos externos configurados:')
        for resource in external_resources:
            self.stdout.write(f'  📄 {resource}')
        
        # Verificar que estos dominios estén en CSP
        if hasattr(settings, 'CSP_STYLE_SRC'):
            style_src = getattr(settings, 'CSP_STYLE_SRC')
            self.stdout.write(f'\nDominios permitidos en CSP_STYLE_SRC: {style_src}')
        
        self.stdout.write('\n💡 Para verificar conectividad, usar herramientas del navegador o curl.')

    def check_middleware_order(self):
        """Verificar orden de middleware"""
        self.stdout.write(self.style.HTTP_INFO('\nVerificando orden de middleware...'))
        
        required_middleware = [
            'django.middleware.security.SecurityMiddleware',
            'axes.middleware.AxesMiddleware',
            'csp.middleware.CSPMiddleware',
        ]
        
        middleware_list = settings.MIDDLEWARE
        for mw in required_middleware:
            if mw in middleware_list:
                position = middleware_list.index(mw)
                self.stdout.write(f'✅ {mw} - Posición: {position}')
            else:
                self.stdout.write(self.style.WARNING(f'⚠️  {mw} no encontrado'))
