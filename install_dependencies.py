#!/usr/bin/env python
"""
Script de instalación de dependencias para Galletas Kati
Instala todas las librerías necesarias para el sistema de notificaciones
"""

import subprocess
import sys
import os

def install_package(package):
    """Instala un paquete usando pip"""
    try:
        print(f"📦 Instalando {package}...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", package
        ], capture_output=True, text=True, check=True)
        print(f"✅ {package} instalado correctamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando {package}: {e}")
        if e.stdout:
            print(f"Stdout: {e.stdout}")
        if e.stderr:
            print(f"Stderr: {e.stderr}")
        return False

def main():
    print("=" * 60)
    print("🍪 GALLETAS KATI - INSTALADOR DE DEPENDENCIAS")
    print("=" * 60)
    print()
    
    # Lista de paquetes a instalar
    packages = [
        "celery==5.3.4",           # Para procesamiento asíncrono
        "redis==5.0.1",            # Para broker de Celery
        "twilio==8.10.3",          # Para SMS y WhatsApp
        "requests==2.31.0",        # Para llamadas HTTP
        "phonenumbers==8.13.25",   # Para validación de números
        "django-phonenumber-field==7.3.0",  # Campo de teléfono para Django
    ]
    
    print("📋 Paquetes a instalar:")
    for package in packages:
        print(f"   • {package}")
    print()
    
    # Actualizar pip primero
    print("🔄 Actualizando pip...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "--upgrade", "pip"
        ], check=True, capture_output=True)
        print("✅ pip actualizado")
    except subprocess.CalledProcessError:
        print("⚠️  No se pudo actualizar pip, continuando...")
    
    print()
    
    # Instalar cada paquete
    success_count = 0
    for package in packages:
        if install_package(package):
            success_count += 1
        print()
    
    print("=" * 60)
    print("📊 RESUMEN DE INSTALACIÓN")
    print("=" * 60)
    print(f"✅ Paquetes instalados correctamente: {success_count}/{len(packages)}")
    
    if success_count == len(packages):
        print("🎉 ¡Todas las dependencias instaladas exitosamente!")
        print()
        print("🚀 Ahora puedes ejecutar:")
        print("   • python manage.py runserver 127.0.0.1:8002")
        print("   • Celery worker: celery -A galletas_kati worker --loglevel=info")
        print("   • Celery beat: celery -A galletas_kati beat --loglevel=info")
    else:
        print("⚠️  Algunas dependencias no se pudieron instalar")
        print("   Revisa los errores arriba y trata de instalar manualmente")
    
    print()
    print("📍 URLs del sistema:")
    print("   🏠 http://127.0.0.1:8002/ (Sitio principal)")
    print("   🔔 http://127.0.0.1:8002/notifications/ (Notificaciones)")
    print("   🔧 http://127.0.0.1:8002/management/ (Admin)")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Instalación cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
    
    input("\nPresiona Enter para continuar...")
