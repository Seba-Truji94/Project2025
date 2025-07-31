#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dulce_bias_project.settings')
django.setup()

from shop.models import Product, Category
from decimal import Decimal

def setup_products():
    """Crear productos con descuento para probar el sistema."""
    
    # Crear categoría por defecto si no existe
    category, created = Category.objects.get_or_create(
        name='Galletas Artesanales',
        defaults={
            'slug': 'galletas-artesanales',
            'description': 'Deliciosas galletas caseras hechas con ingredientes de primera calidad'
        }
    )
    
    if created:
        print(f"✅ Categoría creada: {category.name}")
    else:
        print(f"📂 Categoría existente: {category.name}")
    
    products_data = [
        {
            'name': 'Galletas de Chocolate Premium',
            'slug': 'galletas-chocolate-premium',
            'category': category,
            'description': 'Deliciosas galletas artesanales con chocolate belga',
            'ingredients': 'Harina, mantequilla, chocolate belga, azúcar, huevos, vainilla',
            'price': Decimal('12990'),
            'stock': 25,
            'is_on_sale': True,
            'discount_percentage': Decimal('15.00')
        },
        {
            'name': 'Mix de Galletas Navideñas',
            'slug': 'mix-galletas-navidenas',
            'category': category,
            'description': 'Variedad especial de galletas temáticas navideñas',
            'ingredients': 'Harina, mantequilla, azúcar, especias navideñas, decoración comestible',
            'price': Decimal('18990'),
            'stock': 15,
            'is_on_sale': True,
            'discount_price': Decimal('14990')
        },
        {
            'name': 'Galletas de Avena y Pasas',
            'slug': 'galletas-avena-pasas',
            'category': category,
            'description': 'Galletas caseras con avena integral y pasas',
            'ingredients': 'Avena integral, harina, pasas, mantequilla, miel, canela',
            'price': Decimal('9990'),
            'stock': 30,
            'is_on_sale': False
        },
        {
            'name': 'Galletas de Mantequilla Clásicas',
            'slug': 'galletas-mantequilla-clasicas',
            'category': category,
            'description': 'Tradicionales galletas de mantequilla caseras',
            'ingredients': 'Harina, mantequilla, azúcar, huevos, esencia de vainilla',
            'price': Decimal('8990'),
            'stock': 40,
            'is_on_sale': True,
            'discount_percentage': Decimal('20.00')
        },
        {
            'name': 'Galletas Integrales de Miel',
            'slug': 'galletas-integrales-miel',
            'category': category,
            'description': 'Galletas saludables con harina integral y miel natural',
            'ingredients': 'Harina integral, miel natural, aceite de oliva, semillas, avena',
            'price': Decimal('11490'),
            'stock': 20,
            'is_on_sale': False
        }
    ]

    print("🍪 Configurando productos con descuentos...")
    print("=" * 50)
    
    for data in products_data:
        product, created = Product.objects.get_or_create(
            name=data['name'],
            defaults=data
        )
        
        if created:
            print(f"✅ Producto creado: {product.name}")
        else:
            # Actualizar el producto existente
            for key, value in data.items():
                setattr(product, key, value)
            product.save()
            print(f"🔄 Producto actualizado: {product.name}")
        
        # Mostrar información del producto
        if product.is_on_sale:
            print(f"   💰 Precio: ${product.price} → ${product.current_price}")
            if hasattr(product, 'discount_percentage') and product.discount_percentage:
                print(f"   🏷️  Descuento: {product.discount_percentage}%")
            print(f"   📦 Stock: {product.stock} unidades")
        else:
            print(f"   💰 Precio: ${product.price}")
            print(f"   📦 Stock: {product.stock} unidades")
        print()

    print("=" * 50)
    print(f"📊 Total de productos: {Product.objects.count()}")
    print("🎯 Productos con descuento:")
    
    sale_products = Product.objects.filter(is_on_sale=True)
    for product in sale_products:
        if hasattr(product, 'discount_amount') and callable(product.discount_amount):
            discount_info = f"({product.discount_amount}% desc.)"
        else:
            discount_info = "(con descuento)"
        print(f"  - {product.name}: ${product.price} → ${product.current_price} {discount_info}")
    
    print("\n✅ ¡Productos configurados exitosamente!")

if __name__ == '__main__':
    setup_products()
