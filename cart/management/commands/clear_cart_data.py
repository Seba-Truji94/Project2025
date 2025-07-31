from django.core.management.base import BaseCommand
from django.contrib.sessions.models import Session
from cart.models import Cart, CartItem


class Command(BaseCommand):
    help = 'Limpiar completamente todas las sesiones y carritos para resolver problemas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            help='Limpiar solo el carrito de un usuario específico'
        )
        parser.add_argument(
            '--sessions',
            action='store_true',
            help='Limpiar todas las sesiones de Django'
        )

    def handle(self, *args, **options):
        user = options.get('user')
        clean_sessions = options.get('sessions')
        
        if user:
            self.clean_user_cart(user)
        elif clean_sessions:
            self.clean_all_sessions()
        else:
            self.clean_all_carts()

    def clean_user_cart(self, username):
        """Limpiar carrito de un usuario específico"""
        from django.contrib.auth.models import User
        
        try:
            user = User.objects.get(username=username)
            cart, created = Cart.objects.get_or_create(user=user)
            
            items_count = cart.items.count()
            cart.items.all().delete()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Carrito de {username} limpiado: {items_count} items eliminados'
                )
            )
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'❌ Usuario {username} no existe')
            )

    def clean_all_sessions(self):
        """Limpiar todas las sesiones de Django"""
        session_count = Session.objects.count()
        Session.objects.all().delete()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ {session_count} sesiones eliminadas'
            )
        )
        self.stdout.write(
            self.style.WARNING(
                '⚠️ Todos los usuarios deberán volver a autenticarse'
            )
        )

    def clean_all_carts(self):
        """Limpiar todos los carritos"""
        carts = Cart.objects.all()
        total_items = 0
        
        for cart in carts:
            items_count = cart.items.count()
            total_items += items_count
            cart.items.all().delete()
            self.stdout.write(f'🧹 {cart.user.username}: {items_count} items eliminados')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Todos los carritos limpiados: {total_items} items totales eliminados'
            )
        )
