#!/usr/bin/env python
"""
Script para verificar que el sistema de notificaciones funciona correctamente
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
    print("✅ Django configurado correctamente")
except Exception as e:
    print(f"❌ Error configurando Django: {e}")
    sys.exit(1)

def test_imports():
    """Probar que todos los módulos se importan correctamente"""
    print("\n🔍 Probando importaciones...")
    
    try:
        from notifications.models import Notification
        print("✅ Modelos importados")
    except Exception as e:
        print(f"❌ Error importando modelos: {e}")
        return False
    
    try:
        from notifications.services import NotificationService
        print("✅ Servicios importados")
    except Exception as e:
        print(f"❌ Error importando servicios: {e}")
        return False
    
    try:
        from notifications.views import NotificationListView
        print("✅ Vistas importadas")
    except Exception as e:
        print(f"❌ Error importando vistas: {e}")
        return False
        
    return True

def test_configuration():
    """Probar configuración del sistema"""
    print("\n🧪 Probando configuración...")
    
    try:
        from notifications.services import NotificationService
        config = NotificationService.test_configuration()
        print("✅ Configuración probada")
        return config
    except Exception as e:
        print(f"❌ Error en configuración: {e}")
        return False

def test_urls():
    """Probar que las URLs funcionan"""
    print("\n🔗 Probando URLs...")
    
    try:
        from django.urls import reverse
        from django.test import Client
        
        # Probar que las URLs se resuelven
        preferences_url = reverse('notifications:preferences')
        list_url = reverse('notifications:list')
        
        print(f"✅ URL preferencias: {preferences_url}")
        print(f"✅ URL lista: {list_url}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en URLs: {e}")
        return False

def main():
    print("=" * 60)
    print("🍪 GALLETAS KATI - TEST DEL SISTEMA DE NOTIFICACIONES")
    print("=" * 60)
    
    # Ejecutar pruebas
    tests = [
        ("Importaciones", test_imports),
        ("Configuración", test_configuration),
        ("URLs", test_urls),
    ]
    
    all_passed = True
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        try:
            result = test_func()
            if not result:
                all_passed = False
        except Exception as e:
            print(f"❌ Error en {test_name}: {e}")
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ¡TODAS LAS PRUEBAS PASARON!")
        print("\n🚀 El servidor debería funcionar correctamente.")
        print("Ejecuta: python manage.py runserver 127.0.0.1:8002")
        print("\n📍 Luego accede a:")
        print("   http://127.0.0.1:8002/notifications/")
    else:
        print("⚠️  ALGUNAS PRUEBAS FALLARON")
        print("Revisa los errores arriba.")
    
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Pruebas canceladas por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nPresiona Enter para continuar...")
