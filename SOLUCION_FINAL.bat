@echo off
chcp 65001 >nul
cls
cd /d "c:\Users\cuent\Galletas Kati"

echo.
echo ================================================================
echo GALLETAS KATI - SOLUCION DEFINITIVA BASE DE DATOS
echo ================================================================
echo.

echo Paso 1: Verificando y corrigiendo base de datos...
python -c "import sqlite3; import sys; conn = sqlite3.connect('db.sqlite3'); cursor = conn.cursor(); cursor.execute(\"SELECT name FROM sqlite_master WHERE type='table' AND name='notifications_notificationtemplate';\"); table_exists = cursor.fetchone(); print('Tabla existe:', bool(table_exists)); cursor.execute('PRAGMA table_info(notifications_notificationtemplate)') if table_exists else None; columns = [col[1] for col in cursor.fetchall()] if table_exists else []; print('Columnas encontradas:', len(columns)); has_subject = 'subject' in columns; has_template_body = 'template_body' in columns; print('Tiene subject:', has_subject); print('Tiene template_body:', has_template_body); cursor.execute('ALTER TABLE notifications_notificationtemplate ADD COLUMN subject VARCHAR(200) DEFAULT \"\"') if table_exists and not has_subject else None; cursor.execute('ALTER TABLE notifications_notificationtemplate ADD COLUMN template_body TEXT DEFAULT \"\"') if table_exists and not has_template_body else None; conn.commit(); cursor.execute('PRAGMA table_info(notifications_notificationtemplate)'); final_columns = [col[1] for col in cursor.fetchall()]; print('Columnas finales:', len(final_columns)); print('CORRECCION COMPLETADA'); conn.close()"

echo.
echo Paso 2: Aplicando migraciones...
python manage.py migrate

echo.
echo Paso 3: Iniciando servidor en puerto 8002...
echo ================================================================
echo Accede a: http://127.0.0.1:8002/notifications/admin/templates/
echo ================================================================
python manage.py runserver 8002
