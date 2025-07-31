#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dulce_bias_project.settings')
django.setup()

from django.contrib.auth.models import User
from cart.models import Cart, CartItem
from shop.models import Product

def main():
    print("🔍 DIAGNÓSTICO DETALLADO DEL CARRITO")
    print("=" * 50)
    
    # Mostrar usuarios
    users = User.objects.all()
    print("\n👥 Usuarios registrados:")
    for u in users:
        print(f"  ID: {u.id} - {u.username} - Email: {u.email}")
    
    # Analizar carritos
    print(f"\n🛒 Análisis de {Cart.objects.count()} carritos:")
    
    carts = Cart.objects.all()
    for cart in carts:
        print(f"\n🔍 Usuario: {cart.user.username} (ID: {cart.user.id})")
        
        # Contar items en la base de datos
        items_count = cart.items.count()
        calculated_total = cart.total_items
        
        print(f"  📊 Items en BD: {items_count}")
        print(f"  🧮 Total calculado: {calculated_total}")
        
        if items_count != calculated_total:
            print("  ⚠️  ¡DISCREPANCIA DETECTADA!")
        
        # Verificar cada item
        items = cart.items.all()
        if items.exists():
            print("  📦 Productos en el carrito:")
            problem_items = []
            
            for item in items:
                try:
                    product = item.product
                    status = "✅ OK"
                    
                    # Verificar si el producto existe y está disponible
                    if not Product.objects.filter(id=product.id).exists():
                        status = "❌ PRODUCTO NO EXISTE"
                        problem_items.append(item)
                    elif not product.available:
                        status = "⚠️  PRODUCTO NO DISPONIBLE"
                        problem_items.append(item)
                    elif product.stock < item.quantity:
                        status = f"⚠️  STOCK INSUFICIENTE (Stock: {product.stock}, Pedido: {item.quantity})"
                    
                    print(f"    - {product.name} x{item.quantity} - {status}")
                    
                except Product.DoesNotExist:
                    print(f"    - PRODUCTO ELIMINADO (ID: {item.product_id}) x{item.quantity} - ❌ ERROR")
                    problem_items.append(item)
                except Exception as e:
                    print(f"    - ERROR: {e}")
                    problem_items.append(item)
            
            if problem_items:
                print(f"  🚨 Se encontraron {len(problem_items)} items problemáticos")
                
                # Opción para limpiar automáticamente
                print("  🧹 Limpiando items problemáticos automáticamente...")
                for item in problem_items:
                    print(f"    Eliminando: Item ID {item.id}")
                    item.delete()
                
                # Recalcular después de la limpieza
                cart.refresh_from_db()
                new_count = cart.items.count()
                new_total = cart.total_items
                print(f"  ✅ Carrito limpiado. Nuevos totales: {new_count} items, total calculado: {new_total}")
        else:
            print("  📭 Carrito vacío")
    
    print("\n🎯 RESUMEN:")
    print(f"Total de usuarios: {User.objects.count()}")
    print(f"Total de carritos: {Cart.objects.count()}")
    print(f"Carritos activos: {Cart.objects.filter(items__isnull=False).distinct().count()}")
    print("✅ Diagnóstico completado")

if __name__ == "__main__":
    main()
