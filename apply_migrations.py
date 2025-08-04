import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dulce_bias_project.settings')
django.setup()

from django.core.management import execute_from_command_line

print("🚀 Aplicando migraciones...")
execute_from_command_line(['manage.py', 'migrate'])
print("✅ ¡Migraciones aplicadas!")
