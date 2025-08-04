#!/usr/bin/env python
"""
Diagnóstico rápido del sistema de notificaciones
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dulce_bias_project.settings')

try:
    django.setup()
    print("✅ Django configurado correctamente")
    
    # Probar importación de modelos
    from notifications.models import NotificationTemplate, Notification
    print("✅ Modelos importados correctamente")
    
    # Verificar estructura de modelo
    fields = [f.name for f in NotificationTemplate._meta.get_fields()]
    print(f"📋 Campos del modelo NotificationTemplate: {fields}")
    
    if 'subject' in fields:
        print("✅ Campo 'subject' encontrado en el modelo")
    else:
        print("❌ Campo 'subject' NO encontrado en el modelo")
        
    if 'template_body' in fields:
        print("✅ Campo 'template_body' encontrado en el modelo")
    else:
        print("❌ Campo 'template_body' NO encontrado en el modelo")
    
    # Probar acceso a la base de datos
    count = NotificationTemplate.objects.count()
    print(f"📊 Plantillas en base de datos: {count}")
    
    print("\n🎉 DIAGNÓSTICO COMPLETADO - Sistema funcionando")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print(f"Tipo de error: {type(e).__name__}")
    
    if "no such column" in str(e):
        print("\n🔧 SOLUCIÓN: Ejecutar migraciones")
        print("   python manage.py makemigrations notifications")
        print("   python manage.py migrate")
    elif "no such table" in str(e):
        print("\n🔧 SOLUCIÓN: La tabla no existe, ejecutar migrate")
        print("   python manage.py migrate")
    else:
        print("\n🔧 Error desconocido, revisar configuración")
