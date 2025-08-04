@echo off
echo ================================================================
echo 🎉 GALLETAS KATI - REINICIANDO SERVIDOR
echo ================================================================
echo.
echo ✅ Template template_form.html creado
echo ✅ Formulario NotificationTemplateForm corregido  
echo ✅ Vista template_create actualizada
echo.
echo 🚀 Reiniciando servidor en puerto 8002...
echo ================================================================
echo.
echo 🌐 URLs disponibles:
echo    http://127.0.0.1:8002/notifications/admin/templates/
echo    http://127.0.0.1:8002/notifications/admin/templates/create/
echo.
echo Presiona Ctrl+C para detener el servidor
echo ================================================================

cd /d "c:\Users\cuent\Galletas Kati"
python manage.py runserver 8002
