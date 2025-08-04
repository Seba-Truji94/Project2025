@echo off
echo 🚀 Iniciando Galletas Kati con soporte HTTPS...
echo.
echo 📋 Opciones disponibles:
echo 1. Servidor HTTP normal (puerto 8000)
echo 2. Servidor HTTPS con certificado auto-firmado (puerto 8001)
echo.
set /p choice=Selecciona opcion (1 o 2): 

if "%choice%"=="1" (
    echo.
    echo 🌐 Iniciando servidor HTTP en http://127.0.0.1:8000/
    echo.
    python manage.py runserver 127.0.0.1:8000
) else if "%choice%"=="2" (
    echo.
    echo 🔒 Iniciando servidor HTTPS en https://127.0.0.1:8001/
    echo ⚠️  Acepta el certificado auto-firmado en tu navegador
    echo.
    python manage.py runserver_plus --cert-file cert.pem 127.0.0.1:8001
) else (
    echo.
    echo ❌ Opcion no valida. Iniciando servidor HTTP por defecto...
    echo.
    python manage.py runserver 127.0.0.1:8000
)

pause
