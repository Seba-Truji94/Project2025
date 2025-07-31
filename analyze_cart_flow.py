#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dulce_bias_project.settings')
django.setup()

from django.contrib.auth.models import User
from cart.models import Cart, CartItem, SessionCart
from shop.models import Product

def analyze_cart_data_flow():
    print("🔍 ANÁLISIS DEL FLUJO DE DATOS DEL CARRITO")
    print("=" * 60)
    
    # Analizar usuario autenticado
    user = User.objects.filter(username='SebastianSEIS').first()
    if user:
        print(f"\n👤 USUARIO AUTENTICADO: {user.username}")
        print("-" * 40)
        
        cart = Cart.objects.get(user=user)
        print(f"🏷️  Cart ID: {cart.id}")
        print(f"📅 Creado: {cart.created_at}")
        
        print(f"\n📊 CÁLCULO DE CANTIDAD:")
        total_manual = 0
        for item in cart.items.all():
            print(f"  - {item.product.name}")
            print(f"    💾 quantity (BD): {item.quantity}")
            print(f"    💰 price (producto): ${item.product.current_price:,}")
            print(f"    🧮 subtotal: ${item.get_total_price():,}")
            total_manual += item.quantity
        
        print(f"\n🔢 TOTALES:")
        print(f"  📊 cart.total_items (propiedad): {cart.total_items}")
        print(f"  🧮 Suma manual: {total_manual}")
        print(f"  💰 cart.total_price: ${cart.total_price:,}")
        print(f"  🏷️  cart.formatted_total_price: {cart.formatted_total_price}")
        
        print(f"\n🔗 ORIGEN DE LOS DATOS:")
        print(f"  📍 Cantidad: sum(item.quantity for item in cart.items.all())")
        print(f"  📍 Precio: sum(item.product.current_price * item.quantity)")
        print(f"  📍 Tabla: CartItem → Product.current_price")
        
    # Analizar carrito de sesión de ejemplo
    print(f"\n" + "=" * 60)
    print(f"👻 CARRITO DE SESIÓN (SIMULADO)")
    print("-" * 40)
    
    from django.test import RequestFactory
    from django.contrib.sessions.middleware import SessionMiddleware
    from django.contrib.auth.models import AnonymousUser
    
    factory = RequestFactory()
    request = factory.get('/')
    request.user = AnonymousUser()
    
    middleware = SessionMiddleware(lambda r: None)
    middleware.process_request(request)
    request.session.save()
    
    session_cart = SessionCart(request)
    products = Product.objects.filter(available=True)[:2]
    
    print(f"🗂️  ESTRUCTURA DE DATOS EN SESIÓN:")
    print(f"  📍 request.session['cart'] = {{}}")
    print(f"  📍 Formato: {{'product_id': {{'quantity': X, 'price': 'YYYY'}}}}")
    
    if products:
        print(f"\n🧪 AGREGANDO PRODUCTOS DE PRUEBA:")
        for i, product in enumerate(products):
            quantity = i + 1
            session_cart.add(product, quantity=quantity)
            print(f"  + {product.name}")
            print(f"    💾 quantity: {quantity}")
            print(f"    💰 price: {product.current_price}")
            print(f"    🗂️  stored: {{'quantity': {quantity}, 'price': '{product.current_price}'}}")
        
        print(f"\n📊 CÁLCULO SESIÓN:")
        print(f"  🔢 len(session_cart): {len(session_cart)}")
        print(f"  💰 get_total_price(): ${session_cart.get_total_price():,}")
        
        print(f"\n🔍 DATOS INTERNOS:")
        print(f"  📦 session_cart.cart: {session_cart.cart}")
        
        print(f"\n🔗 ORIGEN DE LOS DATOS SESIÓN:")
        print(f"  📍 Cantidad: sum(item['quantity'] for item in cart.values())")
        print(f"  📍 Precio: sum(Decimal(item['price']) * item['quantity'])")
        print(f"  📍 Storage: request.session['cart']")
    
    print(f"\n" + "=" * 60)
    print(f"🎯 RESUMEN DEL FLUJO:")
    print(f"1. Usuario autenticado → CartItem.quantity → Cart.total_items")
    print(f"2. Usuario anónimo → session['cart'][id]['quantity'] → len(SessionCart)")
    print(f"3. Context processor → cart_items_count en todas las templates")
    print(f"4. Templates usan {{{{ cart_items_count }}}} en header/contadores")

if __name__ == "__main__":
    analyze_cart_data_flow()
