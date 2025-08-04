#!/usr/bin/env python
"""Script para probar el servidor Django"""
import os
import sys

def main():
    # Cambiar al directorio del proyecto
    project_dir = r"c:\Users\cuent\Galletas Kati"
    os.chdir(project_dir)
    
    # Configurar Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dulce_bias_project.settings')
    
    try:
        from django.core.management import execute_from_command_line
        print("✓ Django importado correctamente")
        
        # Verificar configuración
        from django.conf import settings
        print(f"✓ Configuración cargada: {settings.SECRET_KEY[:10]}...")
        
        # Verificar URLs
        from django.urls import reverse
        try:
            url = reverse('notifications_admin:dashboard')
            print(f"✓ URL de notificaciones: {url}")
        except Exception as e:
            print(f"✗ Error con URLs: {e}")
        
        # Intentar iniciar servidor en modo check
        print("\n=== Verificando configuración del servidor ===")
        execute_from_command_line(['manage.py', 'check'])
        
        print("\n=== ¡Todo listo! El servidor debería funcionar correctamente ===")
        print("Ejecuta: python manage.py runserver")
        
    except ImportError as exc:
        print(f"✗ Error importando Django: {exc}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == '__main__':
    main()
