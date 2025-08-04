@echo off
cd /d "c:\Users\cuent\Galletas Kati"
echo.
echo =================================================
echo 🚀 INICIANDO SERVIDOR DJANGO - GALLETAS KATI
echo =================================================
echo 📍 URL Principal: http://127.0.0.1:8002/
echo 🔧 Panel Admin: http://127.0.0.1:8002/management/
echo 📊 Alertas: http://127.0.0.1:8002/management/stock/alertas/
echo 📋 Reportes: http://127.0.0.1:8002/management/stock/reporte/
echo =================================================
echo 💡 Para detener: Ctrl+C
echo =================================================
echo.

python manage.py runserver 127.0.0.1:8002

pause
