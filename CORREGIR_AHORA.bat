@echo off
echo ================================================================
echo 🔧 GALLETAS KATI - CORRECCIÓN DE BASE DE DATOS
echo ================================================================

cd /d "c:\Users\cuent\Galletas Kati"

echo.
echo 📊 Ejecutando corrección directa...
python fix_simple.py

echo.
echo 🚀 Aplicando migración manual...
python manage.py migrate notifications 0003_fix_missing_columns --fake

echo.
echo ✅ Reiniciando servidor en puerto 8002...
echo Presiona Ctrl+C para detener
echo ================================================================
python manage.py runserver 8002
