#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dulce_bias_project.settings')
django.setup()

from django.contrib.auth.models import User
from cart.models import Cart, CartItem
from shop.models import Product

def debug_simple():
    print("🔍 DEBUGGING SIMPLE DEL CARRITO")
    print("=" * 40)
    
    # Verificar cada carrito
    for cart in Cart.objects.all():
        print(f"\n🛒 Usuario: {cart.user.username}")
        
        # Listar todos los items
        items = cart.items.all()
        print(f"  📊 Cantidad de items: {items.count()}")
        
        total_quantity = 0
        for item in items:
            print(f"    - {item.product.name}: {item.quantity} unidades")
            total_quantity += item.quantity
        
        print(f"  🧮 Total manual: {total_quantity}")
        print(f"  🏷️  Total propiedad: {cart.total_items}")
        
        if total_quantity != cart.total_items:
            print("  🚨 PROBLEMA DETECTADO!")
        else:
            print("  ✅ Todo correcto")

if __name__ == "__main__":
    debug_simple()
