@echo off
chcp 65001 >nul
cls
cd /d "c:\Users\cuent\Galletas Kati"

echo.
echo ================================================================
echo 🍪 GALLETAS KATI - INICIANDO SERVIDOR EN PUERTO 8002
echo ================================================================
echo.

echo 🔧 Verificando configuración...
python manage.py check

echo.
echo 🚀 Iniciando servidor en puerto 8002...
echo.
echo 🌐 URL del sistema: http://127.0.0.1:8002/
echo 🔔 Panel de notificaciones: http://127.0.0.1:8002/notifications/
echo 👤 Panel administrativo: http://127.0.0.1:8002/admin/
echo 🛒 Tienda: http://127.0.0.1:8002/
echo.
echo ================================================================
echo Presiona Ctrl+C para detener el servidor
echo ================================================================
echo.

python manage.py runserver 0.0.0.0:8002
