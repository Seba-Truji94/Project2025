#!/usr/bin/env python3
"""
Debug script para verificar el estado del botón del carrito
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

def debug_cart_button():
    print("🔍 DEBUG: Estado del botón del carrito")
    print("=" * 50)
    
    # Verificar usuarios con carritos
    users_with_carts = User.objects.filter(cart__isnull=False).distinct()
    print(f"👥 Usuarios con carritos: {users_with_carts.count()}")
    
    for user in users_with_carts[:5]:  # Mostrar solo los primeros 5
        cart = Cart.objects.filter(user=user).first()
        if cart:
            print(f"  📋 {user.username}: {cart.total_items} items, ${cart.total_price}")
    
    # Verificar productos en carritos
    all_cart_items = CartItem.objects.all()
    print(f"\n📦 Total de items en todos los carritos: {all_cart_items.count()}")
    
    # Verificar productos disponibles
    available_products = Product.objects.filter(available=True)
    print(f"🛍️  Productos disponibles: {available_products.count()}")
    
    # Verificar si hay productos en carritos que no están disponibles
    unavailable_in_cart = CartItem.objects.filter(product__available=False)
    print(f"⚠️  Items en carrito con productos no disponibles: {unavailable_in_cart.count()}")
    
    if unavailable_in_cart.exists():
        print("📋 Productos problemáticos:")
        for item in unavailable_in_cart[:10]:
            print(f"  - {item.product.name} (ID: {item.product.id}) - Usuario: {item.cart.user.username}")
    
    # Verificar estructura de templates
    template_files = [
        "templates/base.html",
        "static/js/script.js",
        "static/js/cart-diagnostics.js",
        "static/css/styles.css"
    ]
    
    print(f"\n📁 Verificando archivos del carrito:")
    for file_path in template_files:
        full_path = os.path.join(os.getcwd(), file_path)
        exists = os.path.exists(full_path)
        print(f"  {'✅' if exists else '❌'} {file_path}")
    
    print("\n🔧 RECOMENDACIONES:")
    print("1. Verificar que el JavaScript esté cargándose correctamente")
    print("2. Revisar la consola del navegador en busca de errores")
    print("3. Verificar que el modal del carrito esté presente en el DOM")
    print("4. Comprobar que los event listeners se estén registrando")

if __name__ == "__main__":
    debug_cart_button()
