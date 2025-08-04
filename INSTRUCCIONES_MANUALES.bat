@echo off
echo.
echo ================================================================
echo 🛠️ SOLUCION RAPIDA - EJECUTA ESTOS COMANDOS MANUALMENTE
echo ================================================================
echo.
echo 1. ABRE UNA TERMINAL/CMD EN: c:\Users\cuent\Galletas Kati
echo.
echo 2. EJECUTA ESTOS COMANDOS UNO POR UNO:
echo.
echo    python fix_definitivo.py
echo.
echo    python manage.py runserver 8002
echo.
echo ================================================================
echo 3. DESPUES ACCEDE A:
echo ================================================================
echo.
echo    🌐 http://127.0.0.1:8002/notifications/admin/templates/
echo.
echo ================================================================
echo.
echo 💡 SI fix_definitivo.py NO FUNCIONA, ejecuta:
echo.
echo    python -c "import sqlite3; conn=sqlite3.connect('db.sqlite3'); c=conn.cursor(); c.execute('ALTER TABLE notifications_notificationtemplate ADD COLUMN subject VARCHAR(200) DEFAULT \"\";'); c.execute('ALTER TABLE notifications_notificationtemplate ADD COLUMN template_body TEXT DEFAULT \"\";'); conn.commit(); conn.close(); print('CORREGIDO')"
echo.
echo ================================================================
pause
