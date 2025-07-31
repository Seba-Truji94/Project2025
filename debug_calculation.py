#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dulce_bias_project.settings')
django.setup()

from django.contrib.auth.models import User
from cart.models import Cart, CartItem
from shop.models import Product

def debug_cart_calculation():
    print("🔍 DEBUGGING CÁLCULO DE CARRITO")
    print("=" * 50)
    
    for cart in Cart.objects.all():
        print(f"\n🛒 Usuario: {cart.user.username}")
        
        # Método 1: Usando la propiedad total_items
        method1 = cart.total_items
        print(f"  Método 1 (propiedad): {method1}")
        
        # Método 2: Calculando manualmente
        manual_calc = sum(item.quantity for item in cart.items.all())
        print(f"  Método 2 (manual): {manual_calc}")
        
        # Método 3: Usando agregación SQL
        from django.db.models import Sum
        sql_calc = cart.items.aggregate(total=Sum('quantity'))['total'] or 0
        print(f"  Método 3 (SQL): {sql_calc}")
        
        # Verificar items individuales
        print("  📦 Items detallados:")
        for item in cart.items.all():
            print(f"    - ID: {item.id}, Producto: {item.product.name}, Cantidad: {item.quantity}")
        
        # Verificar si hay duplicados
        duplicates = cart.items.values('product').annotate(count=Cart.objects.count()).filter(count__gt=1)
        if duplicates:
            print(f"  ⚠️  Productos duplicados encontrados: {duplicates}")
        
        if method1 != manual_calc or manual_calc != sql_calc:
            print(f"  🚨 INCONSISTENCIA DETECTADA!")
        else:
            print(f"  ✅ Cálculos consistentes")

if __name__ == "__main__":
    debug_cart_calculation()
