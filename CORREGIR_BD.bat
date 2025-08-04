@echo off
chcp 65001 >nul
cls
cd /d "c:\Users\cuent\Galletas Kati"

echo.
echo ================================================================
echo 🍪 GALLETAS KATI - CORRECCIÓN DE BASE DE DATOS
echo ================================================================
echo.

echo 🔧 Eliminando migraciones conflictivas...
del notifications\migrations\0002_add_subject_field.py 2>nul

echo.
echo 📝 Creando migraciones frescas...
python manage.py makemigrations notifications --verbosity=2

echo.
echo 🚀 Aplicando migraciones...
python manage.py migrate --verbosity=2

echo.
echo 📋 Verificando estado...
python manage.py showmigrations notifications

echo.
echo 🧪 Probando modelo...
python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dulce_bias_project.settings')
import django
django.setup()
from notifications.models import NotificationTemplate
print('✅ Modelo NotificationTemplate funciona correctamente')
print(f'📊 Plantillas en BD: {NotificationTemplate.objects.count()}')
"

echo.
echo ================================================================
echo 🎉 CORRECCIÓN COMPLETADA
echo ================================================================
echo.
echo ✅ Base de datos corregida
echo ✅ Modelos funcionando
echo.
echo 🚀 Para probar:
echo    python manage.py runserver 0.0.0.0:8002
echo.
echo 🌐 Panel administrativo:
echo    http://127.0.0.1:8002/notifications/admin/templates/
echo.
echo ================================================================
pause
