import os
import sys
print("=== INICIO DIAGNÓSTICO ===")
print(f"Python: {sys.version}")
print(f"Directorio: {os.getcwd()}")
print(f"Archivos: {[f for f in os.listdir('.') if f.endswith('.py')]}")

try:
    import django
    print(f"Django disponible: {django.VERSION}")
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dulce_bias_project.settings')
    django.setup()
    print("Django configurado ✅")
    
    from notifications.models import NotificationTemplate
    print("Modelos importados ✅")
    
    fields = [f.name for f in NotificationTemplate._meta.get_fields()]
    print(f"Campos: {fields}")
    
    count = NotificationTemplate.objects.count()
    print(f"Registros: {count}")
    print("TODO FUNCIONANDO ✅")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
