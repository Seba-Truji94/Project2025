import sqlite3
import sys

print("🛠️ SOLUCIÓN DEFINITIVA - COLUMNAS FALTANTES")
print("=" * 50)

try:
    # Conectar a la base de datos
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    # Verificar si la tabla existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='notifications_notificationtemplate';")
    if not cursor.fetchone():
        print("❌ ERROR: La tabla notifications_notificationtemplate no existe")
        print("🔧 Ejecuta: python manage.py migrate")
        sys.exit(1)
    
    print("✅ Tabla notifications_notificationtemplate encontrada")
    
    # Obtener columnas actuales
    cursor.execute("PRAGMA table_info(notifications_notificationtemplate);")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    
    print(f"\n📋 Columnas actuales ({len(column_names)}):")
    for col in columns:
        print(f"   • {col[1]} ({col[2]})")
    
    # Verificar columnas específicas
    missing_columns = []
    
    if 'subject' not in column_names:
        missing_columns.append('subject')
    
    if 'template_body' not in column_names:
        missing_columns.append('template_body')
    
    if missing_columns:
        print(f"\n❌ Columnas faltantes: {', '.join(missing_columns)}")
        
        # Agregar columnas faltantes
        for column in missing_columns:
            if column == 'subject':
                sql = "ALTER TABLE notifications_notificationtemplate ADD COLUMN subject VARCHAR(200) DEFAULT '';"
            elif column == 'template_body':
                sql = "ALTER TABLE notifications_notificationtemplate ADD COLUMN template_body TEXT DEFAULT '';"
            
            try:
                cursor.execute(sql)
                print(f"   ✅ Agregada: {column}")
            except Exception as e:
                print(f"   ❌ Error agregando {column}: {e}")
        
        # Confirmar cambios
        conn.commit()
        print("\n🎉 CAMBIOS GUARDADOS")
    else:
        print("\n✅ Todas las columnas necesarias están presentes")
    
    # Verificar estructura final
    cursor.execute("PRAGMA table_info(notifications_notificationtemplate);")
    columns = cursor.fetchall()
    
    print(f"\n📊 Estructura final ({len(columns)} columnas):")
    for col in columns:
        print(f"   ✅ {col[1]} ({col[2]})")
    
    print(f"\n🚀 BASE DE DATOS CORREGIDA")
    print("   Ahora puedes acceder a: http://127.0.0.1:8002/notifications/admin/templates/")

except sqlite3.Error as e:
    print(f"❌ Error de SQLite: {e}")
except Exception as e:
    print(f"❌ Error general: {e}")
finally:
    if 'conn' in locals():
        conn.close()
        print("\n🔒 Conexión cerrada")
