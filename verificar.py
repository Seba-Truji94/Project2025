print("=== VERIFICACIÓN SISTEMA ===")
import sys
print(f"Python: {sys.version}")
import os
print(f"Directorio: {os.getcwd()}")
print(f"Archivos Python: {[f for f in os.listdir('.') if f.endswith('.py')]}")

# Verificar manage.py
if os.path.exists('manage.py'):
    print("✅ manage.py encontrado")
else:
    print("❌ manage.py NO encontrado")

# Verificar directorio notifications
if os.path.exists('notifications'):
    print("✅ Directorio notifications encontrado")
    print(f"   Archivos: {os.listdir('notifications')}")
else:
    print("❌ Directorio notifications NO encontrado")

print("=== FIN VERIFICACIÓN ===")
