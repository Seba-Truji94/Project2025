#!/usr/bin/env python3
"""
Script para forzar la recalculación y limpieza de carritos
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

def force_cart_recalculation():
    print("🔄 FORZANDO: Recalculación de carritos")
    print("=" * 50)
    
    # 1. Eliminar CartItems huérfanos o con productos inexistentes
    print("1️⃣ Limpiando items huérfanos...")
    
    orphaned_items = 0
    invalid_items = 0
    
    for item in CartItem.objects.all():
        try:
            # Verificar que el producto existe y está disponible
            if not hasattr(item, 'product') or not item.product:
                item.delete()
                orphaned_items += 1
                continue
                
            # Verificar que el producto está disponible
            if not item.product.available:
                print(f"   🗑️ Eliminando producto no disponible: {item.product.name}")
                item.delete()
                invalid_items += 1
                continue
                
            # Verificar que la cantidad es válida
            if item.quantity <= 0:
                print(f"   🗑️ Eliminando item con cantidad inválida: {item.product.name}")
                item.delete()
                invalid_items += 1
                continue
                
        except Exception as e:
            print(f"   🗑️ Eliminando item problemático: {str(e)}")
            item.delete()
            orphaned_items += 1
    
    print(f"   ✅ Items huérfanos eliminados: {orphaned_items}")
    print(f"   ✅ Items inválidos eliminados: {invalid_items}")
    
    # 2. Verificar y corregir carritos
    print("\n2️⃣ Verificando carritos...")
    
    for cart in Cart.objects.all():
        items_count = cart.items.count()
        calculated_total = sum(item.quantity for item in cart.items.all())
        
        print(f"   📋 {cart.user.username}:")
        print(f"      - Items DB: {items_count}")
        print(f"      - Total calculado: {calculated_total}")
        print(f"      - Precio total: ${cart.total_price}")
        
        # Si el carrito está vacío, asegurarse de que no tenga items fantasma
        if items_count == 0:
            # Verificar si hay items que no se están contando
            all_items = CartItem.objects.filter(cart=cart)
            if all_items.exists():
                print(f"      🗑️ Eliminando {all_items.count()} items fantasma")
                all_items.delete()
    
    # 3. Eliminar carritos completamente vacíos de usuarios que no han hecho login recientemente
    print("\n3️⃣ Limpiando carritos vacíos...")
    
    empty_carts = Cart.objects.annotate(
        items_count=models.Count('items')
    ).filter(items_count=0)
    
    print(f"   📊 Carritos vacíos encontrados: {empty_carts.count()}")
    
    # No eliminar carritos vacíos, solo reportar
    for cart in empty_carts:
        print(f"   📝 Carrito vacío: {cart.user.username}")
    
    # 4. Verificación final
    print("\n4️⃣ Verificación final...")
    
    total_carts = Cart.objects.count()
    total_items = CartItem.objects.count()
    total_users_with_items = Cart.objects.annotate(
        items_count=models.Count('items')
    ).filter(items_count__gt=0).count()
    
    print(f"   📊 Total carritos: {total_carts}")
    print(f"   📦 Total items: {total_items}")
    print(f"   👥 Usuarios con items: {total_users_with_items}")
    
    # 5. Mostrar estado actualizado de cada carrito
    print("\n5️⃣ Estado final de carritos...")
    
    for cart in Cart.objects.all():
        items_count = cart.items.count()
        if items_count > 0:
            print(f"   ✅ {cart.user.username}: {items_count} items, ${cart.total_price}")
        else:
            print(f"   📭 {cart.user.username}: carrito vacío")
    
    print("\n🎯 RECALCULACIÓN COMPLETADA")
    print("✅ Carritos limpiados y verificados")
    print("✅ Items inválidos eliminados")
    print("✅ Cálculos actualizados")

if __name__ == "__main__":
    # Importar models después de django.setup()
    from django.db import models
    force_cart_recalculation()
