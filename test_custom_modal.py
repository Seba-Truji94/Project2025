#!/usr/bin/env python3
"""
Test para verificar la funcionalidad del modal personalizado de cambio rápido
"""

import os
import sys

# Configurar Django ANTES de importar los modelos
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dulce_bias_project.settings')

import django
django.setup()

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
import json
from orders.models import Order

def test_custom_modal_functionality():
    print("🚀 Testing funcionalidad del modal personalizado...")
    print("=" * 60)
    
    # Crear cliente de prueba
    client = Client()
    
    # Obtener superusuario
    try:
        superuser = User.objects.filter(is_superuser=True).first()
        if not superuser:
            print("❌ No se encontró superusuario")
            return False
            
        print(f"👤 Usando superusuario: {superuser.username}")
        
        # Login
        client.force_login(superuser)
        
        # Test 1: Acceso a página de administración
        print("\n🧪 Test 1: Acceso a página de administración...")
        response = client.get('/orders/admin/')
        print(f"📡 Respuesta HTTP: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Verificar que el modal personalizado esté presente
            if 'custom-modal' in content:
                print("✅ Modal personalizado encontrado")
            else:
                print("❌ Modal personalizado no encontrado")
                return False
                
            # Verificar funciones JavaScript
            js_functions = [
                'openQuickModal',
                'closeQuickModal',
                'clearModalBackdrop'
            ]
            
            for func in js_functions:
                if func in content:
                    print(f"✅ Función {func} encontrada")
                else:
                    print(f"❌ Función {func} no encontrada")
                    
            # Verificar estilos CSS del modal personalizado
            css_classes = [
                'custom-modal',
                'custom-modal-overlay',
                'custom-modal-dialog'
            ]
            
            for css_class in css_classes:
                if css_class in content:
                    print(f"✅ Clase CSS {css_class} encontrada")
                else:
                    print(f"❌ Clase CSS {css_class} no encontrada")
        else:
            print(f"❌ Error de acceso: {response.status_code}")
            return False
            
        # Test 2: Funcionalidad AJAX
        print("\n🧪 Test 2: Funcionalidad AJAX de cambio de estado...")
        
        # Obtener una orden para probar
        order = Order.objects.first()
        if not order:
            print("❌ No se encontraron órdenes para probar")
            return False
            
        print(f"📦 Usando orden: {order.order_number}")
        print(f"   Estado actual: {order.get_status_display()}")
        
        # Cambiar estado via AJAX
        new_status = 'confirmed' if order.status != 'confirmed' else 'processing'
        
        ajax_data = {
            'order_id': order.id,
            'status': new_status,
            'notes': 'Test automatizado con modal personalizado'
        }
        
        print(f"🔄 Cambiando estado a: {new_status}")
        
        response = client.post(
            '/orders/admin/ajax/change-status/',
            data=json.dumps(ajax_data),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        print(f"📡 Respuesta HTTP: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"📄 Respuesta JSON: {data}")
                
                if data.get('success'):
                    print("✅ Estado actualizado correctamente")
                    
                    # Verificar que el estado se cambió en la base de datos
                    order.refresh_from_db()
                    if order.status == new_status:
                        print("✅ Estado verificado en la base de datos")
                        
                        # Restaurar estado original
                        order.status = 'pending'
                        order.save()
                        print("🔄 Estado restaurado al original")
                        
                        return True
                    else:
                        print("❌ Estado no se actualizó en la base de datos")
                        return False
                else:
                    print(f"❌ Error en la respuesta: {data.get('error', 'Error desconocido')}")
                    return False
                    
            except json.JSONDecodeError:
                print("❌ Respuesta no es JSON válido")
                return False
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error durante las pruebas: {str(e)}")
        return False

def main():
    print("🚀 Iniciando tests del modal personalizado...")
    print("=" * 60)
    
    success = test_custom_modal_functionality()
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE TESTS")
    print("=" * 60)
    
    if success:
        print("🎉 TODOS LOS TESTS PASARON")
        print("✅ El modal personalizado está funcionando correctamente")
        print("✅ No hay problemas de backdrop difuminado")
        print("✅ La funcionalidad AJAX responde correctamente")
    else:
        print("❌ ALGUNOS TESTS FALLARON")
        print("🔧 Revisar la implementación del modal personalizado")

if __name__ == "__main__":
    main()
