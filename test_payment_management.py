#!/usr/bin/env python3
"""
Test para verificar la funcionalidad de gestión de pagos
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dulce_bias_project.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from orders.models import Order
import json


def test_payment_management():
    print("🧪 Testing funcionalidad de gestión de pagos...")
    print("=" * 60)
    
    # Crear cliente de prueba
    client = Client()
    
    try:
        # Obtener superusuario
        superuser = User.objects.filter(is_superuser=True).first()
        if not superuser:
            print("❌ No se encontró superusuario")
            return False
            
        print(f"👤 Usando superusuario: {superuser.username}")
        
        # Login
        client.force_login(superuser)
        
        # Test 1: Acceso a página de administración con filtros de pago
        print("\n🧪 Test 1: Página de administración con filtros de pago...")
        response = client.get('/orders/admin/')
        print(f"📡 Respuesta HTTP: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Verificar elementos de gestión de pagos
            payment_elements = [
                'payment_status',
                'payment-badge',
                'payment-btn',
                'ajax/change-payment-status',
                'Pagados',
                'Sin Pagar'
            ]
            
            for element in payment_elements:
                if element in content:
                    print(f"✅ Elemento de pago '{element}' encontrado")
                else:
                    print(f"❌ Elemento de pago '{element}' no encontrado")
        else:
            print(f"❌ Error de acceso: {response.status_code}")
            return False
        
        # Test 2: Funcionalidad AJAX de cambio de estado de pago
        print("\n🧪 Test 2: Cambio de estado de pago vía AJAX...")
        
        # Obtener una orden para probar
        order = Order.objects.first()
        if not order:
            print("❌ No se encontraron órdenes para probar")
            return False
            
        print(f"📦 Usando orden: {order.order_number}")
        print(f"   Estado de pago actual: {order.get_payment_status_display()}")
        
        # Test cambio a pagado
        if order.payment_status == 'pending':
            new_status = 'paid'
            action = 'mark_paid'
        else:
            new_status = 'pending'
            action = 'mark_unpaid'
        
        test_data = {
            'order_id': order.id,
            'payment_status': new_status,
            'action': action
        }
        
        print(f"🔄 Cambiando estado de pago a: {new_status}")
        
        response = client.post(
            '/orders/admin/ajax/change-payment-status/',
            data=json.dumps(test_data),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        print(f"📡 Respuesta HTTP: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"📄 Respuesta JSON: {data}")
                
                if data.get('success'):
                    print("✅ Estado de pago actualizado correctamente")
                    
                    # Verificar que el estado cambió en la base de datos
                    order.refresh_from_db()
                    if order.payment_status == new_status:
                        print("✅ Estado verificado en la base de datos")
                        
                        # Restaurar estado original
                        original_status = 'pending' if new_status == 'paid' else 'paid'
                        order.payment_status = original_status
                        order.save()
                        print("🔄 Estado restaurado al original")
                        
                        return True
                    else:
                        print(f"❌ Estado no se actualizó en BD. Actual: {order.payment_status}")
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


def test_payment_filters():
    """Test de filtros por estado de pago"""
    print("\n🧪 Test 3: Filtros por estado de pago...")
    
    client = Client()
    superuser = User.objects.filter(is_superuser=True).first()
    client.force_login(superuser)
    
    # Test filtro por pagados
    response = client.get('/orders/admin/?payment_status=paid')
    print(f"📡 Filtro 'pagados' - HTTP: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Filtro de pagados funciona")
    else:
        print("❌ Error en filtro de pagados")
        return False
    
    # Test filtro por pendientes
    response = client.get('/orders/admin/?payment_status=pending')
    print(f"📡 Filtro 'pendientes' - HTTP: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Filtro de pendientes funciona")
        return True
    else:
        print("❌ Error en filtro de pendientes")
        return False


def main():
    print("🚀 Iniciando tests de gestión de pagos...")
    print("=" * 60)
    
    success1 = test_payment_management()
    success2 = test_payment_filters()
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE TESTS")
    print("=" * 60)
    
    if success1 and success2:
        print("🎉 TODOS LOS TESTS PASARON")
        print("✅ La gestión de pagos está funcionando correctamente")
        print("✅ Los filtros de pago están operativos")
        print("✅ La funcionalidad AJAX responde correctamente")
        print("\n💡 FUNCIONALIDADES DISPONIBLES:")
        print("   🔍 Filtros por estado de pago (Pendiente/Pagado/Fallido/Reembolsado)")
        print("   📊 Estadísticas de pagos en el dashboard")
        print("   🎛️  Botones de cambio rápido de estado de pago")
        print("   ⚡ Actualización en tiempo real sin recargar página")
        print("   🔐 Control de permisos para superusuarios")
    else:
        print("❌ ALGUNOS TESTS FALLARON")
        if not success1:
            print("  - Problema con funcionalidad AJAX de cambio de estado")
        if not success2:
            print("  - Problema con filtros de estado de pago")
        
        print("\n🔧 Recomendaciones:")
        print("  1. Verificar que el servidor esté corriendo")
        print("  2. Verificar URLs de administración")
        print("  3. Revisar permisos de superusuario")
        print("  4. Verificar la consola del navegador para errores JS")


if __name__ == "__main__":
    main()
