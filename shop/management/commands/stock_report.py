from django.core.management.base import BaseCommand
from django.db.models import Sum, Count, Q
from shop.models import Product, ProductStock
from orders.models import Order, OrderItem
from datetime import datetime, timedelta
from django.utils import timezone
import csv
import os


class Command(BaseCommand):
    help = 'Genera reportes detallados de movimientos de stock'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Número de días hacia atrás para el reporte (default: 30)',
        )
        parser.add_argument(
            '--product-id',
            type=int,
            help='ID específico de producto para reporte detallado',
        )
        parser.add_argument(
            '--export-csv',
            action='store_true',
            help='Exportar resultados a archivo CSV',
        )
        parser.add_argument(
            '--movement-type',
            choices=['sale', 'entry', 'return', 'adjustment', 'cancellation'],
            help='Filtrar por tipo específico de movimiento',
        )
        parser.add_argument(
            '--summary-only',
            action='store_true',
            help='Solo mostrar resumen, sin detalles',
        )

    def handle(self, *args, **options):
        days = options['days']
        product_id = options['product_id']
        export_csv = options['export_csv']
        movement_type = options['movement_type']
        summary_only = options['summary_only']
        
        # Fecha de inicio
        start_date = timezone.now() - timedelta(days=days)
        
        self.stdout.write(f'Generando reporte de stock para los últimos {days} días...')
        self.stdout.write(f'Desde: {start_date.strftime("%d/%m/%Y %H:%M")}')
        self.stdout.write(f'Hasta: {timezone.now().strftime("%d/%m/%Y %H:%M")}')
        
        # Filtros base
        filters = Q(created_at__gte=start_date)
        
        if product_id:
            filters &= Q(product_id=product_id)
        
        if movement_type:
            filters &= Q(movement_type=movement_type)
        
        movements = ProductStock.objects.filter(filters).order_by('-created_at')
        
        # Preparar datos para CSV si es necesario
        csv_data = []
        
        if not summary_only:
            self.stdout.write('\n' + '='*80)
            self.stdout.write('RESUMEN DE MOVIMIENTOS')
            self.stdout.write('='*80)
            
            # Resumen por tipo de movimiento
            movement_summary = movements.values('movement_type').annotate(
                total_movements=Count('id'),
                total_quantity=Sum('quantity')
            ).order_by('-total_movements')
            
            for summary in movement_summary:
                movement_type_display = dict(ProductStock.MOVEMENT_CHOICES).get(
                    summary['movement_type'], 
                    summary['movement_type']
                )
                self.stdout.write(
                    f"📊 {movement_type_display}: {summary['total_movements']} movimientos, "
                    f"Cantidad total: {summary['total_quantity'] or 0}"
                )
        
        # Reporte específico de producto
        if product_id:
            try:
                product = Product.objects.get(id=product_id)
                self.stdout.write('\n' + '='*80)
                self.stdout.write(f'REPORTE DETALLADO - {product.name}')
                self.stdout.write('='*80)
                self.stdout.write(f'Stock actual: {product.stock} unidades')
                
                product_movements = movements.filter(product=product)
                
                if product_movements.exists():
                    self.stdout.write(f'Total de movimientos en el período: {product_movements.count()}')
                    
                    # Calcular stock al inicio del período
                    movements_before = ProductStock.objects.filter(
                        product=product,
                        created_at__lt=start_date
                    ).order_by('-created_at').first()
                    
                    initial_stock = movements_before.new_stock if movements_before else 0
                    self.stdout.write(f'Stock al inicio del período: {initial_stock} unidades')
                    
                    # Cambio neto
                    net_change = product.stock - initial_stock
                    change_indicator = "📈" if net_change > 0 else "📉" if net_change < 0 else "➡️"
                    self.stdout.write(f'Cambio neto: {change_indicator} {net_change:+d} unidades')
                    
                    if not summary_only:
                        self.stdout.write('\nDetalle de movimientos:')
                        self.stdout.write('-' * 80)
                        
                        for movement in product_movements:
                            # Icono según tipo de movimiento
                            icons = {
                                'sale': '🛒',
                                'entry': '📦',
                                'return': '↩️',
                                'adjustment': '⚙️',
                                'cancellation': '❌'
                            }
                            icon = icons.get(movement.movement_type, '📝')
                            
                            self.stdout.write(
                                f"{icon} {movement.created_at.strftime('%d/%m %H:%M')} - "
                                f"{dict(ProductStock.MOVEMENT_CHOICES)[movement.movement_type]} - "
                                f"Cantidad: {movement.quantity:+d} - "
                                f"Stock: {movement.previous_stock} → {movement.new_stock}"
                            )
                            
                            if movement.reason:
                                self.stdout.write(f"   💬 {movement.reason}")
                            
                            if movement.reference:
                                self.stdout.write(f"   🔗 Ref: {movement.reference}")
                else:
                    self.stdout.write('No hay movimientos en el período especificado')
                    
            except Product.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'❌ Producto con ID {product_id} no encontrado')
                )
                return
        
        # Reporte general si no es producto específico
        elif not summary_only:
            self.stdout.write('\n' + '='*80)
            self.stdout.write('TOP 10 PRODUCTOS CON MÁS MOVIMIENTOS')
            self.stdout.write('='*80)
            
            top_products = movements.values('product__name', 'product__id').annotate(
                movement_count=Count('id'),
                total_quantity=Sum('quantity')
            ).order_by('-movement_count')[:10]
            
            for i, product_data in enumerate(top_products, 1):
                self.stdout.write(
                    f"{i:2d}. {product_data['product__name']} "
                    f"({product_data['movement_count']} movimientos, "
                    f"Cantidad total: {product_data['total_quantity'] or 0:+d})"
                )
        
        # Análisis de ventas vs devoluciones
        self.stdout.write('\n' + '='*80)
        self.stdout.write('ANÁLISIS DE VENTAS VS DEVOLUCIONES')
        self.stdout.write('='*80)
        
        sales = movements.filter(movement_type='sale')
        returns = movements.filter(movement_type='return')
        
        sales_count = sales.count()
        returns_count = returns.count()
        
        total_sold = abs(sales.aggregate(Sum('quantity'))['quantity__sum'] or 0)
        total_returned = returns.aggregate(Sum('quantity'))['quantity__sum'] or 0
        
        return_rate = (returns_count / sales_count * 100) if sales_count > 0 else 0
        
        self.stdout.write(f'📦 Ventas: {sales_count} operaciones, {total_sold} unidades')
        self.stdout.write(f'↩️  Devoluciones: {returns_count} operaciones, {total_returned} unidades')
        self.stdout.write(f'📊 Tasa de devolución: {return_rate:.1f}%')
        
        # Productos más vendidos
        if sales.exists():
            self.stdout.write('\n🏆 TOP 5 PRODUCTOS MÁS VENDIDOS:')
            self.stdout.write('-' * 50)
            
            top_sold = sales.values('product__name').annotate(
                units_sold=Sum('quantity')
            ).order_by('units_sold')[:5]  # quantity es negativo para ventas
            
            for i, product_data in enumerate(top_sold, 1):
                units = abs(product_data['units_sold'])
                self.stdout.write(f"{i}. {product_data['product__name']}: {units} unidades")
        
        # Exportar a CSV si se solicita
        if export_csv:
            self.export_to_csv(movements, days)
        
        # Alertas y recomendaciones
        self.stdout.write('\n' + '='*80)
        self.stdout.write('ALERTAS Y RECOMENDACIONES')
        self.stdout.write('='*80)
        
        # Productos sin movimientos
        active_products = Product.objects.filter(available=True)
        products_with_movements = movements.values_list('product_id', flat=True).distinct()
        stagnant_products = active_products.exclude(id__in=products_with_movements)
        
        if stagnant_products.exists():
            self.stdout.write(
                self.style.WARNING(
                    f'⚠️  {stagnant_products.count()} productos activos sin movimientos en {days} días:'
                )
            )
            for product in stagnant_products[:5]:  # Mostrar solo primeros 5
                self.stdout.write(f'   📦 {product.name} (Stock: {product.stock})')
            
            if stagnant_products.count() > 5:
                self.stdout.write(f'   ... y {stagnant_products.count() - 5} más')
        
        # Productos con alta rotación
        high_rotation = movements.values('product__name', 'product__stock').annotate(
            movement_count=Count('id')
        ).filter(movement_count__gte=10).order_by('-movement_count')
        
        if high_rotation.exists():
            self.stdout.write('\n🔥 PRODUCTOS CON ALTA ROTACIÓN (≥10 movimientos):')
            for product_data in high_rotation[:5]:
                self.stdout.write(
                    f"   📈 {product_data['product__name']} "
                    f"({product_data['movement_count']} movimientos, "
                    f"Stock actual: {product_data['product__stock']})"
                )
        
        self.stdout.write('\n' + '='*80)
        self.stdout.write(
            self.style.SUCCESS(f'✅ Reporte completado. Procesados {movements.count()} movimientos.')
        )

    def export_to_csv(self, movements, days):
        """Exporta los movimientos a un archivo CSV"""
        try:
            timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
            filename = f'stock_movements_{days}days_{timestamp}.csv'
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Headers
                writer.writerow([
                    'Fecha',
                    'Producto',
                    'Tipo de Movimiento',
                    'Cantidad',
                    'Stock Anterior',
                    'Stock Nuevo',
                    'Motivo',
                    'Referencia',
                    'Usuario'
                ])
                
                # Datos
                for movement in movements:
                    writer.writerow([
                        movement.created_at.strftime('%d/%m/%Y %H:%M:%S'),
                        movement.product.name,
                        dict(ProductStock.MOVEMENT_CHOICES)[movement.movement_type],
                        movement.quantity,
                        movement.previous_stock,
                        movement.new_stock,
                        movement.reason or '',
                        movement.reference or '',
                        movement.user.username if movement.user else 'Sistema'
                    ])
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Datos exportados a: {filename}')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error exportando CSV: {str(e)}')
            )
