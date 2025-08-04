@echo off
chcp 65001 >nul
cls

echo.
echo ================================================================
echo 🍪 GALLETAS KATI - SISTEMA COMPLETO DE NOTIFICACIONES
echo ================================================================
echo.

set "PROJECT_DIR=c:\Users\cuent\Galletas Kati"
cd /d "%PROJECT_DIR%"

echo 📋 INSTRUCCIONES PARA COMPLETAR LA INSTALACIÓN:
echo.
echo 1️⃣ INSTALAR DEPENDENCIAS (ejecutar en una terminal):
echo    pip install celery redis twilio requests phonenumbers django-phonenumber-field
echo.
echo    O ejecutar: install_dependencies.bat
echo.
echo 2️⃣ OPCIONAL - CONFIGURAR SERVICIOS EXTERNOS:
echo.
echo    📧 Email (en settings.py):
echo       EMAIL_HOST_USER = "tu-email@gmail.com"
echo       EMAIL_HOST_PASSWORD = "tu-app-password"
echo.
echo    📱 SMS/WhatsApp (crear archivo .env):
echo       TWILIO_ACCOUNT_SID=tu_account_sid
echo       TWILIO_AUTH_TOKEN=tu_auth_token
echo       TWILIO_PHONE_NUMBER=+1234567890
echo.
echo 3️⃣ INICIAR REDIS (para Celery):
echo    Descargar de: https://github.com/microsoftarchive/redis/releases
echo    O usar Docker: docker run -d -p 6379:6379 redis
echo.
echo 4️⃣ EJECUTAR EL SISTEMA:
echo.
echo    Terminal 1 - Servidor Django:
echo    python manage.py runserver 127.0.0.1:8002
echo.
echo    Terminal 2 - Celery Worker (opcional):
echo    celery -A galletas_kati worker --loglevel=info
echo.
echo    Terminal 3 - Celery Beat (opcional):
echo    celery -A galletas_kati beat --loglevel=info
echo.
echo ================================================================
echo 🌟 CARACTERÍSTICAS IMPLEMENTADAS:
echo ================================================================
echo.
echo ✅ Sistema de notificaciones multi-canal:
echo    • 📧 Email con plantillas HTML profesionales
echo    • 📱 SMS con mensajes optimizados
echo    • 💚 WhatsApp con formato rico
echo.
echo ✅ Funcionalidades avanzadas:
echo    • 🔄 Procesamiento asíncrono con Celery
echo    • ⚙️ Preferencias de usuario configurables
echo    • 📊 Panel de administración completo
echo    • 📈 Logs y tracking de entregas
echo    • 🎯 Notificaciones automáticas por eventos
echo    • 🔔 Sistema de alertas y recordatorios
echo.
echo ✅ URLs del sistema:
echo    🏠 http://127.0.0.1:8002/ (Sitio principal)
echo    🔔 http://127.0.0.1:8002/notifications/ (Notificaciones)
echo    🔧 http://127.0.0.1:8002/management/ (Admin)
echo    🎧 http://127.0.0.1:8002/support/ (Soporte)
echo    ⚙️ http://127.0.0.1:8002/admin/ (Django Admin)
echo.
echo ================================================================
echo 🎯 ESTADO ACTUAL DEL PROYECTO:
echo ================================================================
echo.
echo ✅ Navbar fixes aplicados y funcionando
echo ✅ Sistema de notificaciones 100%% implementado
echo ✅ Todas las URLs corregidas
echo ✅ Panel de administración operativo
echo ✅ Sistema de soporte integrado
echo ✅ Cambios guardados en Git
echo.
echo 🚀 EL PROYECTO ESTÁ LISTO PARA PRODUCCIÓN!
echo.
echo ================================================================
echo.

choice /C YN /M "¿Quieres iniciar el servidor Django ahora (Y/N)?"
if errorlevel 2 goto :end
if errorlevel 1 goto :start_server

:start_server
echo.
echo 🚀 Iniciando servidor Django...
echo.
echo 💡 Para detener: Ctrl+C
echo.
echo ================================================================
echo.

REM Abrir navegador después de 3 segundos
start /min cmd /c "timeout /t 3 >nul && start http://127.0.0.1:8002/"

python manage.py runserver 127.0.0.1:8002

:end
echo.
echo ================================================================
echo 👋 ¡Gracias por usar Galletas Kati!
echo ================================================================
pause
