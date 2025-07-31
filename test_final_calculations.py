#!/usr/bin/env python
"""
Test final de validación de cálculos
Simula el proceso completo de creación de orden
"""

import os
import sys
import django
from decimal import Decimal

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dulce_bias_project.settings')
django.setup()

from orders.models import Order, OrderItem
from shop.models import Product
from django.contrib.auth.models import User


def test_order_calculations():
    """Test completo de cálculos de órdenes"""
    print("🧪 Iniciando test de cálculos de órdenes...")
    print("=" * 60)
    
    # Test 1: Verificar orden existente
    print("📋 Test 1: Verificando orden DB-20250731-0006")
    try:
        order = Order.objects.get(order_number='DB-20250731-0006')
        
        # Calcular subtotal
        calculated_subtotal = sum(item.get_total_price() for item in order.items.all())
        stored_subtotal = order.subtotal
        
        # Calcular total
        calculated_total = calculated_subtotal + order.shipping_cost
        stored_total = order.total
        
        print(f"   Subtotal: ${calculated_subtotal:,.0f} == ${stored_subtotal:,.0f} ✅")
        print(f"   Total: ${calculated_total:,.0f} == ${stored_total:,.0f} ✅")
        print(f"   Items: {order.get_total_items()}")
        
        # Verificar formateo
        print(f"   Formato subtotal: {order.formatted_subtotal}")
        print(f"   Formato total: {order.formatted_total}")
        
        assert calculated_subtotal == stored_subtotal, f"Subtotal incorrecto: {calculated_subtotal} != {stored_subtotal}"
        assert calculated_total == stored_total, f"Total incorrecto: {calculated_total} != {stored_total}"
        
        print("   ✅ Test 1 PASADO")
        
    except Order.DoesNotExist:
        print("   ❌ Orden no encontrada")
        return False
    except AssertionError as e:
        print(f"   ❌ Test 1 FALLÓ: {e}")
        return False
    
    # Test 2: Verificar auto-corrección
    print("\n📋 Test 2: Verificando auto-corrección de cálculos")
    try:
        order = Order.objects.get(order_number='DB-20250731-0006')
        
        # Corromper intencionalmente los datos
        original_subtotal = order.subtotal
        original_total = order.total
        
        order.subtotal = Decimal('1000')  # Valor incorrecto
        order.total = Decimal('2000')     # Valor incorrecto
        
        # Guardar debería auto-corregir
        order.save()
        
        # Verificar que se corrigió
        order.refresh_from_db()
        
        assert order.subtotal == original_subtotal, f"Auto-corrección falló en subtotal"
        assert order.total == original_total, f"Auto-corrección falló en total"
        
        print(f"   Subtotal auto-corregido: ${order.subtotal:,.0f} ✅")
        print(f"   Total auto-corregido: ${order.total:,.0f} ✅")
        print("   ✅ Test 2 PASADO")
        
    except Exception as e:
        print(f"   ❌ Test 2 FALLÓ: {e}")
        return False
    
    # Test 3: Verificar todas las órdenes
    print("\n📋 Test 3: Verificando todas las órdenes")
    orders_checked = 0
    errors_found = 0
    
    for order in Order.objects.all():
        orders_checked += 1
        calculated_subtotal = sum(item.get_total_price() for item in order.items.all())
        calculated_total = calculated_subtotal + order.shipping_cost
        
        if calculated_subtotal != order.subtotal or calculated_total != order.total:
            errors_found += 1
            print(f"   ❌ Error en {order.order_number}")
        
    print(f"   Órdenes verificadas: {orders_checked}")
    print(f"   Errores encontrados: {errors_found}")
    
    if errors_found == 0:
        print("   ✅ Test 3 PASADO")
    else:
        print("   ❌ Test 3 FALLÓ")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 TODOS LOS TESTS PASARON EXITOSAMENTE")
    print("✅ Los cálculos de órdenes están funcionando correctamente")
    print("✅ La auto-corrección está funcionando")
    print("✅ Todas las órdenes tienen cálculos válidos")
    
    return True


if __name__ == "__main__":
    success = test_order_calculations()
    if not success:
        sys.exit(1)
    else:
        print("\n🚀 Sistema de órdenes validado y funcionando correctamente")
