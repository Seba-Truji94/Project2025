#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dulce_bias_project.settings')
django.setup()

from shop.models import Product
from cart.models import Cart, CartItem
from django.contrib.auth.models import User
from decimal import Decimal

def detailed_cart_analysis():
    print("🔍 ANÁLISIS DETALLADO DEL CARRITO")
    print("=" * 50)
    
    # Buscar usuario con carrito
    user = User.objects.filter(cart__items__isnull=False).first()
    
    if not user:
        print("❌ No hay usuarios con items en el carrito")
        return
        
    cart = user.cart
    print(f"👤 Analizando carrito de: {user.username}")
    print()
    
    total_esperado = Decimal('0')
    
    for item in cart.items.all():
        product = item.product
        print(f"🍪 PRODUCTO: {product.name}")
        print(f"   💰 Precio base: ${product.price}")
        
        if product.is_on_sale:
            print(f"   🏷️  PRODUCTO EN OFERTA")
            if product.discount_price:
                print(f"   💸 Precio con descuento fijo: ${product.discount_price}")
            elif product.discount_percentage > 0:
                discount_amount = product.price * (Decimal(str(product.discount_percentage)) / Decimal('100'))
                discounted_price = product.price - discount_amount
                print(f"   📊 Descuento porcentual: {product.discount_percentage}%")
                print(f"   💰 Descuento en pesos: ${discount_amount}")
                print(f"   💸 Precio final: ${discounted_price}")
        
        current_price = product.current_price
        print(f"   💳 Precio actual (método): ${current_price}")
        print(f"   📦 Cantidad: {item.quantity}")
        
        # Calcular total del item
        item_total = current_price * item.quantity
        total_esperado += item_total
        
        print(f"   🧮 Total del item: ${item_total}")
        print(f"   🎨 Total formateado: {item.formatted_total_price}")
        print()
    
    print(f"💰 TOTALES:")
    print(f"   🧮 Subtotal esperado: ${total_esperado}")
    print(f"   🧮 Subtotal del carrito: ${cart.total_price}")
    print(f"   🎨 Subtotal formateado: {cart.formatted_total_price}")
    
    if cart.total_price >= 15000:
        print(f"   🚚 Envío: GRATIS (compra ≥ $15.000)")
    else:
        missing = 15000 - cart.total_price
        print(f"   🚚 Envío: $3.000 (faltan ${missing} para envío gratis)")
    
    print(f"   💳 Total final: ${cart.final_total}")
    print(f"   🎨 Total final formateado: {cart.formatted_final_total}")
    
    # Verificar coincidencia
    if total_esperado == cart.total_price:
        print(f"\n✅ ¡CÁLCULOS CORRECTOS!")
    else:
        print(f"\n❌ ¡DISCREPANCIA EN CÁLCULOS!")
        print(f"   Diferencia: ${abs(total_esperado - cart.total_price)}")

def check_product_discounts():
    print("\n🔍 VERIFICACIÓN DE DESCUENTOS")
    print("=" * 50)
    
    products_on_sale = Product.objects.filter(is_on_sale=True, available=True)
    
    for product in products_on_sale:
        print(f"\n🍪 {product.name}")
        print(f"   💰 Precio base: ${product.price}")
        print(f"   🏷️  En oferta: {product.is_on_sale}")
        
        if product.discount_price:
            print(f"   💸 Precio con descuento fijo: ${product.discount_price}")
            calculated_discount = product.price - product.discount_price
            percentage = (calculated_discount / product.price) * 100
            print(f"   📊 Descuento calculado: ${calculated_discount} ({percentage:.1f}%)")
        
        if product.discount_percentage > 0:
            print(f"   📊 Porcentaje de descuento: {product.discount_percentage}%")
            discount_amount = product.price * (Decimal(str(product.discount_percentage)) / Decimal('100'))
            final_price = product.price - discount_amount
            print(f"   💰 Descuento en pesos: ${discount_amount}")
            print(f"   💸 Precio final calculado: ${final_price}")
        
        current_price = product.current_price
        print(f"   💳 Precio actual (propiedad): ${current_price}")
        print(f"   🎨 Precio formateado: {product.formatted_current_price}")

if __name__ == "__main__":
    print("🧮 INICIANDO ANÁLISIS DETALLADO\n")
    
    try:
        detailed_cart_analysis()
        check_product_discounts()
        
        print("\n✅ ANÁLISIS COMPLETADO")
        
    except Exception as e:
        print(f"\n❌ ERROR EN ANÁLISIS: {e}")
        import traceback
        traceback.print_exc()
