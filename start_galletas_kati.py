#!/usr/bin/env python
"""
Script de inicio rápido para Galletas Kati
Ejecuta el servidor Django y muestra información importante
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def main():
    # Cambiar al directorio del proyecto
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    print("=" * 60)
    print("🍪 GALLETAS KATI - SERVIDOR DE DESARROLLO")
    print("=" * 60)
    print()
    print("📍 URLs Principales:")
    print("   🏠 Sitio Principal: http://127.0.0.1:8002/")
    print("   🔧 Panel Admin: http://127.0.0.1:8002/management/")
    print("   📊 Stock y Alertas: http://127.0.0.1:8002/management/stock/alertas/")
    print("   📋 Reportes: http://127.0.0.1:8002/management/stock/reporte/")
    print("   🔔 Notificaciones: http://127.0.0.1:8002/notifications/")
    print("   🎧 Soporte: http://127.0.0.1:8002/support/")
    print()
    print("🆕 Sistema de Notificaciones Implementado:")
    print("   ✅ Email, SMS y WhatsApp")
    print("   ✅ Notificaciones asíncronas")
    print("   ✅ Preferencias de usuario")
    print("   ✅ Panel de administración")
    print()
    print("=" * 60)
    print("💡 Para detener el servidor: Ctrl+C")
    print("=" * 60)
    print()
    
    # Verificar si manage.py existe
    if not os.path.exists('manage.py'):
        print("❌ Error: manage.py no encontrado")
        print("   Asegúrate de estar en el directorio correcto")
        return False
    
    try:
        # Ejecutar el servidor
        print("🚀 Iniciando servidor Django...")
        print()
        
        # Abrir el navegador después de un delay
        def open_browser():
            time.sleep(3)
            webbrowser.open('http://127.0.0.1:8002/')
        
        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.start()
        
        # Ejecutar el servidor
        subprocess.run([
            sys.executable, 'manage.py', 'runserver', '127.0.0.1:8002'
        ], check=True)
        
    except KeyboardInterrupt:
        print("\n")
        print("=" * 60)
        print("🛑 Servidor detenido por el usuario")
        print("=" * 60)
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al ejecutar el servidor: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

if __name__ == "__main__":
    success = main()
    input("\nPresiona Enter para continuar...")
    sys.exit(0 if success else 1)
