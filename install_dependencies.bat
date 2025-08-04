@echo off
chcp 65001 >nul
cls
cd /d "c:\Users\cuent\Galletas Kati"

echo.
echo ================================================================
echo 🍪 GALLETAS KATI - INSTALADOR DE DEPENDENCIAS
echo ================================================================
echo.
echo 📦 Instalando paquetes necesarios para notificaciones...
echo.

echo 🔄 Actualizando pip...
python -m pip install --upgrade pip
echo.

echo 📦 Instalando Celery (procesamiento asíncrono)...
python -m pip install celery==5.3.4
echo.

echo 📦 Instalando Redis (broker para Celery)...
python -m pip install redis==5.0.1
echo.

echo 📦 Instalando Twilio (SMS y WhatsApp)...
python -m pip install twilio==8.10.3
echo.

echo 📦 Instalando Requests (llamadas HTTP)...
python -m pip install requests==2.31.0
echo.

echo 📦 Instalando validadores de teléfono...
python -m pip install phonenumbers==8.13.25
python -m pip install django-phonenumber-field==7.3.0
echo.

echo ================================================================
echo 🎉 INSTALACIÓN COMPLETADA
echo ================================================================
echo.
echo ✅ Dependencias instaladas:
echo    • Celery - Procesamiento asíncrono
echo    • Redis - Broker de mensajes
echo    • Twilio - SMS y WhatsApp
echo    • Requests - Llamadas HTTP
echo    • PhoneNumbers - Validación de teléfonos
echo.
echo 🚀 Ahora puedes ejecutar:
echo    • python manage.py runserver 127.0.0.1:8002
echo    • celery -A galletas_kati worker --loglevel=info
echo    • celery -A galletas_kati beat --loglevel=info
echo.
echo 📍 URLs del sistema:
echo    🏠 http://127.0.0.1:8002/ (Sitio principal)
echo    🔔 http://127.0.0.1:8002/notifications/ (Notificaciones)
echo    🔧 http://127.0.0.1:8002/management/ (Admin)
echo ================================================================
echo.
pause
