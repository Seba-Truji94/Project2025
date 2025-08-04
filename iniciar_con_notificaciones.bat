@echo off
chcp 65001 >nul
cls
cd /d "c:\Users\cuent\Galletas Kati"

echo.
echo ================================================================
echo 🍪 GALLETAS KATI - SISTEMA COMPLETO CON NOTIFICACIONES
echo ================================================================
echo.
echo 📍 URLs Principales:
echo    🏠 Sitio Principal: http://127.0.0.1:8002/
echo    🔧 Panel Admin: http://127.0.0.1:8002/management/
echo    📊 Stock y Alertas: http://127.0.0.1:8002/management/stock/alertas/
echo    📋 Reportes: http://127.0.0.1:8002/management/stock/reporte/
echo    🔔 Notificaciones: http://127.0.0.1:8002/notifications/
echo    🎧 Soporte: http://127.0.0.1:8002/support/
echo.
echo 🆕 Sistema de Notificaciones Implementado:
echo    ✅ Email, SMS y WhatsApp
echo    ✅ Notificaciones asíncronas con Celery
echo    ✅ Preferencias de usuario configurables
echo    ✅ Panel de administración completo
echo    ✅ Plantillas profesionales
echo.
echo 📝 Notas importantes:
echo    • Para usar notificaciones, instalar: pip install celery redis twilio
echo    • Para SMS/WhatsApp configurar credenciales en .env
echo    • Panel admin disponible en /admin/ con superusuario
echo.
echo ================================================================
echo 💡 Para detener el servidor: Ctrl+C
echo ================================================================
echo.

echo 🔍 Verificando configuración...
python manage.py check --deploy 2>nul
if errorlevel 1 (
    echo ⚠️  Advertencias en la configuración detectadas
    echo.
)

echo 🚀 Iniciando servidor Django...
echo.

REM Abrir navegador después de 3 segundos
start /min cmd /c "timeout /t 3 >nul && start http://127.0.0.1:8002/"

python manage.py runserver 127.0.0.1:8002

echo.
echo ================================================================
echo 🛑 Servidor detenido
echo ================================================================
pause
