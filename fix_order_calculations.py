#!/usr/bin/env python
"""
Script para corregir los cálculos incorrectos de las órdenes
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


def fix_order_calculations():
    """Corrige los cálculos incorrectos de las órdenes"""
    print("🔧 Iniciando corrección de cálculos de órdenes...")
    print("=" * 60)
    
    orders = Order.objects.all().prefetch_related('items')
    orders_fixed = 0
    
    for order in orders:
        print(f"\n📦 Revisando pedido: {order.order_number}")
        
        # Calcular subtotal correcto
        calculated_subtotal = sum(item.get_total_price() for item in order.items.all())
        stored_subtotal = order.subtotal
        
        print(f"   💰 Subtotal calculado: ${calculated_subtotal:,.0f}")
        print(f"   💰 Subtotal almacenado: ${stored_subtotal:,.0f}")
        
        if calculated_subtotal != stored_subtotal:
            # Corregir subtotal
            order.subtotal = calculated_subtotal
            print(f"   🔧 Corrigiendo subtotal de ${stored_subtotal:,.0f} a ${calculated_subtotal:,.0f}")
            
            # Recalcular total
            new_total = calculated_subtotal + order.shipping_cost
            old_total = order.total
            order.total = new_total
            print(f"   🔧 Corrigiendo total de ${old_total:,.0f} a ${new_total:,.0f}")
            
            # Guardar cambios
            order.save()
            orders_fixed += 1
            print("   ✅ Orden corregida y guardada")
        else:
            print("   ✅ Orden ya tiene cálculos correctos")
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE CORRECCIÓN")
    print("=" * 60)
    print(f"Órdenes revisadas: {orders.count()}")
    print(f"Órdenes corregidas: {orders_fixed}")
    
    if orders_fixed > 0:
        print(f"\n✅ {orders_fixed} órdenes fueron corregidas exitosamente")
    else:
        print("\n✅ Todas las órdenes ya tenían cálculos correctos")


def show_order_details(order_number):
    """Muestra los detalles de una orden específica"""
    try:
        order = Order.objects.get(order_number=order_number)
        print(f"📦 Detalles del pedido: {order_number}")
        print("=" * 50)
        
        print(f"Usuario: {order.user.username} ({order.full_name})")
        print(f"Estado: {order.get_status_display()}")
        print(f"Fecha: {order.created_at}")
        
        print(f"\n📋 Items:")
        total_calculated = Decimal('0')
        for item in order.items.all():
            item_total = item.get_total_price()
            total_calculated += item_total
            print(f"  • {item.product.name}")
            print(f"    Precio: ${item.price:,.0f} x {item.quantity} = ${item_total:,.0f}")
        
        print(f"\n💰 Cálculos:")
        print(f"  Subtotal calculado: ${total_calculated:,.0f}")
        print(f"  Subtotal almacenado: ${order.subtotal:,.0f}")
        print(f"  Envío: ${order.shipping_cost:,.0f}")
        print(f"  Total calculado: ${total_calculated + order.shipping_cost:,.0f}")
        print(f"  Total almacenado: ${order.total:,.0f}")
        
        print(f"\n🎨 Formato:")
        print(f"  Subtotal: {order.formatted_subtotal}")
        print(f"  Envío: {order.formatted_shipping_cost}")
        print(f"  Total: {order.formatted_total}")
        
    except Order.DoesNotExist:
        print(f"❌ No se encontró el pedido: {order_number}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "fix":
            fix_order_calculations()
        else:
            # Mostrar detalles de un pedido específico
            order_number = sys.argv[1]
            show_order_details(order_number)
    else:
        print("Uso:")
        print("  python fix_order_calculations.py fix          # Corregir todas las órdenes")
        print("  python fix_order_calculations.py DB-XXXXXXX  # Ver detalles de una orden")
