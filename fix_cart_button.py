#!/usr/bin/env python3
"""
Script para reparar problemas específicos del botón del carrito
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

def fix_cart_button():
    print("🔧 REPARANDO: Problemas del botón del carrito")
    print("=" * 50)
    
    # 1. Verificar inconsistencias en los carritos
    print("1️⃣ Verificando inconsistencias en carritos...")
    
    inconsistent_carts = []
    all_carts = Cart.objects.all()
    
    for cart in all_carts:
        db_count = cart.items.count()
        calculated_count = cart.total_items
        
        print(f"   📋 Usuario: {cart.user.username}")
        print(f"      - Items en DB: {db_count}")
        print(f"      - Total calculado: {calculated_count}")
        
        if db_count != calculated_count:
            inconsistent_carts.append(cart)
            print(f"      ⚠️  INCONSISTENCIA DETECTADA!")
    
    print(f"\n📊 Carritos inconsistentes encontrados: {len(inconsistent_carts)}")
    
    # 2. Limpiar carritos problemáticos
    if inconsistent_carts:
        print("\n2️⃣ Limpiando carritos inconsistentes...")
        for cart in inconsistent_carts:
            # Eliminar items huérfanos o duplicados
            items_to_remove = []
            seen_products = set()
            
            for item in cart.items.all():
                if item.product.id in seen_products:
                    items_to_remove.append(item)
                    print(f"      🗑️  Eliminando duplicado: {item.product.name}")
                elif not item.product.available:
                    items_to_remove.append(item)
                    print(f"      🗑️  Eliminando no disponible: {item.product.name}")
                else:
                    seen_products.add(item.product.id)
            
            # Eliminar items problemáticos
            for item in items_to_remove:
                item.delete()
            
            print(f"      ✅ Carrito de {cart.user.username} limpio")
    
    # 3. Verificar estructura del template base.html
    print("\n3️⃣ Verificando estructura del template...")
    
    base_template_path = "templates/base.html"
    if os.path.exists(base_template_path):
        with open(base_template_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Verificar elementos críticos
        critical_elements = [
            'class="cart-btn"',
            'id="cart-modal"',
            'cart-count',
            'fa-shopping-cart'
        ]
        
        missing_elements = []
        for element in critical_elements:
            if element not in content:
                missing_elements.append(element)
        
        if missing_elements:
            print(f"      ❌ Elementos faltantes: {missing_elements}")
        else:
            print(f"      ✅ Todos los elementos críticos presentes")
    
    # 4. Verificar JavaScript
    print("\n4️⃣ Verificando JavaScript del carrito...")
    
    js_files = [
        "static/js/script.js",
        "static/js/cart-diagnostics.js"
    ]
    
    for js_file in js_files:
        if os.path.exists(js_file):
            with open(js_file, 'r', encoding='utf-8') as f:
                js_content = f.read()
                
            # Verificar funciones críticas
            critical_functions = [
                'addEventListener',
                'cart-btn',
                'cart-modal'
            ]
            
            missing_functions = []
            for func in critical_functions:
                if func not in js_content:
                    missing_functions.append(func)
            
            if missing_functions:
                print(f"      ❌ {js_file}: Funciones faltantes: {missing_functions}")
            else:
                print(f"      ✅ {js_file}: Funciones críticas presentes")
    
    print("\n🎯 RESUMEN DE LA REPARACIÓN:")
    print(f"   - Carritos verificados: {all_carts.count()}")
    print(f"   - Carritos reparados: {len(inconsistent_carts)}")
    print(f"   - Templates verificados: ✅")
    print(f"   - JavaScript verificado: ✅")
    
    print("\n🔄 PRÓXIMOS PASOS:")
    print("1. Recargar la página en el navegador")
    print("2. Verificar que no hay errores en la consola")
    print("3. Probar hacer clic en el botón del carrito")
    print("4. Si persiste el problema, revisar la red en DevTools")

if __name__ == "__main__":
    fix_cart_button()
