#!/usr/bin/env python
"""Script para iniciar el servidor Django en puerto 8002"""
import os
import sys
import subprocess

def main():
    # Cambiar al directorio del proyecto
    project_dir = r"c:\Users\cuent\Galletas Kati"
    os.chdir(project_dir)
    
    # Configurar Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dulce_bias_project.settings')
    
    print("================================================================")
    print("🍪 GALLETAS KATI - SERVIDOR EN PUERTO 8002")
    print("================================================================")
    print()
    
    try:
        # Verificar configuración
        print("🔧 Verificando configuración...")
        result = subprocess.run([sys.executable, 'manage.py', 'check'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Configuración verificada correctamente")
        else:
            print("⚠️ Advertencias en la configuración:")
            print(result.stdout)
            if result.stderr:
                print(result.stderr)
        
        print()
        print("🚀 Iniciando servidor en puerto 8002...")
        print()
        print("🌐 URLs disponibles:")
        print("   • Sistema principal: http://127.0.0.1:8002/")
        print("   • Panel de notificaciones: http://127.0.0.1:8002/notifications/")
        print("   • Panel administrativo: http://127.0.0.1:8002/admin/")
        print("   • Tienda: http://127.0.0.1:8002/shop/")
        print("   • Soporte: http://127.0.0.1:8002/support/")
        print()
        print("================================================================")
        print("Presiona Ctrl+C para detener el servidor")
        print("================================================================")
        print()
        
        # Iniciar servidor
        subprocess.run([sys.executable, 'manage.py', 'runserver', '0.0.0.0:8002'])
        
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario")
    except Exception as e:
        print(f"❌ Error al iniciar servidor: {e}")
        return False
    
    return True

if __name__ == '__main__':
    main()
