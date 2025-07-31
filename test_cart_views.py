#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dulce_bias_project.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from cart.views import CartDetailView
from cart.models import SessionCart

def test_cart_views():
    print("🔍 TESTING VISTA DE CARRITO")
    print("=" * 40)
    
    factory = RequestFactory()
    
    # Test 1: Usuario autenticado
    print("\n1️⃣ USUARIOS AUTENTICADOS:")
    for user in User.objects.all():
        request = factory.get('/cart/')
        request.user = user
        
        view = CartDetailView()
        view.request = request
        context = view.get_context_data()
        
        print(f"\n👤 Usuario: {user.username}")
        if 'cart' in context:
            cart = context['cart']
            print(f"   🛒 Items en carrito: {cart.total_items}")
            print(f"   📦 Items en context: {len(context.get('cart_items', []))}")
        else:
            print("   ❌ No hay carrito en el contexto")
    
    # Test 2: Usuario no autenticado (sesión)
    print("\n2️⃣ USUARIO NO AUTENTICADO (SESIÓN):")
    request = factory.get('/cart/')
    request.user = AnonymousUser()
    
    # Agregar middleware de sesión
    middleware = SessionMiddleware(lambda r: None)
    middleware.process_request(request)
    request.session.save()
    
    # Simular carrito de sesión con algunos productos
    from shop.models import Product
    products = Product.objects.filter(available=True)[:2]
    
    session_cart = SessionCart(request)
    if products:
        session_cart.add(products[0], quantity=3)
        if len(products) > 1:
            session_cart.add(products[1], quantity=2)
    
    view = CartDetailView()
    view.request = request
    context = view.get_context_data()
    
    print(f"👤 Usuario: Anónimo")
    if 'session_cart' in context:
        session_cart = context['session_cart']
        print(f"   🛒 Items en sesión: {len(session_cart)}")
        print(f"   📦 Items en context: {len(context.get('cart_items', []))}")
        
        print("   📋 Productos en sesión:")
        for item in session_cart:
            print(f"     - {item['product'].name}: {item['quantity']} unidades")
    else:
        print("   ❌ No hay carrito de sesión")

if __name__ == "__main__":
    test_cart_views()
