import subprocess
import sys
import os

print("🍪 Iniciando Galletas Kati...")
os.chdir(r"c:\Users\cuent\Galletas Kati")
subprocess.call([sys.executable, "manage.py", "runserver", "127.0.0.1:8002"])
