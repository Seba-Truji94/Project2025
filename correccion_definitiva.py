#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SOLUCIÓN DEFINITIVA PARA GALLETAS KATI
Base de datos SQLite - Agregar columnas faltantes
"""

import sqlite3
import sys
import os

def main():
    print("=" * 60)
    print("🛠️  GALLETAS KATI - CORRECCIÓN DE BASE DE DATOS")
    print("=" * 60)
    
    db_file = 'db.sqlite3'
    
    # Verificar que existe la base de datos
    if not os.path.exists(db_file):
        print(f"❌ ERROR: No se encontró {db_file}")
        print("🔧 Ejecuta primero: python manage.py migrate")
        return False
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        print(f"✅ Conectado a {db_file}")
        
        # Verificar que existe la tabla
        table_name = 'notifications_notificationtemplate'
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name=?
        """, (table_name,))
        
        if not cursor.fetchone():
            print(f"❌ ERROR: La tabla {table_name} no existe")
            print("🔧 Ejecuta: python manage.py migrate notifications")
            return False
        
        print(f"✅ Tabla {table_name} encontrada")
        
        # Obtener estructura actual
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print(f"\n📋 Estructura actual ({len(columns)} columnas):")
        for i, col in enumerate(columns, 1):
            print(f"   {i:2d}. {col[1]:20} ({col[2]})")
        
        # Verificar columnas requeridas
        required_columns = {
            'subject': "VARCHAR(200) DEFAULT ''",
            'template_body': "TEXT DEFAULT ''"
        }
        
        changes_made = []
        
        for col_name, col_definition in required_columns.items():
            if col_name not in column_names:
                try:
                    sql = f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_definition}"
                    cursor.execute(sql)
                    changes_made.append(col_name)
                    print(f"✅ Agregada columna: {col_name}")
                except Exception as e:
                    print(f"❌ Error agregando {col_name}: {e}")
                    return False
            else:
                print(f"✅ Columna {col_name} ya existe")
        
        # Guardar cambios
        if changes_made:
            conn.commit()
            print(f"\n🎉 CAMBIOS GUARDADOS: {', '.join(changes_made)}")
        else:
            print(f"\n✅ NO SE NECESITAN CAMBIOS")
        
        # Verificar estructura final
        cursor.execute(f"PRAGMA table_info({table_name})")
        final_columns = cursor.fetchall()
        
        print(f"\n📊 Estructura final ({len(final_columns)} columnas):")
        for i, col in enumerate(final_columns, 1):
            status = "🆕" if col[1] in changes_made else "✅"
            print(f"   {i:2d}. {status} {col[1]:20} ({col[2]})")
        
        print("\n" + "=" * 60)
        print("🎉 CORRECCIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 60)
        print("\n🚀 AHORA PUEDES INICIAR EL SERVIDOR:")
        print("   python manage.py runserver 8002")
        print("\n🌐 Y ACCEDER A:")
        print("   http://127.0.0.1:8002/notifications/admin/templates/")
        print("=" * 60)
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Error de SQLite: {e}")
        return False
    except Exception as e:
        print(f"❌ Error general: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()
            print("🔒 Conexión cerrada")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
