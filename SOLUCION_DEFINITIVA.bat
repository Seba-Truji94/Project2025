@echo off
chcp 65001 >nul
cls
cd /d "c:\Users\cuent\Galletas Kati"

echo ================================================================
echo 🛠️ GALLETAS KATI - SOLUCIÓN DEFINITIVA BASE DE DATOS
echo ================================================================
echo.

echo 🔧 Paso 1: Deteniendo servidor si está corriendo...
taskkill /f /im python.exe 2>nul

echo.
echo 📋 Paso 2: Verificando estructura actual...
python -c "
import sqlite3
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()
try:
    cursor.execute('PRAGMA table_info(notifications_notificationtemplate);')
    columns = cursor.fetchall()
    print('Columnas actuales:')
    for col in columns:
        print(f'  - {col[1]}')
    column_names = [col[1] for col in columns]
    if 'subject' not in column_names:
        print('❌ Falta columna: subject')
    if 'template_body' not in column_names:
        print('❌ Falta columna: template_body')
except Exception as e:
    print(f'Error: {e}')
finally:
    conn.close()
"

echo.
echo 🔧 Paso 3: Aplicando corrección directa...
python -c "
import sqlite3
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()
try:
    # Verificar si la tabla existe
    cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\" AND name=\"notifications_notificationtemplate\";')
    if cursor.fetchone():
        print('✅ Tabla encontrada')
        
        # Obtener columnas actuales
        cursor.execute('PRAGMA table_info(notifications_notificationtemplate);')
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        # Agregar columnas faltantes
        if 'subject' not in column_names:
            cursor.execute('ALTER TABLE notifications_notificationtemplate ADD COLUMN subject VARCHAR(200) DEFAULT \"\";')
            print('✅ Agregada columna: subject')
        else:
            print('✅ Columna subject ya existe')
            
        if 'template_body' not in column_names:
            cursor.execute('ALTER TABLE notifications_notificationtemplate ADD COLUMN template_body TEXT DEFAULT \"\";')
            print('✅ Agregada columna: template_body')
        else:
            print('✅ Columna template_body ya existe')
        
        conn.commit()
        print('🎉 Base de datos actualizada')
    else:
        print('❌ Tabla no encontrada')
except Exception as e:
    print(f'Error: {e}')
finally:
    conn.close()
"

echo.
echo 📋 Paso 4: Verificando corrección...
python -c "
import sqlite3
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()
try:
    cursor.execute('PRAGMA table_info(notifications_notificationtemplate);')
    columns = cursor.fetchall()
    print('Estructura final:')
    for col in columns:
        print(f'  ✅ {col[1]} ({col[2]})')
except Exception as e:
    print(f'Error: {e}')
finally:
    conn.close()
"

echo.
echo 🚀 Paso 5: Iniciando servidor corregido...
echo ================================================================
echo 🌐 Accede a: http://127.0.0.1:8002/notifications/admin/templates/
echo ================================================================
python manage.py runserver 8002
