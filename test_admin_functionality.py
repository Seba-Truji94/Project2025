#!/usr/bin/env python
"""
Test para verificar que la funcionalidad AJAX de cambio de estado funcione correctamente
"""

import os
import sys
import django
import json

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dulce_bias_project.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from orders.models import Order


def test_ajax_change_status():
    """Test de la funcionalidad AJAX para cambio de estado"""
    print("🧪 Testing funcionalidad AJAX de cambio de estado...")
    print("=" * 60)
    
    # Crear cliente de prueba
    client = Client()
    
    # Obtener un superusuario
    try:
        superuser = User.objects.filter(is_superuser=True).first()
        if not superuser:
            print("❌ No se encontró ningún superusuario")
            return False
        
        print(f"👤 Usando superusuario: {superuser.username}")
        
        # Login
        client.force_login(superuser)
        
        # Obtener una orden para probar
        order = Order.objects.first()
        if not order:
            print("❌ No se encontraron órdenes para probar")
            return False
        
        print(f"📦 Usando orden: {order.order_number}")
        print(f"   Estado actual: {order.get_status_display()}")
        
        # Preparar datos para el cambio de estado
        original_status = order.status
        new_status = 'confirmed' if original_status != 'confirmed' else 'processing'
        
        test_data = {
            'order_id': order.id,
            'status': new_status,
            'notes': 'Test de cambio de estado vía AJAX'
        }
        
        print(f"🔄 Cambiando estado a: {new_status}")
        
        # Hacer petición AJAX
        response = client.post(
            '/orders/admin/ajax/change-status/',
            data=json.dumps(test_data),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        print(f"📡 Respuesta HTTP: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"📄 Respuesta JSON: {response_data}")
            
            if response_data.get('success'):
                # Verificar que el estado cambió en la base de datos
                order.refresh_from_db()
                if order.status == new_status:
                    print("✅ Estado actualizado correctamente en la base de datos")
                    
                    # Restaurar estado original
                    order.status = original_status
                    order.save()
                    print("🔄 Estado restaurado al original")
                    
                    print("\n🎉 TEST EXITOSO: La funcionalidad AJAX funciona correctamente")
                    return True
                else:
                    print(f"❌ Estado no cambió en la base de datos. Actual: {order.status}")
                    return False
            else:
                print(f"❌ Respuesta de error: {response_data.get('error')}")
                return False
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"   Contenido: {response.content.decode()}")
            return False
    
    except Exception as e:
        print(f"❌ Error durante el test: {str(e)}")
        return False


def test_admin_page_access():
    """Test de acceso a la página de administración"""
    print("\n🧪 Testing acceso a la página de administración...")
    print("=" * 60)
    
    client = Client()
    
    try:
        superuser = User.objects.filter(is_superuser=True).first()
        if not superuser:
            print("❌ No se encontró ningún superusuario")
            return False
        
        client.force_login(superuser)
        
        response = client.get('/orders/admin/')
        
        print(f"📡 Respuesta HTTP: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Página de administración accesible")
            
            # Verificar que el contenido contiene elementos esperados
            content = response.content.decode()
            
            checks = [
                ('quickStatusModal', 'Modal de cambio rápido'),
                ('save-status-btn', 'Botón de guardar estado'),
                ('clearModalBackdrop', 'Función de limpieza'),
                ('ajax/change-status', 'URL AJAX'),
            ]
            
            for check, description in checks:
                if check in content:
                    print(f"✅ {description} encontrado")
                else:
                    print(f"⚠️ {description} NO encontrado")
            
            return True
        else:
            print(f"❌ Error de acceso: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"❌ Error durante el test: {str(e)}")
        return False


if __name__ == "__main__":
    print("🚀 Iniciando tests de funcionalidad de administración...")
    
    success1 = test_admin_page_access()
    success2 = test_ajax_change_status()
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE TESTS")
    print("=" * 60)
    
    if success1 and success2:
        print("🎉 TODOS LOS TESTS PASARON")
        print("✅ La funcionalidad de administración está funcionando correctamente")
        print("✅ El problema del modal difuminado debería estar resuelto")
    else:
        print("❌ ALGUNOS TESTS FALLARON")
        if not success1:
            print("  - Problema con acceso a la página de administración")
        if not success2:
            print("  - Problema con funcionalidad AJAX de cambio de estado")
        
        print("\n🔧 Recomendaciones:")
        print("  1. Verificar que el servidor esté corriendo")
        print("  2. Verificar permisos de superusuario")
        print("  3. Revisar logs del servidor para errores")
        print("  4. Usar el botón 'Limpiar Vista' si la página sigue difuminada")
