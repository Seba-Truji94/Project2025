#!/usr/bin/env python3
"""
Debug específico de las cantidades de CartItems
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dulce_bias_project.settings')
django.setup()

from django.contrib.auth.models import User
from cart.models import Cart, CartItem
from shop.models import Product

def debug_cart_quantities():
    print("🔍 DEBUG: Cantidades específicas de CartItems")
    print("=" * 60)
    
    # Investigar cada CartItem individualmente
    all_items = CartItem.objects.all().order_by('cart__user__username')
    
    for item in all_items:
        print(f"\n📦 CartItem ID: {item.id}")
        print(f"   👤 Usuario: {item.cart.user.username}")
        print(f"   🛍️  Producto: {item.product.name} (ID: {item.product.id})")
        print(f"   📊 Cantidad: {item.quantity}")
        print(f"   💰 Precio unitario: ${item.product.current_price}")
        print(f"   💵 Total item: ${item.get_total_price()}")
        print(f"   📅 Agregado: {item.added_at}")
        
        # Verificar si la cantidad es razonable
        if item.quantity > 50:
            print(f"   ⚠️  CANTIDAD SOSPECHOSA: {item.quantity} es muy alta")
        elif item.quantity < 1:
            print(f"   ⚠️  CANTIDAD INVÁLIDA: {item.quantity} debe ser mayor a 0")
        else:
            print(f"   ✅ Cantidad normal")
    
    print(f"\n🧮 RESUMEN POR CARRITO:")
    print("=" * 60)
    
    for cart in Cart.objects.all():
        if cart.items.exists():
            print(f"\n👤 {cart.user.username}:")
            total_quantity = 0
            total_price = 0
            
            for item in cart.items.all():
                print(f"   - {item.product.name}: {item.quantity} unidades")
                total_quantity += item.quantity
                total_price += item.get_total_price()
            
            print(f"   📊 Total manual: {total_quantity} unidades")
            print(f"   💰 Total manual: ${total_price}")
            print(f"   🔄 Total calculado: {cart.total_items} unidades")
            print(f"   💵 Total calculado: ${cart.total_price}")
            
            if total_quantity != cart.total_items:
                print(f"   ❌ INCONSISTENCIA EN CANTIDAD!")
            if abs(total_price - cart.total_price) > 1:
                print(f"   ❌ INCONSISTENCIA EN PRECIO!")

def fix_cart_quantities():
    print(f"\n🔧 REPARANDO: Cantidades incorrectas")
    print("=" * 60)
    
    fixed_items = 0
    
    for item in CartItem.objects.all():
        original_quantity = item.quantity
        
        # Si la cantidad es mayor a 100, es probablemente un error
        if item.quantity > 100:
            # Reducir a un valor razonable
            item.quantity = min(10, item.quantity // 10)
            item.save()
            fixed_items += 1
            print(f"   🔧 {item.cart.user.username} - {item.product.name}: {original_quantity} → {item.quantity}")
        
        # Si la cantidad es 0 o negativa, eliminar el item
        elif item.quantity <= 0:
            print(f"   🗑️ Eliminando item con cantidad {original_quantity}: {item.product.name}")
            item.delete()
            fixed_items += 1
    
    print(f"\n✅ Items reparados: {fixed_items}")
    
    # Verificación post-reparación
    print(f"\n🔍 VERIFICACIÓN POST-REPARACIÓN:")
    print("=" * 60)
    
    for cart in Cart.objects.all():
        if cart.items.exists():
            db_count = cart.items.count()
            total_quantity = cart.total_items
            print(f"   👤 {cart.user.username}: {db_count} items, {total_quantity} unidades totales")

if __name__ == "__main__":
    debug_cart_quantities()
    fix_cart_quantities()
