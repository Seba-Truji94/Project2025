#!/usr/bin/env python
"""
Script para validar los cálculos de las órdenes
Verifica que los totales sean matemáticamente correctos
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


def validate_order_calculations():
    """Valida todos los cálculos de las órdenes"""
    print("🔍 Iniciando validación de cálculos de órdenes...")
    print("=" * 60)
    
    orders = Order.objects.all().prefetch_related('items')
    errors_found = []
    orders_checked = 0
    
    for order in orders:
        orders_checked += 1
        print(f"\n📦 Validando pedido: {order.order_number}")
        print(f"   Estado: {order.get_status_display()}")
        print(f"   Usuario: {order.user.username}")
        
        # 1. Validar suma de items = subtotal
        calculated_subtotal = sum(item.get_total_price() for item in order.items.all())
        stored_subtotal = order.subtotal
        
        print(f"   💰 Subtotal calculado: ${calculated_subtotal:,.0f}")
        print(f"   💰 Subtotal almacenado: ${stored_subtotal:,.0f}")
        
        if calculated_subtotal != stored_subtotal:
            error = f"❌ ERROR en {order.order_number}: Subtotal calculado (${calculated_subtotal:,.0f}) != Subtotal almacenado (${stored_subtotal:,.0f})"
            errors_found.append(error)
            print(f"   {error}")
        else:
            print("   ✅ Subtotal correcto")
        
        # 2. Validar subtotal + shipping = total
        calculated_total = stored_subtotal + order.shipping_cost
        stored_total = order.total
        
        print(f"   🚚 Costo de envío: ${order.shipping_cost:,.0f}")
        print(f"   🧮 Total calculado: ${calculated_total:,.0f}")
        print(f"   🧮 Total almacenado: ${stored_total:,.0f}")
        
        if calculated_total != stored_total:
            error = f"❌ ERROR en {order.order_number}: Total calculado (${calculated_total:,.0f}) != Total almacenado (${stored_total:,.0f})"
            errors_found.append(error)
            print(f"   {error}")
        else:
            print("   ✅ Total correcto")
        
        # 3. Validar items individuales
        print("   📋 Items del pedido:")
        total_items = 0
        for item in order.items.all():
            item_total = item.get_total_price()
            expected_total = item.price * item.quantity
            total_items += item.quantity
            
            print(f"      • {item.product.name}: {item.quantity} x ${item.price:,.0f} = ${item_total:,.0f}")
            
            if item_total != expected_total:
                error = f"❌ ERROR en item {item.id}: Total calculado (${item_total:,.0f}) != Esperado (${expected_total:,.0f})"
                errors_found.append(error)
                print(f"        {error}")
        
        # 4. Validar get_total_items()
        calculated_items = order.get_total_items()
        print(f"   📦 Total items calculado: {calculated_items}")
        print(f"   📦 Total items contado: {total_items}")
        
        if calculated_items != total_items:
            error = f"❌ ERROR en {order.order_number}: Total items calculado ({calculated_items}) != Contado ({total_items})"
            errors_found.append(error)
            print(f"   {error}")
        else:
            print("   ✅ Cantidad de items correcta")
        
        # 5. Validar métodos de formateo
        try:
            formatted_subtotal = order.formatted_subtotal
            formatted_shipping = order.formatted_shipping_cost
            formatted_total = order.formatted_total
            print(f"   🎨 Formato subtotal: {formatted_subtotal}")
            print(f"   🎨 Formato envío: {formatted_shipping}")
            print(f"   🎨 Formato total: {formatted_total}")
            print("   ✅ Formateo correcto")
        except Exception as e:
            error = f"❌ ERROR en formateo de {order.order_number}: {str(e)}"
            errors_found.append(error)
            print(f"   {error}")
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE VALIDACIÓN")
    print("=" * 60)
    print(f"Órdenes revisadas: {orders_checked}")
    print(f"Errores encontrados: {len(errors_found)}")
    
    if errors_found:
        print("\n❌ ERRORES DETECTADOS:")
        for error in errors_found:
            print(f"  {error}")
        return False
    else:
        print("\n✅ TODAS LAS VALIDACIONES PASARON CORRECTAMENTE")
        print("   Los cálculos matemáticos están correctos")
        return True


def validate_specific_order(order_number):
    """Valida un pedido específico en detalle"""
    try:
        order = Order.objects.get(order_number=order_number)
        print(f"🔍 Validación detallada del pedido: {order_number}")
        print("=" * 50)
        
        # Información básica
        print(f"Usuario: {order.user.username} ({order.full_name})")
        print(f"Estado: {order.get_status_display()}")
        print(f"Pago: {order.get_payment_status_display()}")
        print(f"Método: {order.get_payment_method_display()}")
        print(f"Fecha: {order.created_at}")
        
        # Detalles financieros
        print(f"\n💰 DETALLES FINANCIEROS:")
        items = order.items.all()
        subtotal_calculado = Decimal('0')
        
        for i, item in enumerate(items, 1):
            item_total = item.get_total_price()
            subtotal_calculado += item_total
            print(f"  {i}. {item.product.name}")
            print(f"     Precio unitario: ${item.price:,.0f}")
            print(f"     Cantidad: {item.quantity}")
            print(f"     Total item: ${item_total:,.0f}")
        
        print(f"\n📊 RESUMEN:")
        print(f"  Subtotal calculado: ${subtotal_calculado:,.0f}")
        print(f"  Subtotal almacenado: ${order.subtotal:,.0f}")
        print(f"  Costo de envío: ${order.shipping_cost:,.0f}")
        print(f"  Total calculado: ${subtotal_calculado + order.shipping_cost:,.0f}")
        print(f"  Total almacenado: ${order.total:,.0f}")
        
        # Validaciones
        print(f"\n✓ VALIDACIONES:")
        if subtotal_calculado == order.subtotal:
            print("  ✅ Subtotal correcto")
        else:
            print(f"  ❌ Subtotal incorrecto: diferencia de ${abs(subtotal_calculado - order.subtotal):,.0f}")
        
        if (subtotal_calculado + order.shipping_cost) == order.total:
            print("  ✅ Total correcto")
        else:
            diff = abs((subtotal_calculado + order.shipping_cost) - order.total)
            print(f"  ❌ Total incorrecto: diferencia de ${diff:,.0f}")
        
        print(f"  ✅ Total items: {order.get_total_items()}")
        
    except Order.DoesNotExist:
        print(f"❌ No se encontró el pedido: {order_number}")
        return False
    
    return True


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Validar pedido específico
        order_number = sys.argv[1]
        validate_specific_order(order_number)
    else:
        # Validar todas las órdenes
        validate_order_calculations()
