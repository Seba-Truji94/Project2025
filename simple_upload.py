import os
import sys

print("🍪 GALLETAS KATI - ESTADO DEL REPOSITORIO")
print("=" * 50)

# Cambiar al directorio
os.chdir(r"c:\Users\cuent\Galletas Kati")
print(f"📁 Directorio: {os.getcwd()}")

# Verificar git
if os.path.exists('.git'):
    print("✅ Repositorio git detectado")
else:
    print("❌ No es un repositorio git")
    sys.exit(1)

# Ejecutar comandos git
commands = [
    "git status --porcelain",
    "git add -A", 
    "git status --porcelain",
    'git commit -m "feat: Sistema completo actualizado - notificaciones, navbar fixes, panel admin"',
    "git push origin main"
]

for cmd in commands:
    print(f"\n🔧 Ejecutando: {cmd}")
    result = os.system(cmd)
    if result == 0:
        print("✅ Comando exitoso")
    else:
        print(f"⚠️  Código de salida: {result}")

print("\n🎉 Proceso completado")
print("📍 Verifica en GitHub: https://github.com/Seba-Truji94/Project2025")
