#!/usr/bin/env python
"""
Script para probar el acceso al admin después de la corrección del middleware
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dulce_bias_project.settings')
django.setup()

def test_middleware():
    """Probar que el middleware funciona correctamente"""
    from django.test import RequestFactory
    
    factory = RequestFactory()
    
    # Crear un request simulado al admin
    request = factory.post('/admin/login/', {'username': 'test', 'password': 'test'})
    
    # Importar y probar el middleware
    from security.middleware import SecurityLogMiddleware
    middleware = SecurityLogMiddleware(lambda r: None)
    
    # Simular que no hay user (como en el caso real)
    try:
        result = middleware.process_request(request)
        print("✅ Middleware funciona correctamente - no hay errores")
        return True
    except AttributeError as e:
        print(f"❌ Error en middleware: {e}")
        return False

if __name__ == "__main__":
    print("🔒 Probando middleware de seguridad...")
    if test_middleware():
        print("✅ El problema del middleware ha sido resuelto")
    else:
        print("❌ Aún hay problemas con el middleware")
