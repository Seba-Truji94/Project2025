@echo off
echo � Paso 1: Corrigiendo base de datos SQLite...
python -c "
import sqlite3
conn = sqlite3.connect('db.sqlite3')
c = conn.cursor()

# Verificar y corregir NotificationTemplate
c.execute('SELECT name FROM sqlite_master WHERE type=\"table\" AND name=\"notifications_notificationtemplate\";')
template_exists = c.fetchone()
if template_exists:
    c.execute('PRAGMA table_info(notifications_notificationtemplate);')
    template_columns = [col[1] for col in c.fetchall()]
    print('Tabla NotificationTemplate - Columnas:', template_columns)
    
    if 'subject' not in template_columns:
        c.execute('ALTER TABLE notifications_notificationtemplate ADD COLUMN subject VARCHAR(200) DEFAULT \"\";')
        print('✅ Agregada columna subject')
    
    if 'template_body' not in template_columns:
        c.execute('ALTER TABLE notifications_notificationtemplate ADD COLUMN template_body TEXT DEFAULT \"\";')
        print('✅ Agregada columna template_body')

# Verificar y corregir UserNotificationPreference
c.execute('SELECT name FROM sqlite_master WHERE type=\"table\" AND name=\"notifications_usernotificationpreference\";')
pref_exists = c.fetchone()
if pref_exists:
    c.execute('PRAGMA table_info(notifications_usernotificationpreference);')
    pref_columns = [col[1] for col in c.fetchall()]
    print('Tabla UserNotificationPreference - Columnas:', pref_columns)
    
    required_cols = [
        ('order_notifications', 'BOOLEAN DEFAULT 1'),
        ('shipping_notifications', 'BOOLEAN DEFAULT 1'),
        ('promotional_notifications', 'BOOLEAN DEFAULT 1'),
        ('support_notifications', 'BOOLEAN DEFAULT 1'),
        ('email_enabled', 'BOOLEAN DEFAULT 1'),
        ('sms_enabled', 'BOOLEAN DEFAULT 0'),
        ('whatsapp_enabled', 'BOOLEAN DEFAULT 0'),
        ('push_enabled', 'BOOLEAN DEFAULT 1'),
        ('phone_number', 'VARCHAR(20) DEFAULT \"\"'),
        ('whatsapp_number', 'VARCHAR(20) DEFAULT \"\"')
    ]
    
    for col_name, col_def in required_cols:
        if col_name not in pref_columns:
            c.execute(f'ALTER TABLE notifications_usernotificationpreference ADD COLUMN {col_name} {col_def};')
            print(f'✅ Agregada columna {col_name}')

conn.commit()
conn.close()
print('🎉 BASE DE DATOS COMPLETAMENTE CORREGIDA')
"cp 65001 >nul
cls
cd /d "c:\Users\cuent\Galletas Kati"

echo.
echo ================================================================
echo 🍪 GALLETAS KATI - CONFIGURACIÓN FINAL DE BASE DE DATOS
echo ================================================================
echo.

echo � Paso 1: Corrigiendo base de datos SQLite...
python -c "import sqlite3; conn=sqlite3.connect('db.sqlite3'); c=conn.cursor(); c.execute('SELECT name FROM sqlite_master WHERE type=\"table\" AND name=\"notifications_notificationtemplate\";'); table_exists=c.fetchone(); print('Tabla existe:', bool(table_exists)); c.execute('PRAGMA table_info(notifications_notificationtemplate);') if table_exists else None; columns=[col[1] for col in c.fetchall()] if table_exists else []; print('Columnas actuales:', columns); c.execute('ALTER TABLE notifications_notificationtemplate ADD COLUMN subject VARCHAR(200) DEFAULT \"\";') if table_exists and 'subject' not in columns else None; c.execute('ALTER TABLE notifications_notificationtemplate ADD COLUMN template_body TEXT DEFAULT \"\";') if table_exists and 'template_body' not in columns else None; conn.commit(); conn.close(); print('BASE DE DATOS CORREGIDA')"

echo.
echo �📝 Paso 2: Creando migraciones para notificaciones...
python manage.py makemigrations notifications --verbosity=2

echo.
echo 🚀 Paso 3: Aplicando todas las migraciones...
python manage.py migrate --verbosity=2

echo.
echo 📋 Paso 4: Verificando estado de migraciones...
python manage.py showmigrations

echo.
echo ================================================================
echo 🎉 CONFIGURACIÓN COMPLETADA
echo ================================================================
echo.
echo ✅ Base de datos configurada
echo ✅ Sistema de notificaciones operativo
echo.
echo 🚀 Paso 5: Iniciando servidor en puerto 8002...
echo ================================================================
echo.
echo 🌐 Servidor iniciando en: http://127.0.0.1:8002
echo 📋 Panel de notificaciones: http://127.0.0.1:8002/notifications/admin/templates/
echo 👤 Administración: http://127.0.0.1:8002/admin/
echo.
echo Presiona Ctrl+C para detener el servidor
echo ================================================================
python manage.py runserver 8002
