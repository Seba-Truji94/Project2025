from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from cart.models import Cart, CartItem
from shop.models import Product


class Command(BaseCommand):
    help = 'Diagnóstico del carrito para detectar problemas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='ID del usuario a diagnosticar'
        )

    def handle(self, *args, **options):
        user_id = options.get('user_id')
        
        if user_id:
            self.debug_user_cart(user_id)
        else:
            self.debug_all_carts()

    def debug_user_cart(self, user_id):
        """Debuggear carrito de un usuario específico"""
        try:
            user = User.objects.get(id=user_id)
            self.stdout.write(f"\n🔍 Diagnóstico del carrito para: {user.username} (ID: {user.id})")
            
            try:
                cart = Cart.objects.get(user=user)
                self.stdout.write(f"✅ Carrito encontrado (ID: {cart.id})")
                self.stdout.write(f"📅 Creado: {cart.created_at}")
                self.stdout.write(f"🔄 Actualizado: {cart.updated_at}")
                
                items = cart.items.all()
                self.stdout.write(f"📦 Total items en DB: {items.count()}")
                self.stdout.write(f"🔢 Total calculado: {cart.total_items}")
                
                if items.exists():
                    self.stdout.write("\n📋 Productos en el carrito:")
                    invalid_items = []
                    
                    for item in items:
                        try:
                            product = item.product
                            if not product.available:
                                self.stdout.write(f"⚠️  {item.id}: {product.name} (Cantidad: {item.quantity}) - PRODUCTO NO DISPONIBLE")
                                invalid_items.append(item)
                            elif product.stock < item.quantity:
                                self.stdout.write(f"⚠️  {item.id}: {product.name} (Cantidad: {item.quantity}) - STOCK INSUFICIENTE (Stock: {product.stock})")
                            else:
                                self.stdout.write(f"✅ {item.id}: {product.name} (Cantidad: {item.quantity}) - OK")
                        except Product.DoesNotExist:
                            self.stdout.write(f"❌ {item.id}: PRODUCTO ELIMINADO (ID: {item.product_id})")
                            invalid_items.append(item)
                    
                    if invalid_items:
                        self.stdout.write(f"\n🧹 Se encontraron {len(invalid_items)} items inválidos")
                        response = input("¿Deseas limpiar los items inválidos? (y/N): ")
                        if response.lower() == 'y':
                            for item in invalid_items:
                                item.delete()
                                self.stdout.write(f"🗑️  Item eliminado: {item.id}")
                            self.stdout.write("✅ Carrito limpiado")
                else:
                    self.stdout.write("📭 Carrito vacío")
                    
            except Cart.DoesNotExist:
                self.stdout.write("❌ No existe carrito para este usuario")
                
        except User.DoesNotExist:
            self.stdout.write(f"❌ Usuario con ID {user_id} no existe")

    def debug_all_carts(self):
        """Debuggear todos los carritos"""
        self.stdout.write("\n🔍 Diagnóstico general de carritos")
        
        # Carritos con items inválidos
        invalid_carts = []
        
        for cart in Cart.objects.all():
            invalid_items = []
            
            for item in cart.items.all():
                try:
                    product = item.product
                    if not product.available or not Product.objects.filter(id=product.id).exists():
                        invalid_items.append(item)
                except Product.DoesNotExist:
                    invalid_items.append(item)
            
            if invalid_items:
                invalid_carts.append((cart, invalid_items))
        
        if invalid_carts:
            self.stdout.write(f"\n⚠️  Se encontraron {len(invalid_carts)} carritos con problemas:")
            
            for cart, items in invalid_carts:
                self.stdout.write(f"Usuario: {cart.user.username} - Items inválidos: {len(items)}")
                
            response = input("\n¿Deseas limpiar todos los items inválidos? (y/N): ")
            if response.lower() == 'y':
                total_cleaned = 0
                for cart, items in invalid_carts:
                    for item in items:
                        item.delete()
                        total_cleaned += 1
                
                self.stdout.write(f"✅ Se limpiaron {total_cleaned} items inválidos")
        else:
            self.stdout.write("✅ Todos los carritos están en buen estado")
        
        # Estadísticas generales
        total_carts = Cart.objects.count()
        active_carts = Cart.objects.filter(items__isnull=False).distinct().count()
        
        self.stdout.write(f"\n📊 Estadísticas:")
        self.stdout.write(f"Total carritos: {total_carts}")
        self.stdout.write(f"Carritos activos: {active_carts}")
        self.stdout.write(f"Carritos vacíos: {total_carts - active_carts}")
