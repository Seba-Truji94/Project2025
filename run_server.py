#!/usr/bin/env python
"""
Script para iniciar el servidor Django
Ejecuta este archivo para iniciar el servidor web
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dulce_bias_project.settings')
    
    print("🚀 INICIANDO SERVIDOR DJANGO")
    print("=" * 50)
    print("📍 URL: http://127.0.0.1:8002/")
    print("🔧 Panel de Administración: http://127.0.0.1:8002/management/")
    print("📊 Alertas de Stock: http://127.0.0.1:8002/management/stock/alertas/")
    print("📋 Reporte de Stock: http://127.0.0.1:8002/management/stock/reporte/")
    print("=" * 50)
    print("💡 Para detener el servidor: Ctrl+C")
    print("=" * 50)
    
    try:
        execute_from_command_line(['manage.py', 'runserver', '127.0.0.1:8002'])
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario")
    except Exception as e:
        print(f"❌ Error al iniciar servidor: {e}")
