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

def debug_cart_calculations():
    print("🔍 DIAGNÓSTICO DE CÁLCULOS DEL CARRITO")
    print("=" * 50)
    
    # Verificar usuarios con carrito
    users_with_cart = User.objects.filter(cart__isnull=False)
    
    if not users_with_cart.exists():
        print("❌ No hay usuarios con carritos")
        return
    
    for user in users_with_cart:
        cart = user.cart
        print(f"\n👤 Usuario: {user.username}")
        print(f"📅 Carrito creado: {cart.created_at}")
        print(f"🔄 Última actualización: {cart.updated_at}")
        
        # Verificar items del carrito
        items = cart.items.all()
        if not items.exists():
            print("❌ El carrito está vacío")
            continue
            
        print(f"\n📦 Items en el carrito: {items.count()}")
        
        subtotal_manual = Decimal('0')
        
        for i, item in enumerate(items, 1):
            product = item.product
            print(f"\n{i}. 🍪 {product.name}")
            print(f"   💰 Precio base: ${product.price}")
            print(f"   💸 Precio actual: ${product.current_price}")
            print(f"   📊 Cantidad: {item.quantity}")
            
            # Calcular total del item
            item_total = item.get_total_price()
            item_total_manual = product.current_price * item.quantity
            
            print(f"   🧮 Total del item (método): ${item_total}")
            print(f"   🧮 Total del item (manual): ${item_total_manual}")
            
            if item_total != item_total_manual:
                print(f"   ⚠️  ¡DISCREPANCIA EN CÁLCULO DEL ITEM!")
            
            subtotal_manual += item_total_manual
        
        # Verificar totales del carrito
        print(f"\n💰 RESUMEN DEL CARRITO:")
        print(f"   📊 Total items (propiedad): {cart.total_items}")
        print(f"   📊 Total items (manual): {sum(item.quantity for item in items)}")
        
        cart_total = cart.total_price
        print(f"   💰 Subtotal (propiedad): ${cart_total}")
        print(f"   💰 Subtotal (manual): ${subtotal_manual}")
        
        if cart_total != subtotal_manual:
            print(f"   ⚠️  ¡DISCREPANCIA EN SUBTOTAL!")
        
        # Verificar cálculo de envío
        shipping_cost = cart.shipping_cost
        shipping_manual = 0 if cart_total >= 15000 else 3000
        
        print(f"   🚚 Envío (propiedad): ${shipping_cost}")
        print(f"   🚚 Envío (manual): ${shipping_manual}")
        
        if shipping_cost != shipping_manual:
            print(f"   ⚠️  ¡DISCREPANCIA EN CÁLCULO DE ENVÍO!")
        
        # Verificar total final
        final_total = cart.final_total
        final_manual = cart_total + shipping_cost
        
        print(f"   💳 Total final (propiedad): ${final_total}")
        print(f"   💳 Total final (manual): ${final_manual}")
        
        if final_total != final_manual:
            print(f"   ⚠️  ¡DISCREPANCIA EN TOTAL FINAL!")
        
        # Verificar formatos
        print(f"\n🎨 FORMATOS:")
        print(f"   Subtotal formateado: {cart.formatted_total_price}")
        print(f"   Envío formateado: {cart.formatted_shipping_cost}")
        print(f"   Total formateado: {cart.formatted_final_total}")
        

def test_product_prices():
    print("\n🔍 VERIFICACIÓN DE PRECIOS DE PRODUCTOS")
    print("=" * 50)
    
    products = Product.objects.filter(available=True)[:5]
    
    for product in products:
        print(f"\n🍪 {product.name}")
        print(f"   💰 Precio base: ${product.price}")
        print(f"   💸 Precio actual: ${product.current_price}")
        print(f"   🏷️  En oferta: {product.is_on_sale}")
        
        if product.is_on_sale:
            print(f"   💸 Precio con descuento: ${product.discount_price}")
            print(f"   📊 Porcentaje descuento: {product.discount_percentage}%")
        
        print(f"   🎨 Precio formateado: {product.formatted_current_price}")


def verify_cart_item_calculations():
    print("\n🔍 VERIFICACIÓN DETALLADA DE ITEMS")
    print("=" * 50)
    
    cart_items = CartItem.objects.all()[:10]
    
    for item in cart_items:
        print(f"\n📦 Item: {item}")
        print(f"   🍪 Producto: {item.product.name}")
        print(f"   💰 Precio del producto: ${item.product.current_price}")
        print(f"   📊 Cantidad: {item.quantity}")
        
        # Verificar cálculo
        calculated_total = item.get_total_price()
        manual_total = item.product.current_price * item.quantity
        
        print(f"   🧮 Total calculado: ${calculated_total}")
        print(f"   🧮 Total manual: ${manual_total}")
        print(f"   🎨 Total formateado: {item.formatted_total_price}")
        
        if calculated_total != manual_total:
            print(f"   ⚠️  ¡DISCREPANCIA!")


if __name__ == "__main__":
    print("🧮 INICIANDO DIAGNÓSTICO DE CÁLCULOS DEL CARRITO\n")
    
    try:
        debug_cart_calculations()
        test_product_prices()
        verify_cart_item_calculations()
        
        print("\n✅ DIAGNÓSTICO COMPLETADO")
        
    except Exception as e:
        print(f"\n❌ ERROR EN DIAGNÓSTICO: {e}")
        import traceback
        traceback.print_exc()
