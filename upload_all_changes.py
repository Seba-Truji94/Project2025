#!/usr/bin/env python3
"""
Script para subir todos los cambios al repositorio git
"""

import os
import subprocess
import sys
from pathlib import Path

def run_git_command(command, description):
    """Ejecuta un comando git y maneja errores"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=r"c:\Users\cuent\Galletas Kati",
            capture_output=True, 
            text=True,
            timeout=30
        )
        
        if result.stdout:
            print(f"✅ {result.stdout}")
        if result.stderr and result.returncode != 0:
            print(f"⚠️  {result.stderr}")
            
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("❌ Timeout - comando tardó demasiado")
        return False
    except Exception as e:
        print(f"❌ Error ejecutando comando: {e}")
        return False

def main():
    print("=" * 60)
    print("🍪 GALLETAS KATI - SUBIENDO TODOS LOS CAMBIOS")
    print("=" * 60)
    
    # Cambiar al directorio del proyecto
    project_dir = Path(r"c:\Users\cuent\Galletas Kati")
    if not project_dir.exists():
        print("❌ Directorio del proyecto no encontrado")
        return False
    
    os.chdir(project_dir)
    print(f"📁 Directorio actual: {os.getcwd()}")
    
    # Verificar que sea un repositorio git
    if not (project_dir / ".git").exists():
        print("❌ No es un repositorio git")
        return False
    
    # Ejecutar comandos git
    commands = [
        ("git status", "📋 Verificando estado actual"),
        ("git add -A", "📦 Agregando todos los archivos"),
        ("git status --porcelain", "📊 Verificando archivos en staging"),
    ]
    
    for command, description in commands:
        if not run_git_command(command, description):
            print(f"❌ Error en: {command}")
            return False
    
    # Crear commit
    commit_message = """feat: Actualizacion completa del sistema

- Sistema de notificaciones completamente implementado
- Panel administrativo con dropdown menu integrado  
- Navbar corregido en todas las vistas del sistema
- Templates profesionales y responsivos
- CSS global para evitar superposicion de contenido
- Scripts de verificacion y mantenimiento
- Documentacion actualizada

Caracteristicas:
- Notificaciones Email/SMS/WhatsApp
- Dashboard administrativo completo
- Gestion de plantillas y usuarios
- Accesos directos en menu dropdown
- Navbar dinamico sin superposicion
- Sistema completamente funcional

URLs disponibles:
- /notifications/ - Panel principal
- /notifications/admin/ - Administracion
- /notifications/admin/templates/ - Plantillas
- /notifications/preferences/ - Preferencias"""
    
    commit_command = f'git commit -m "{commit_message}"'
    if not run_git_command(commit_command, "💾 Creando commit"):
        print("ℹ️  Es posible que no haya cambios para commitear")
    
    # Subir cambios
    if not run_git_command("git push origin main", "🚀 Subiendo cambios al repositorio"):
        print("❌ Error subiendo cambios")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 ¡CAMBIOS SUBIDOS EXITOSAMENTE!")
    print("=" * 60)
    print("\n📍 El repositorio está actualizado con:")
    print("   ✅ Sistema de notificaciones completo")
    print("   ✅ Panel administrativo integrado")
    print("   ✅ Navbar corregido globalmente")
    print("   ✅ Templates y CSS optimizados")
    print("   ✅ Scripts de mantenimiento")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n❌ Algunos comandos fallaron")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n❌ Proceso cancelado por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    input("\n✅ Presiona Enter para continuar...")
