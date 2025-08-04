@echo off
cd /d "c:\Users\cuent\Galletas Kati"

echo ================================================================
echo 🛠️ CORRIGIENDO BASE DE DATOS AHORA...
echo ================================================================

python -c "
import sqlite3
print('🔧 Conectando a base de datos...')
conn = sqlite3.connect('db.sqlite3')
c = conn.cursor()

# Verificar tabla
c.execute('SELECT name FROM sqlite_master WHERE type=\"table\" AND name=\"notifications_notificationtemplate\";')
if c.fetchone():
    print('✅ Tabla encontrada')
    
    # Obtener columnas
    c.execute('PRAGMA table_info(notifications_notificationtemplate);')
    columns = [col[1] for col in c.fetchall()]
    print(f'📋 Columnas actuales: {len(columns)}')
    
    # Agregar columnas faltantes
    if 'subject' not in columns:
        c.execute('ALTER TABLE notifications_notificationtemplate ADD COLUMN subject VARCHAR(200) DEFAULT \"\";')
        print('✅ Agregada: subject')
    else:
        print('✅ subject ya existe')
        
    if 'template_body' not in columns:
        c.execute('ALTER TABLE notifications_notificationtemplate ADD COLUMN template_body TEXT DEFAULT \"\";')
        print('✅ Agregada: template_body')  
    else:
        print('✅ template_body ya existe')
    
    conn.commit()
    print('🎉 BASE DE DATOS CORREGIDA')
else:
    print('❌ Tabla no encontrada')

conn.close()
"

echo.
echo ================================================================
echo 🚀 INICIANDO SERVIDOR...
echo ================================================================
python manage.py runserver 8002
