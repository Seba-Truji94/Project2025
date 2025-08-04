#!/usr/bin/env python
"""
Corrección directa de la base de datos SQLite
"""
import sqlite3
import os

db_path = 'db.sqlite3'

if not os.path.exists(db_path):
    print("❌ No se encontró db.sqlite3")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Verificar si la tabla existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='notifications_notificationtemplate';")
    table_exists = cursor.fetchone()
    
    if not table_exists:
        print("❌ La tabla notifications_notificationtemplate no existe")
        print("🔧 Ejecutar: python manage.py migrate")
        exit(1)
    
    print("✅ Tabla notifications_notificationtemplate encontrada")
    
    # Verificar estructura actual
    cursor.execute("PRAGMA table_info(notifications_notificationtemplate);")
    columns = cursor.fetchall()
    
    print("\n📋 Estructura actual de la tabla:")
    column_names = []
    for col in columns:
        column_names.append(col[1])
        print(f"   - {col[1]} ({col[2]})")
    
    # Verificar columnas específicas
    has_subject = 'subject' in column_names
    has_template_body = 'template_body' in column_names
    
    print(f"\n📊 Estado de columnas:")
    print(f"   subject: {'✅' if has_subject else '❌'}")
    print(f"   template_body: {'✅' if has_template_body else '❌'}")
    
    fixes_needed = []
    
    # Agregar columna subject si no existe
    if not has_subject:
        try:
            cursor.execute("ALTER TABLE notifications_notificationtemplate ADD COLUMN subject VARCHAR(200) DEFAULT '';")
            print("✅ Columna 'subject' agregada")
            fixes_needed.append("subject agregado")
        except Exception as e:
            print(f"❌ Error agregando 'subject': {e}")
    
    # Agregar columna template_body si no existe
    if not has_template_body:
        try:
            cursor.execute("ALTER TABLE notifications_notificationtemplate ADD COLUMN template_body TEXT DEFAULT '';")
            print("✅ Columna 'template_body' agregada")
            fixes_needed.append("template_body agregado")
        except Exception as e:
            print(f"❌ Error agregando 'template_body': {e}")
    
    if fixes_needed:
        conn.commit()
        print(f"\n🎉 Correcciones aplicadas: {', '.join(fixes_needed)}")
    else:
        print("\n✅ No se necesitan correcciones")
    
    # Verificar nuevamente
    cursor.execute("PRAGMA table_info(notifications_notificationtemplate);")
    columns = cursor.fetchall()
    
    print("\n📋 Estructura final de la tabla:")
    for col in columns:
        print(f"   - {col[1]} ({col[2]})")

except Exception as e:
    print(f"❌ Error: {e}")
finally:
    conn.close()

print("\n🔧 Ahora ejecuta: python manage.py runserver 8002")
