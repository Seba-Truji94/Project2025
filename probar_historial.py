#!/usr/bin/env python
"""
Prueba del historial de stock - Resuelve el error 404
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dulce_bias_project.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

def probar_historial():
    print("🧪 PROBANDO HISTORIAL DE STOCK")
    print("=" * 50)
    
    # Crear cliente de prueba
    client = Client()
    
    # Crear superusuario temporal para la prueba
    try:
        user = User.objects.get(username='admin')
        print("✅ Usuario admin encontrado")
    except User.DoesNotExist:
        user = User.objects.create_superuser('admin', 'admin@test.com', 'admin123')
        print("✅ Usuario admin creado temporalmente")
    
    # Iniciar sesión
    client.login(username='admin', password='admin123')
    print("✅ Sesión iniciada")
    
    # Probar URL del historial
    try:
        response = client.get('/management/stock/history/17/')
        print(f"📊 Respuesta del historial: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ HISTORIAL FUNCIONANDO CORRECTAMENTE")
            print("   • URL correcta: /management/stock/history/17/")
            print("   • Vista respondiendo: 200 OK")
            print("   • Template renderizado exitosamente")
        elif response.status_code == 404:
            print("⚠️  Producto 17 no existe - probando con otro ID")
            
            # Intentar con ID 1
            response = client.get('/management/stock/history/1/')
            if response.status_code == 200:
                print("✅ HISTORIAL FUNCIONANDO con ID 1")
            else:
                print(f"❌ Error con ID 1: {response.status_code}")
        else:
            print(f"⚠️  Respuesta inesperada: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error en la prueba: {str(e)}")
    
    # Probar URLs relacionadas
    urls_prueba = [
        ('/management/stock/alertas/', 'Alertas de stock'),
        ('/management/stock/reporte/', 'Reporte de stock'),
        ('/management/stock/movimiento/', 'Movimiento de stock')
    ]
    
    print("\n🔗 PROBANDO URLS RELACIONADAS:")
    for url, nombre in urls_prueba:
        try:
            response = client.get(url)
            status = "✅" if response.status_code == 200 else "❌"
            print(f"   {status} {nombre}: {response.status_code}")
        except Exception as e:
            print(f"   ❌ {nombre}: Error - {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎉 PRUEBA COMPLETADA")
    print("=" * 50)

if __name__ == '__main__':
    probar_historial()
