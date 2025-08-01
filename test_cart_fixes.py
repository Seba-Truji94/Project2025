#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dulce_bias_project.settings')
django.setup()

from cart.models import Cart, CartItem, SessionCart
from shop.models import Product
from django.contrib.auth.models import User
from decimal import Decimal

def test_cart_calculations():
    print("🔧 VERIFICANDO CORRECCIONES DEL CARRITO")
    print("=" * 50)
    
    # Verificar cálculos para usuarios autenticados
    users_with_cart = User.objects.filter(cart__isnull=False, cart__items__isnull=False).distinct()
    
    for user in users_with_cart:
        cart = user.cart
        print(f"\n👤 Usuario: {user.username}")
        
        total_esperado = Decimal('0')
        
        for item in cart.items.all():
            product = item.product
            price_with_discount = product.current_price
            item_total_expected = price_with_discount * item.quantity
            item_total_calculated = item.get_total_price()
            
            print(f"🍪 {product.name}")
            print(f"   💰 Precio base: ${product.price}")
            if product.is_on_sale:
                print(f"   💸 Precio con descuento: ${price_with_discount}")
                print(f"   🏷️  OFERTA ACTIVA")
            else:
                print(f"   💸 Precio actual: ${price_with_discount}")
            print(f"   📦 Cantidad: {item.quantity}")
            print(f"   🧮 Total esperado: ${item_total_expected}")
            print(f"   🧮 Total calculado: ${item_total_calculated}")
            
            if item_total_expected != item_total_calculated:
                print(f"   ❌ DISCREPANCIA DETECTADA!")
            else:
                print(f"   ✅ Cálculo correcto")
            
            total_esperado += item_total_expected
        
        print(f"\n💰 RESUMEN:")
        print(f"   🧮 Subtotal esperado: ${total_esperado}")
        print(f"   🧮 Subtotal del carrito: ${cart.total_price}")
        print(f"   🚚 Envío: ${cart.shipping_cost}")
        print(f"   💳 Total final: ${cart.final_total}")
        
        if total_esperado == cart.total_price:
            print(f"   ✅ ¡CÁLCULOS CORRECTOS!")
        else:
            print(f"   ❌ DISCREPANCIA EN TOTALES!")

def test_session_cart():
    print(f"\n🔧 PROBANDO CARRITO DE SESIÓN")
    print("=" * 50)
    
    # Crear un mock request para probar SessionCart
    class MockRequest:
        def __init__(self):
            self.session = {}
    
    mock_request = MockRequest()
    session_cart = SessionCart(mock_request)
    
    # Obtener algunos productos con ofertas
    products_on_sale = Product.objects.filter(is_on_sale=True, available=True)[:3]
    
    print("Agregando productos al carrito de sesión...")
    
    for product in products_on_sale:
        session_cart.add(product, quantity=2)
        print(f"✅ Agregado: {product.name}")
        print(f"   💰 Precio base: ${product.price}")
        print(f"   💸 Precio con descuento: ${product.current_price}")
    
    print(f"\n🧮 TOTALES DEL CARRITO DE SESIÓN:")
    
    total_manual = Decimal('0')
    for item in session_cart:
        item_total = item['price'] * item['quantity']
        product_current_price = item['product'].current_price
        
        print(f"🍪 {item['product'].name}")
        print(f"   💸 Precio guardado en sesión: ${item['price']}")
        print(f"   💸 Precio actual del producto: ${product_current_price}")
        print(f"   📦 Cantidad: {item['quantity']}")
        print(f"   🧮 Total del item: ${item_total}")
        
        if item['price'] != product_current_price:
            print(f"   ⚠️  PRECIOS NO COINCIDEN!")
        else:
            print(f"   ✅ Precios correctos")
        
        total_manual += item_total
    
    session_total = session_cart.get_total_price()
    print(f"\n💰 Total manual: ${total_manual}")
    print(f"💰 Total de sesión: ${session_total}")
    
    if total_manual == session_total:
        print(f"✅ ¡CÁLCULOS DE SESIÓN CORRECTOS!")
    else:
        print(f"❌ DISCREPANCIA EN CÁLCULOS DE SESIÓN!")

if __name__ == "__main__":
    print("🔧 INICIANDO VERIFICACIÓN DE CORRECCIONES\n")
    
    try:
        test_cart_calculations()
        test_session_cart()
        
        print("\n✅ VERIFICACIÓN COMPLETADA")
        
    except Exception as e:
        print(f"\n❌ ERROR EN VERIFICACIÓN: {e}")
        import traceback
        traceback.print_exc()
