#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dulce_bias_project.settings')
django.setup()

from django.contrib.auth.models import User
from cart.models import Cart, SessionCart
from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from cart.context_processors import cart as cart_context

def debug_context_processor():
    print("🔍 DEBUGGING CONTEXT PROCESSOR")
    print("=" * 50)
    
    factory = RequestFactory()
    
    # Simular request para cada usuario
    for user in User.objects.all():
        print(f"\n👤 Usuario: {user.username}")
        
        # Crear request simulado
        request = factory.get('/')
        request.user = user
        
        # Obtener contexto del carrito
        context = cart_context(request)
        
        print(f"  🛒 Context cart_items_count: {context.get('cart_items_count', 'N/A')}")
        print(f"  💰 Context cart_total: {context.get('cart_total', 'N/A')}")
        
        # Verificar carrito real
        try:
            cart_obj = Cart.objects.get(user=user)
            print(f"  📊 DB total_items: {cart_obj.total_items}")
            print(f"  💾 DB items count: {cart_obj.items.count()}")
        except Cart.DoesNotExist:
            print(f"  ❌ No tiene carrito en BD")
    
    print("\n" + "=" * 50)
    
    # Test usuario anónimo
    print("👻 Usuario anónimo:")
    request = factory.get('/')
    
    # Simular usuario anónimo usando AnonymousUser de Django
    from django.contrib.auth.models import AnonymousUser
    request.user = AnonymousUser()
    
    # Agregar sesión
    middleware = SessionMiddleware(lambda r: None)
    middleware.process_request(request)
    request.session.save()
    
    # Crear un carrito de sesión de prueba
    session_cart = SessionCart(request)
    print(f"  📦 Sesión cart length: {len(session_cart)}")
    
    context = cart_context(request)
    print(f"  🛒 Context cart_items_count: {context.get('cart_items_count', 'N/A')}")
    print(f"  💰 Context cart_total: {context.get('cart_total', 'N/A')}")
    
    # Agregar algunos productos de prueba a la sesión para verificar
    from shop.models import Product
    products = Product.objects.filter(available=True)[:2]
    if products:
        print("\n  🧪 Agregando productos de prueba a la sesión:")
        for i, product in enumerate(products):
            session_cart.add(product, quantity=i+1)
            print(f"    - {product.name}: {i+1} unidades")
        
        # Obtener contexto actualizado
        context = cart_context(request)
        print(f"  🛒 Context actualizado cart_items_count: {context.get('cart_items_count', 'N/A')}")
        print(f"  💰 Context actualizado cart_total: {context.get('cart_total', 'N/A')}")
        print(f"  📦 Sesión cart length actualizado: {len(session_cart)}")
    
    print("\n🎯 POSIBLES CAUSAS DEL PROBLEMA:")
    print("1. Usuario está viendo carrito como anónimo pero header muestra datos de usuario autenticado")
    print("2. Caché del navegador mostrando datos antiguos")
    print("3. Sesión del navegador tiene productos que no se muestran en la página")
    print("4. Context processor ejecutándose con usuario diferente al que ve la página")

if __name__ == "__main__":
    debug_context_processor()
