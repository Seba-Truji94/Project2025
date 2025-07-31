from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from cart.models import Cart, CartItem
from shop.models import Product


class Command(BaseCommand):
    help = 'Limpiar carritos de productos no disponibles o eliminados'

    def handle(self, *args, **options):
        self.stdout.write("🧹 Iniciando limpieza de carritos...")
        
        cleaned_items = 0
        cleaned_carts = 0
        
        for cart in Cart.objects.all():
            cart_cleaned = False
            invalid_items = []
            
            for item in cart.items.all():
                try:
                    product = item.product
                    # Verificar si el producto existe y está disponible
                    if not product.available or not Product.objects.filter(id=product.id).exists():
                        invalid_items.append(item)
                except Product.DoesNotExist:
                    invalid_items.append(item)
            
            if invalid_items:
                cart_cleaned = True
                cleaned_carts += 1
                
                self.stdout.write(f"🛒 Limpiando carrito de {cart.user.username}:")
                for item in invalid_items:
                    try:
                        product_name = item.product.name
                    except:
                        product_name = f"Producto ID {item.product_id} (eliminado)"
                    
                    self.stdout.write(f"  ❌ Eliminando: {product_name} x{item.quantity}")
                    item.delete()
                    cleaned_items += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Limpieza completada: {cleaned_items} items eliminados de {cleaned_carts} carritos'
            )
        )
        
        if cleaned_items == 0:
            self.stdout.write(self.style.SUCCESS('✨ Todos los carritos están limpios'))
