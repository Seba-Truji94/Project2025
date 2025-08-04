import subprocess
import os

print("🍪 GALLETAS KATI - SUBIENDO CAMBIOS")
print("=" * 40)

os.chdir(r"c:\Users\cuent\Galletas Kati")

commands = [
    ("git add -A", "Agregando archivos"),
    ("git commit -m 'feat: Sistema completo - notificaciones y navbar'", "Creando commit"),
    ("git push origin main", "Subiendo al repositorio")
]

for cmd, desc in commands:
    print(f"\n{desc}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
        print(f"Código: {result.returncode}")
    except Exception as e:
        print(f"Error: {e}")

print("\n🎉 Proceso completado!")
