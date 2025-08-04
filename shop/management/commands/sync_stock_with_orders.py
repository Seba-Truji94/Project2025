from django.core.management.base import BaseCommand
from django.db import transaction
from orders.models import Order, OrderItem
from shop.models import Product, ProductStock
from django.utils import timezone


class Command(BaseCommand):
    help = 'Actualiza el stock basado en órdenes existentes y crea los movimientos de stock correspondientes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula la operación sin hacer cambios reales',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Fuerza la actualización incluso si ya existen movimientos de stock',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('MODO DRY-RUN: No se realizarán cambios reales')
            )
        
        self.stdout.write('Iniciando sincronización de stock con órdenes existentes...')
        
        # Obtener todas las órdenes que deberían afectar el stock
        orders = Order.objects.filter(
            status__in=['confirmed', 'processing', 'shipped', 'delivered']
        ).order_by('created_at')
        
        total_orders = orders.count()
        processed_orders = 0
        created_movements = 0
        stock_adjustments = 0
        
        self.stdout.write(f'Encontradas {total_orders} órdenes a procesar...')
        
        with transaction.atomic():
            for order in orders:
                # Verificar si ya existen movimientos de stock para esta orden
                existing_movements = ProductStock.objects.filter(
                    reference=order.order_number
                ).exists()
                
                if existing_movements and not force:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Orden #{order.order_number} ya tiene movimientos de stock (usar --force para sobrescribir)'
                        )
                    )
                    continue
                
                self.stdout.write(f'Procesando orden #{order.order_number}...')
                
                # Procesar cada item de la orden
                for item in order.items.all():
                    product = item.product
                    
                    if not dry_run:
                        # Si estamos forzando, eliminar movimientos existentes
                        if force and existing_movements:
                            ProductStock.objects.filter(
                                reference=order.order_number,
                                product=product
                            ).delete()
                        
                        # Obtener el stock actual antes del ajuste
                        current_stock = product.stock
                        
                        # Crear movimiento de stock por la venta
                        movement = ProductStock.objects.create(
                            product=product,
                            movement_type='sale',
                            quantity=-item.quantity,  # Negativo porque es una salida
                            previous_stock=current_stock + item.quantity,  # El stock que debería haber antes
                            new_stock=current_stock,  # El stock actual
                            reason=f'Sincronización: Venta - Pedido #{order.order_number}',
                            reference=order.order_number,
                            user=order.user
                        )
                        
                        created_movements += 1
                        
                        self.stdout.write(
                            f'  ✓ {product.name}: -{item.quantity} unidades (Stock actual: {current_stock})'
                        )
                    else:
                        self.stdout.write(
                            f'  [DRY-RUN] {product.name}: -{item.quantity} unidades'
                        )
                
                processed_orders += 1
                
                # Mostrar progreso cada 10 órdenes
                if processed_orders % 10 == 0:
                    self.stdout.write(f'Progreso: {processed_orders}/{total_orders} órdenes')
        
        # Verificar y reportar inconsistencias de stock
        self.stdout.write('\nVerificando consistencia de stock...')
        
        products_with_issues = []
        total_products_checked = 0
        
        for product in Product.objects.all():
            total_products_checked += 1
            
            # Calcular el stock teórico basado en movimientos
            movements = ProductStock.objects.filter(product=product).order_by('created_at')
            
            if movements.exists():
                # El stock actual debería ser igual al último new_stock registrado
                last_movement = movements.last()
                
                if product.stock != last_movement.new_stock:
                    products_with_issues.append({
                        'product': product,
                        'current_stock': product.stock,
                        'expected_stock': last_movement.new_stock,
                        'difference': product.stock - last_movement.new_stock
                    })
        
        # Reportar resultados
        self.stdout.write('\n' + '='*50)
        self.stdout.write('RESUMEN DE SINCRONIZACIÓN')
        self.stdout.write('='*50)
        self.stdout.write(f'Órdenes procesadas: {processed_orders}/{total_orders}')
        self.stdout.write(f'Movimientos de stock creados: {created_movements}')
        self.stdout.write(f'Productos verificados: {total_products_checked}')
        
        if products_with_issues:
            self.stdout.write(
                self.style.WARNING(f'Productos con inconsistencias de stock: {len(products_with_issues)}')
            )
            
            for issue in products_with_issues:
                self.stdout.write(
                    f'  - {issue["product"].name}: '
                    f'Stock actual: {issue["current_stock"]}, '
                    f'Esperado: {issue["expected_stock"]}, '
                    f'Diferencia: {issue["difference"]}'
                )
        else:
            self.stdout.write(
                self.style.SUCCESS('✓ Todos los productos tienen stock consistente')
            )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('\nEsto fue una simulación. Ejecuta sin --dry-run para aplicar los cambios.')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('\n✓ Sincronización de stock completada exitosamente!')
            )
        
        # Sugerencias adicionales
        self.stdout.write('\n' + '='*50)
        self.stdout.write('RECOMENDACIONES')
        self.stdout.write('='*50)
        self.stdout.write('1. Verifica manualmente los productos con inconsistencias')
        self.stdout.write('2. Considera crear movimientos de ajuste para corregir diferencias')
        self.stdout.write('3. A partir de ahora, el stock se actualizará automáticamente')
        self.stdout.write('4. Ejecuta: python manage.py check_stock_alerts para ver alertas')
