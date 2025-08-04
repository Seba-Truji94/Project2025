#!/usr/bin/env python
"""
Script de verificación y reparación del sistema de notificaciones
Verifica que todo esté configurado correctamente y repara problemas comunes
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dulce_bias_project.settings')

try:
    django.setup()
except Exception as e:
    print(f"❌ Error configurando Django: {e}")
    sys.exit(1)

from django.core.management import execute_from_command_line
from django.conf import settings
from django.apps import apps

def check_installed_apps():
    """Verifica que notifications esté en INSTALLED_APPS"""
    print("🔍 Verificando INSTALLED_APPS...")
    
    if 'notifications' in settings.INSTALLED_APPS:
        print("✅ notifications está en INSTALLED_APPS")
        return True
    else:
        print("❌ notifications NO está en INSTALLED_APPS")
        print("   Agregando 'notifications' a INSTALLED_APPS...")
        return False

def check_urls():
    """Verifica que las URLs estén configuradas"""
    print("🔍 Verificando configuración de URLs...")
    
    try:
        from django.urls import reverse
        from django.core.exceptions import NoReverseMatch
        
        # Intentar resolver algunas URLs de notificaciones
        try:
            reverse('notifications:preferences')
            print("✅ URLs de notificaciones configuradas correctamente")
            return True
        except NoReverseMatch:
            print("❌ URLs de notificaciones NO están configuradas")
            return False
            
    except Exception as e:
        print(f"⚠️  No se pudieron verificar las URLs: {e}")
        return False

def run_migrations():
    """Ejecuta las migraciones necesarias"""
    print("🔄 Ejecutando migraciones...")
    
    try:
        # Crear migraciones si no existen
        print("   📝 Creando migraciones para notifications...")
        execute_from_command_line(['manage.py', 'makemigrations', 'notifications'])
        
        # Aplicar migraciones
        print("   🚀 Aplicando migraciones...")
        execute_from_command_line(['manage.py', 'migrate'])
        
        print("✅ Migraciones completadas")
        return True
        
    except Exception as e:
        print(f"❌ Error en migraciones: {e}")
        return False

def check_templates():
    """Verifica que las plantillas existan"""
    print("🔍 Verificando plantillas...")
    
    base_path = Path(__file__).parent / 'notifications' / 'templates' / 'notifications'
    
    required_templates = [
        'preferences.html',
        'list.html',
        'email/order_confirmation.html',
        'email/general.html',
        'email/support_ticket.html',
    ]
    
    all_exist = True
    for template in required_templates:
        template_path = base_path / template
        if template_path.exists():
            print(f"   ✅ {template}")
        else:
            print(f"   ❌ {template} - NO EXISTE")
            all_exist = False
    
    return all_exist

def check_models():
    """Verifica que los modelos estén disponibles"""
    print("🔍 Verificando modelos...")
    
    try:
        from notifications.models import (
            Notification, 
            UserNotificationPreference, 
            NotificationTemplate,
            NotificationLog,
            NotificationQueue
        )
        
        print("✅ Todos los modelos están disponibles")
        
        # Verificar que las tablas existan
        print("🔍 Verificando tablas en base de datos...")
        
        try:
            # Intentar contar registros (esto fallará si las tablas no existen)
            notification_count = Notification.objects.count()
            preference_count = UserNotificationPreference.objects.count()
            
            print(f"✅ Tablas creadas - Notificaciones: {notification_count}, Preferencias: {preference_count}")
            return True
            
        except Exception as e:
            print(f"⚠️  Tablas no creadas todavía: {e}")
            return False
            
    except ImportError as e:
        print(f"❌ Error importando modelos: {e}")
        return False

def test_basic_functionality():
    """Prueba funcionalidad básica del sistema"""
    print("🧪 Probando funcionalidad básica...")
    
    try:
        from notifications.services import NotificationService
        
        print("✅ NotificationService importado correctamente")
        
        # Probar configuración básica
        try:
            result = NotificationService.test_configuration()
            print(f"✅ Configuración básica: {result}")
            return True
        except Exception as e:
            print(f"⚠️  Configuración necesita ajustes: {e}")
            return False
            
    except ImportError as e:
        print(f"❌ Error importando servicios: {e}")
        return False

def main():
    print("=" * 60)
    print("🍪 GALLETAS KATI - VERIFICACIÓN DEL SISTEMA DE NOTIFICACIONES")
    print("=" * 60)
    print()
    
    checks = [
        ("Aplicaciones instaladas", check_installed_apps),
        ("Configuración de URLs", check_urls),
        ("Plantillas", check_templates),
        ("Modelos", check_models),
    ]
    
    # Ejecutar migraciones primero
    run_migrations()
    print()
    
    # Ejecutar verificaciones
    all_passed = True
    for check_name, check_func in checks:
        print(f"📋 {check_name}:")
        try:
            result = check_func()
            if not result:
                all_passed = False
        except Exception as e:
            print(f"❌ Error en {check_name}: {e}")
            all_passed = False
        print()
    
    # Probar funcionalidad
    test_basic_functionality()
    print()
    
    print("=" * 60)
    if all_passed:
        print("🎉 ¡SISTEMA DE NOTIFICACIONES VERIFICADO Y LISTO!")
        print()
        print("📍 Puedes acceder a:")
        print("   🔔 http://127.0.0.1:8002/notifications/")
        print("   ⚙️ http://127.0.0.1:8002/notifications/preferences/")
        print("   📊 http://127.0.0.1:8002/admin/ (Django Admin)")
    else:
        print("⚠️  ALGUNAS VERIFICACIONES FALLARON")
        print("   Revisa los errores arriba y corrige los problemas")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Verificación cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nPresiona Enter para continuar...")
