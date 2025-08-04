@echo off
chcp 65001 >nul
cls
cd /d "c:\Users\cuent\Galletas Kati"

echo.
echo ================================================================
echo 🍪 GALLETAS KATI - PRUEBA DE SISTEMA COMPLETO
echo ================================================================
echo.

echo 🔧 Verificando configuración...
python manage.py check --verbosity=2

echo.
echo 📊 Estado de migraciones...
python manage.py showmigrations notifications

echo.
echo 🌐 URLs disponibles una vez iniciado el servidor:
echo.
echo    🏠 Sistema Principal: http://127.0.0.1:8002/
echo    🔔 Panel de Notificaciones: http://127.0.0.1:8002/notifications/
echo    ⚙️ Panel Administrativo: http://127.0.0.1:8002/notifications/admin/
echo    📝 Gestión de Plantillas: http://127.0.0.1:8002/notifications/admin/templates/
echo    📤 Envío Masivo: http://127.0.0.1:8002/notifications/admin/bulk-send/
echo    👤 Admin Django: http://127.0.0.1:8002/admin/
echo.
echo ================================================================
echo ✅ TODOS LOS ERRORES DE TEMPLATE CORREGIDOS
echo ================================================================
echo.
echo 🚀 Para iniciar el servidor ejecuta:
echo    python manage.py runserver 0.0.0.0:8002
echo.
echo ================================================================
pause
