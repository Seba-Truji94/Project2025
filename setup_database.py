#!/usr/bin/env python
"""
Script para crear y aplicar migraciones del sistema de notificaciones
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

from django.core.management import execute_from_command_line

def create_migrations():
    """Crear migraciones para notifications"""
    print("📝 Creando migraciones para notifications...")
    try:
        execute_from_command_line(['manage.py', 'makemigrations', 'notifications', '--verbosity=2'])
        print("✅ Migraciones creadas")
        return True
    except Exception as e:
        print(f"❌ Error creando migraciones: {e}")
        return False

def apply_migrations():
    """Aplicar migraciones"""
    print("🚀 Aplicando migraciones...")
    try:
        execute_from_command_line(['manage.py', 'migrate', '--verbosity=2'])
        print("✅ Migraciones aplicadas")
        return True
    except Exception as e:
        print(f"❌ Error aplicando migraciones: {e}")
        return False

def show_migrations():
    """Mostrar estado de migraciones"""
    print("📋 Estado de migraciones:")
    try:
        execute_from_command_line(['manage.py', 'showmigrations'])
        return True
    except Exception as e:
        print(f"❌ Error mostrando migraciones: {e}")
        return False

def main():
    print("=" * 60)
    print("🍪 GALLETAS KATI - CONFIGURACIÓN DE BASE DE DATOS")
    print("=" * 60)
    
    # Crear migraciones
    if not create_migrations():
        return False
    
    print()
    
    # Aplicar migraciones
    if not apply_migrations():
        return False
    
    print()
    
    # Mostrar estado
    show_migrations()
    
    print("\n" + "=" * 60)
    print("🎉 ¡BASE DE DATOS CONFIGURADA!")
    print("🚀 El sistema de notificaciones ya debería funcionar en:")
    print("   http://127.0.0.1:8002/notifications/")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n❌ Hubo errores en la configuración")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n❌ Proceso cancelado por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    input("\nPresiona Enter para continuar...")
