#!/usr/bin/env python3
import os
import subprocess
import sys

def execute_git_commands():
    """Ejecuta comandos git de forma secuencial"""
    
    # Cambiar al directorio del proyecto
    project_path = r"c:\Users\cuent\Galletas Kati"
    os.chdir(project_path)
    
    print(f"🍪 GALLETAS KATI - GIT PUSH")
    print(f"📁 Directorio: {os.getcwd()}")
    print("=" * 50)
    
    # Lista de comandos a ejecutar
    git_commands = [
        {
            'command': ['git', 'status', '--porcelain'],
            'description': '📋 Verificando archivos modificados'
        },
        {
            'command': ['git', 'add', '-A'],
            'description': '📦 Agregando todos los archivos'
        },
        {
            'command': ['git', 'status', '--porcelain'],
            'description': '📊 Verificando archivos en staging'
        },
        {
            'command': ['git', 'commit', '-m', 'feat: Sistema completo - notificaciones, navbar fixes, panel admin integrado'],
            'description': '💾 Creando commit'
        },
        {
            'command': ['git', 'push', 'origin', 'main'],
            'description': '🚀 Subiendo cambios a GitHub'
        }
    ]
    
    for step in git_commands:
        print(f"\n{step['description']}...")
        try:
            result = subprocess.run(
                step['command'], 
                cwd=project_path,
                capture_output=True, 
                text=True, 
                timeout=60,
                shell=False
            )
            
            print(f"Comando: {' '.join(step['command'])}")
            print(f"Código: {result.returncode}")
            
            if result.stdout.strip():
                print(f"Salida:\n{result.stdout}")
            
            if result.stderr.strip():
                print(f"Error/Advertencia:\n{result.stderr}")
                
            if result.returncode != 0 and 'commit' not in step['command'][1]:
                print(f"❌ Error ejecutando: {' '.join(step['command'])}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"❌ Timeout ejecutando: {' '.join(step['command'])}")
            return False
        except Exception as e:
            print(f"❌ Excepción: {e}")
            return False
    
    print("\n" + "=" * 50)
    print("🎉 ¡GIT PUSH COMPLETADO!")
    print("📍 Revisa tu repositorio en:")
    print("   https://github.com/Seba-Truji94/Project2025")
    print("=" * 50)
    
    return True

if __name__ == '__main__':
    try:
        success = execute_git_commands()
        if success:
            print("\n✅ Todos los cambios fueron subidos exitosamente")
        else:
            print("\n❌ Hubo problemas subiendo los cambios")
    except KeyboardInterrupt:
        print("\n🛑 Proceso cancelado por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
    
    input("\nPresiona Enter para continuar...")
