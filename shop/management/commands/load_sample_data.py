from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from shop.models import Category, Product
from decimal import Decimal

class Command(BaseCommand):
    help = 'Carga datos de muestra para la tienda'

    def handle(self, *args, **options):
        # Crear categorías
        categorias_data = [
            {
                'name': 'Galletas Clásicas',
                'slug': 'galletas-clasicas',
                'description': 'Nuestras galletas tradicionales más populares',
            },
            {
                'name': 'Galletas Premium',
                'slug': 'galletas-premium',
                'description': 'Galletas gourmet con ingredientes selectos',
            },
            {
                'name': 'Galletas de Temporada',
                'slug': 'galletas-temporada',
                'description': 'Sabores especiales por tiempo limitado',
            },
            {
                'name': 'Paquetes Familiares',
                'slug': 'paquetes-familiares',
                'description': 'Variedades perfectas para compartir',
            },
        ]

        categorias = {}
        for cat_data in categorias_data:
            categoria, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            categorias[cat_data['slug']] = categoria
            if created:
                self.stdout.write(f"Categoría creada: {categoria.name}")

        # Crear productos
        productos_data = [
            {
                'name': 'Galletas de Chispas de Chocolate',
                'slug': 'galletas-chispas-chocolate',
                'description': 'Deliciosas galletas crujientes con chispas de chocolate belga',
                'price': Decimal('2500'),
                'stock': 50,
                'category': 'galletas-clasicas',
            },
            {
                'name': 'Galletas de Avena y Pasas',
                'slug': 'galletas-avena-pasas',
                'description': 'Galletas nutritivas con avena integral y pasas dulces',
                'price': Decimal('2200'),
                'stock': 45,
                'category': 'galletas-clasicas',
            },
            {
                'name': 'Alfajores de Manjar',
                'slug': 'alfajores-manjar',
                'description': 'Tradicionales alfajores rellenos con manjar casero',
                'price': Decimal('1800'),
                'stock': 60,
                'category': 'galletas-clasicas',
            },
            {
                'name': 'Galletas de Mantequilla',
                'slug': 'galletas-mantequilla',
                'description': 'Clásicas galletas de mantequilla, suaves y aromáticas',
                'price': Decimal('2000'),
                'stock': 40,
                'category': 'galletas-clasicas',
            },
            {
                'name': 'Macarons Franceses',
                'slug': 'macarons-franceses',
                'description': 'Delicados macarons en sabores gourmet: frambuesa, pistacho, vainilla',
                'price': Decimal('4500'),
                'stock': 25,
                'category': 'galletas-premium',
            },
            {
                'name': 'Galletas de Chocolate Belga',
                'slug': 'galletas-chocolate-belga',
                'description': 'Galletas premium con chocolate belga 70% cacao',
                'price': Decimal('3500'),
                'stock': 30,
                'category': 'galletas-premium',
            },
            {
                'name': 'Shortbread Escocés',
                'slug': 'shortbread-escoces',
                'description': 'Auténtico shortbread escocés con mantequilla europea',
                'price': Decimal('3200'),
                'stock': 35,
                'category': 'galletas-premium',
            },
            {
                'name': 'Galletas de Jengibre Navideñas',
                'slug': 'galletas-jengibre-navidenas',
                'description': 'Especiales galletas de jengibre con especias navideñas',
                'price': Decimal('2800'),
                'stock': 20,
                'category': 'galletas-temporada',
            },
            {
                'name': 'Galletas de Calabaza y Canela',
                'slug': 'galletas-calabaza-canela',
                'description': 'Galletas de temporada con calabaza y canela',
                'price': Decimal('2600'),
                'stock': 25,
                'category': 'galletas-temporada',
            },
            {
                'name': 'Caja Mixta Familiar',
                'slug': 'caja-mixta-familiar',
                'description': 'Variedad de 24 galletas mixtas perfectas para la familia',
                'price': Decimal('8500'),
                'stock': 15,
                'category': 'paquetes-familiares',
            },
            {
                'name': 'Paquete Degustación',
                'slug': 'paquete-degustacion',
                'description': '12 galletas diferentes para probar nuestros sabores',
                'price': Decimal('5500'),
                'stock': 20,
                'category': 'paquetes-familiares',
            },
        ]

        for prod_data in productos_data:
            categoria = categorias[prod_data.pop('category')]
            producto, created = Product.objects.get_or_create(
                slug=prod_data['slug'],
                defaults={**prod_data, 'category': categoria}
            )
            if created:
                self.stdout.write(f"Producto creado: {producto.name}")

        self.stdout.write(
            self.style.SUCCESS('Datos de muestra cargados exitosamente!')
        )
