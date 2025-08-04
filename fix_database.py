#!/usr/bin/env python
"""
Script para inspeccionar y corregir la estructura de la base de datos
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dulce_bias_project.settings')
django.setup()

from django.db import connection
from django.core.management import call_command

def inspect_database():
    """Inspeccionar la estructura de la base de datos"""
    print("================================================================")
    print("🔍 INSPECCIÓN DE BASE DE DATOS - NOTIFICACIONES")
    print("================================================================")
    
    with connection.cursor() as cursor:
        # Verificar si la tabla existe
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='notifications_notificationtemplate';
        """)
        table_exists = cursor.fetchone()
        
        if table_exists:
            print("✅ Tabla notifications_notificationtemplate encontrada")
            
            # Obtener estructura de la tabla
            cursor.execute("PRAGMA table_info(notifications_notificationtemplate);")
            columns = cursor.fetchall()
            
            print("\n📋 Columnas actuales:")
            column_names = []
            for col in columns:
                column_names.append(col[1])
                print(f"   • {col[1]} ({col[2]})")
            
            # Verificar si falta la columna subject
            if 'subject' not in column_names:
                print("\n❌ PROBLEMA: Falta la columna 'subject'")
                print("🔧 Intentando corregir...")
                
                try:
                    # Añadir la columna subject
                    cursor.execute("""
                        ALTER TABLE notifications_notificationtemplate 
                        ADD COLUMN subject VARCHAR(200) DEFAULT '';
                    """)
                    print("✅ Columna 'subject' añadida exitosamente")
                except Exception as e:
                    print(f"❌ Error al añadir columna: {e}")
            else:
                print("✅ La columna 'subject' existe")
                
        else:
            print("❌ Tabla notifications_notificationtemplate NO encontrada")
            print("🔧 Ejecutando migraciones...")
            
            try:
                call_command('migrate', verbosity=2)
                print("✅ Migraciones ejecutadas")
            except Exception as e:
                print(f"❌ Error en migraciones: {e}")

def verify_models():
    """Verificar que los modelos se puedan importar"""
    print("\n================================================================")
    print("🔍 VERIFICACIÓN DE MODELOS")
    print("================================================================")
    
    try:
        from notifications.models import NotificationTemplate, Notification
        print("✅ Modelos importados correctamente")
        
        # Probar crear una instancia de prueba
        template_count = NotificationTemplate.objects.count()
        notification_count = Notification.objects.count()
        
        print(f"📊 Plantillas en BD: {template_count}")
        print(f"📊 Notificaciones en BD: {notification_count}")
        
    except Exception as e:
        print(f"❌ Error al verificar modelos: {e}")

if __name__ == '__main__':
    inspect_database()
    verify_models()
    
    print("\n================================================================")
    print("🎉 VERIFICACIÓN COMPLETADA")
    print("================================================================")
    print("\n🚀 Para probar el sistema:")
    print("   python manage.py runserver 0.0.0.0:8002")
    print("\n🌐 URL del panel administrativo:")
    print("   http://127.0.0.1:8002/notifications/admin/templates/")
