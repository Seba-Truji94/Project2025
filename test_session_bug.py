#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dulce_bias_project.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.models import AnonymousUser
from cart.models import SessionCart
from cart.context_processors import cart as cart_context
from shop.models import Product

def test_session_cart_bug():
    print("🔍 TESTING SESSION CART BUG")
    print("=" * 40)
    
    factory = RequestFactory()
    request = factory.get('/')
    request.user = AnonymousUser()
    
    # Configurar sesión
    middleware = SessionMiddleware(lambda r: None)
    middleware.process_request(request)
    request.session.save()
    
    print("1. Estado inicial:")
    print(f"   Session keys: {list(request.session.keys())}")
    print(f"   Session data: {dict(request.session)}")
    
    # Crear SessionCart y agregar productos
    session_cart = SessionCart(request)
    print(f"   SessionCart length: {len(session_cart)}")
    print(f"   SessionCart dict: {session_cart.cart}")
    
    # Agregar productos
    products = Product.objects.filter(available=True)[:2]
    if products:
        print("\n2. Agregando productos:")
        for i, product in enumerate(products):
            session_cart.add(product, quantity=i+1)
            print(f"   Added: {product.name} x{i+1}")
            print(f"   Cart after add: {session_cart.cart}")
            print(f"   Length after add: {len(session_cart)}")
    
    print(f"\n3. Estado final del SessionCart:")
    print(f"   Length: {len(session_cart)}")
    print(f"   Cart dict: {session_cart.cart}")
    print(f"   Session data: {dict(request.session)}")
    
    # Probar context processor
    print(f"\n4. Context Processor:")
    context = cart_context(request)
    print(f"   cart_items_count: {context.get('cart_items_count')}")
    print(f"   cart_total: {context.get('cart_total')}")
    
    # Crear NUEVO SessionCart con la misma request
    print(f"\n5. Nuevo SessionCart con misma request:")
    new_session_cart = SessionCart(request)
    print(f"   New length: {len(new_session_cart)}")
    print(f"   New cart dict: {new_session_cart.cart}")
    
    # Probar context processor de nuevo
    print(f"\n6. Context Processor después:")
    context2 = cart_context(request)
    print(f"   cart_items_count: {context2.get('cart_items_count')}")
    print(f"   cart_total: {context2.get('cart_total')}")
    
if __name__ == "__main__":
    test_session_cart_bug()
