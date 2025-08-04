import sqlite3
import os

print("🔧 CORRECCIÓN DIRECTA SQLITE")
print("=" * 40)

db_path = 'db.sqlite3'

if not os.path.exists(db_path):
    print("❌ No se encontró db.sqlite3")
    exit()

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Verificar tabla
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='notifications_notificationtemplate';")
    if not cursor.fetchone():
        print("❌ Tabla no existe")
        exit()
    
    print("✅ Tabla encontrada")
    
    # Verificar columnas
    cursor.execute("PRAGMA table_info(notifications_notificationtemplate);")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    
    print(f"📋 Columnas actuales: {column_names}")
    
    # Agregar columnas faltantes
    if 'subject' not in column_names:
        cursor.execute("ALTER TABLE notifications_notificationtemplate ADD COLUMN subject VARCHAR(200) DEFAULT '';")
        print("✅ Agregada: subject")
    
    if 'template_body' not in column_names:
        cursor.execute("ALTER TABLE notifications_notificationtemplate ADD COLUMN template_body TEXT DEFAULT '';")
        print("✅ Agregada: template_body")
    
    conn.commit()
    
    # Verificar final
    cursor.execute("PRAGMA table_info(notifications_notificationtemplate);")
    columns = cursor.fetchall()
    
    print("\n📋 Columnas finales:")
    for col in columns:
        print(f"   {col[1]}")
    
    print("\n🎉 ¡CORREGIDO! Reinicia el servidor")
    
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    if 'conn' in locals():
        conn.close()
