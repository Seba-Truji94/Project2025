#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dulce_bias_project.settings')
django.setup()

from django.db import connection

# Obtener cursor de la base de datos
cursor = connection.cursor()

print("🔧 CORRECCIÓN DE BASE DE DATOS")
print("=" * 50)

try:
    # Verificar estructura actual
    cursor.execute("PRAGMA table_info(notifications_notificationtemplate);")
    columns = cursor.fetchall()
    
    print("📋 Estructura actual:")
    column_names = [col[1] for col in columns]
    for col in columns:
        print(f"   - {col[1]} ({col[2]})")
    
    # Agregar columnas faltantes
    fixes = []
    
    if 'subject' not in column_names:
        cursor.execute("ALTER TABLE notifications_notificationtemplate ADD COLUMN subject VARCHAR(200) DEFAULT '';")
        fixes.append("subject")
        print("✅ Columna 'subject' agregada")
    
    if 'template_body' not in column_names:
        cursor.execute("ALTER TABLE notifications_notificationtemplate ADD COLUMN template_body TEXT DEFAULT '';")
        fixes.append("template_body")
        print("✅ Columna 'template_body' agregada")
    
    if fixes:
        print(f"\n🎉 Correcciones aplicadas: {', '.join(fixes)}")
    else:
        print("\n✅ No se necesitan correcciones")
    
    # Verificar después de correcciones
    cursor.execute("PRAGMA table_info(notifications_notificationtemplate);")
    columns = cursor.fetchall()
    
    print("\n📋 Estructura final:")
    for col in columns:
        print(f"   - {col[1]} ({col[2]})")
    
    print("\n🚀 Base de datos corregida. Reinicia el servidor.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\n🔧 Alternativa: Ejecutar migraciones manuales")
