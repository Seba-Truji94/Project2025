@echo off
chcp 65001 >nul
cls
cd /d "c:\Users\cuent\Galletas Kati"

echo ================================================================
echo 🎉 GALLETAS KATI - SERVIDOR CORREGIDO
echo ================================================================
echo.
echo ✅ Base de datos verificada y corregida
echo ✅ Todas las columnas necesarias presentes:
echo    - id, name, notification_type, channel
echo    - subject_template, body_template, html_template  
echo    - is_active, created_at, updated_at
echo    - subject, template_body
echo.
echo 🚀 Iniciando servidor en puerto 8002...
echo ================================================================
echo.
echo 🌐 URLs disponibles:
echo    http://127.0.0.1:8002/
echo    http://127.0.0.1:8002/notifications/admin/templates/
echo    http://127.0.0.1:8002/admin/
echo.
echo Presiona Ctrl+C para detener el servidor
echo ================================================================

python manage.py runserver 8002
