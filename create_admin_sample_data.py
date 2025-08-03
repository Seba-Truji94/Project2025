#!/usr/bin/env python
"""
Script para crear datos de ejemplo para el módulo de administración
"""
import os
import django
from decimal import Decimal
from datetime import datetime, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dulce_bias_project.settings')
django.setup()

from django.utils import timezone
from shop.models import TaxConfiguration, DiscountCoupon, Supplier, Product, ProductSupplier
from django.contrib.auth.models import User


def create_sample_data():
    """Crear datos de ejemplo para administración"""
    
    print("🔧 Creando datos de ejemplo para administración...")
    
    # 1. Configuración de Impuestos
    print("📊 Creando configuraciones de impuestos...")
    
    iva_chile, created = TaxConfiguration.objects.get_or_create(
        name="IVA Chile",
        defaults={
            'rate': Decimal('19.00'),
            'is_active': True,
            'applies_to_shipping': True
        }
    )
    if created:
        print(f"  ✅ Creado: {iva_chile}")
    
    sin_impuesto, created = TaxConfiguration.objects.get_or_create(
        name="Sin Impuesto",
        defaults={
            'rate': Decimal('0.00'),
            'is_active': True,
            'applies_to_shipping': False
        }
    )
    if created:
        print(f"  ✅ Creado: {sin_impuesto}")
    
    # 2. Cupones de Descuento
    print("🎫 Creando cupones de descuento...")
    
    # Obtener o crear usuario admin
    admin_user, _ = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@dulcebias.cl',
            'is_staff': True,
            'is_superuser': True
        }
    )
    
    cupones_ejemplo = [
        {
            'code': 'BIENVENIDO20',
            'name': 'Descuento de Bienvenida',
            'description': 'Descuento del 20% para nuevos clientes',
            'discount_type': 'percentage',
            'discount_value': Decimal('20.00'),
            'minimum_order_amount': Decimal('10000'),
            'max_uses': 100,
            'valid_from': timezone.now(),
            'valid_until': timezone.now() + timedelta(days=30)
        },
        {
            'code': 'ENVIOGRATIS',
            'name': 'Envío Gratis',
            'description': 'Envío gratuito en compras superiores a $15.000',
            'discount_type': 'free_shipping',
            'discount_value': Decimal('0.00'),
            'minimum_order_amount': Decimal('15000'),
            'max_uses': None,
            'valid_from': timezone.now(),
            'valid_until': timezone.now() + timedelta(days=60)
        },
        {
            'code': 'PRIMERACOMPRA',
            'name': 'Primera Compra',
            'description': '$2.000 de descuento en tu primera compra',
            'discount_type': 'fixed_amount',
            'discount_value': Decimal('2000.00'),
            'minimum_order_amount': Decimal('8000'),
            'usage_type': 'per_customer',
            'max_uses': 500,
            'valid_from': timezone.now(),
            'valid_until': timezone.now() + timedelta(days=90)
        },
        {
            'code': 'BLACKFRIDAY50',
            'name': 'Black Friday Super Descuento',
            'description': '50% de descuento en productos seleccionados',
            'discount_type': 'percentage',
            'discount_value': Decimal('50.00'),
            'minimum_order_amount': Decimal('5000'),
            'maximum_discount_amount': Decimal('10000'),
            'max_uses': 200,
            'valid_from': timezone.now() + timedelta(days=10),
            'valid_until': timezone.now() + timedelta(days=15)
        }
    ]
    
    for cupon_data in cupones_ejemplo:
        cupon, created = DiscountCoupon.objects.get_or_create(
            code=cupon_data['code'],
            defaults={
                **cupon_data,
                'created_by': admin_user,
                'is_active': True
            }
        )
        if created:
            print(f"  ✅ Creado cupón: {cupon}")
    
    # 3. Proveedores
    print("🏭 Creando proveedores...")
    
    proveedores_ejemplo = [
        {
            'name': 'Ingredientes Premium SpA',
            'contact_person': 'María González',
            'email': 'compras@ingredientespremium.cl',
            'phone': '+56 2 2345 6789',
            'address': 'Av. Providencia 1234, Oficina 456',
            'city': 'Santiago',
            'tax_id': '76.123.456-7',
            'rating': Decimal('4.5'),
            'notes': 'Proveedor principal de ingredientes orgánicos'
        },
        {
            'name': 'Distribuidora Dulce Norte',
            'contact_person': 'Carlos Ramírez',
            'email': 'ventas@dulcenorte.cl',
            'phone': '+56 55 234 5678',
            'address': 'Calle Industrial 789',
            'city': 'Antofagasta',
            'tax_id': '78.987.654-3',
            'rating': Decimal('4.2'),
            'notes': 'Especialistas en productos del norte'
        },
        {
            'name': 'Chocolates Artesanales del Sur',
            'contact_person': 'Ana Pérez',
            'email': 'contacto@chocolatessur.cl',
            'phone': '+56 63 345 6789',
            'address': 'Camino Rural Km 15',
            'city': 'Valdivia',
            'tax_id': '77.555.333-1',
            'rating': Decimal('4.8'),
            'notes': 'Chocolate orgánico de alta calidad'
        },
        {
            'name': 'Frutos Secos y Más Ltda',
            'contact_person': 'Roberto Silva',
            'email': 'pedidos@frutossecos.cl',
            'phone': '+56 2 9876 5432',
            'address': 'Mercado Central Local 45',
            'city': 'Santiago',
            'tax_id': '79.111.222-8',
            'rating': Decimal('4.0'),
            'notes': 'Amplia variedad de frutos secos nacionales e importados'
        }
    ]
    
    for proveedor_data in proveedores_ejemplo:
        proveedor, created = Supplier.objects.get_or_create(
            name=proveedor_data['name'],
            defaults=proveedor_data
        )
        if created:
            print(f"  ✅ Creado proveedor: {proveedor}")
    
    # 4. Asignar configuraciones de impuesto a productos existentes
    print("🏷️ Configurando impuestos en productos...")
    
    products_count = 0
    for product in Product.objects.all():
        if not product.tax_configuration:
            # Asignar IVA a la mayoría de productos
            if 'premium' in product.name.lower() or 'gourmet' in product.name.lower():
                product.tax_configuration = iva_chile
            else:
                product.tax_configuration = iva_chile  # Por defecto IVA
            
            product.save()
            products_count += 1
    
    print(f"  ✅ Configurado IVA en {products_count} productos")
    
    # 5. Crear relaciones producto-proveedor para algunos productos
    print("🔗 Creando relaciones producto-proveedor...")
    
    # Obtener algunos productos y proveedores
    productos = Product.objects.all()[:5]  # Primeros 5 productos
    proveedores = Supplier.objects.all()
    
    relations_created = 0
    for i, product in enumerate(productos):
        proveedor = proveedores[i % len(proveedores)]  # Rotar proveedores
        
        # Calcular precio de costo (70% del precio de venta)
        cost_price = product.price * Decimal('0.7')
        
        relation, created = ProductSupplier.objects.get_or_create(
            product=product,
            supplier=proveedor,
            defaults={
                'supplier_sku': f'SKU-{product.id}-{proveedor.id}',
                'cost_price': cost_price,
                'minimum_order_quantity': 10,
                'lead_time_days': 7,
                'is_primary': True
            }
        )
        
        if created:
            relations_created += 1
    
    print(f"  ✅ Creadas {relations_created} relaciones producto-proveedor")
    
    # 6. Estadísticas finales
    print("\n📊 RESUMEN DE DATOS CREADOS:")
    print(f"  • Configuraciones de impuesto: {TaxConfiguration.objects.count()}")
    print(f"  • Cupones de descuento: {DiscountCoupon.objects.count()}")
    print(f"  • Proveedores: {Supplier.objects.count()}")
    print(f"  • Productos con IVA configurado: {Product.objects.exclude(tax_configuration=None).count()}")
    print(f"  • Relaciones producto-proveedor: {ProductSupplier.objects.count()}")
    
    print("\n🎉 ¡Datos de ejemplo creados exitosamente!")
    print("\nAhora puedes acceder al panel de administración en:")
    print("http://127.0.0.1:8000/admin/")
    print("\nNuevas secciones disponibles:")
    print("  • 🏷️ Configuraciones de Impuesto")
    print("  • 🎫 Cupones de Descuento")
    print("  • 📦 Movimientos de Stock")
    print("  • 🏭 Proveedores")
    print("  • 🔗 Relaciones Producto-Proveedor")


if __name__ == "__main__":
    create_sample_data()
