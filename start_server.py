#!/usr/bin/env python
"""
Script para iniciar el servidor con diferentes opciones de protocolo
"""
import os
import sys
import subprocess

def main():
    print("🚀 Iniciador de Galletas Kati")
    print("=" * 40)
    print("1. HTTP estándar (puerto 8000)")
    print("2. HTTP en puerto alternativo (8002)")
    print("3. Forzar HTTP (deshabilitando redirecciones)")
    print("=" * 40)
    
    try:
        choice = input("Selecciona una opción (1-3): ").strip()
        
        if choice == "1":
            print("\n🌐 Iniciando servidor HTTP estándar...")
            subprocess.run([sys.executable, "manage.py", "runserver", "127.0.0.1:8000"])
            
        elif choice == "2":
            print("\n🌐 Iniciando servidor HTTP en puerto alternativo...")
            subprocess.run([sys.executable, "manage.py", "runserver", "127.0.0.1:8002"])
            
        elif choice == "3":
            print("\n🔧 Configurando servidor HTTP forzado...")
            # Temporalmente deshabilitar redirecciones HTTPS
            os.environ['DJANGO_FORCE_HTTP'] = 'True'
            subprocess.run([sys.executable, "manage.py", "runserver", "0.0.0.0:8000"])
            
        else:
            print("❌ Opción no válida")
            
    except KeyboardInterrupt:
        print("\n\n👋 Servidor detenido")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
