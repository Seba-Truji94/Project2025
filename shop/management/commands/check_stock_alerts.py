from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from shop.models import Product, ProductStock
from orders.models import Order
from datetime import datetime, timedelta
from django.utils import timezone


class Command(BaseCommand):
    help = 'Verifica y reporta alertas de stock bajo'

    def add_arguments(self, parser):
        parser.add_argument(
            '--send-email',
            action='store_true',
            help='Envía alertas por email (requiere configuración de email)',
        )
        parser.add_argument(
            '--critical-only',
            action='store_true',
            help='Solo mostrar productos con stock crítico (≤5 o agotados)',
        )
        parser.add_argument(
            '--create-movements',
            action='store_true',
            help='Crear movimientos de stock para alertas registradas',
        )

    def handle(self, *args, **options):
        send_email = options['send_email']
        critical_only = options['critical_only']
        create_movements = options['create_movements']
        
        self.stdout.write('Verificando alertas de stock...')
        
        # Definir umbrales
        CRITICAL_THRESHOLD = 5
        LOW_THRESHOLD = 10
        
        # Obtener productos según filtros
        if critical_only:
            critical_products = Product.objects.filter(
                stock__lte=CRITICAL_THRESHOLD,
                available=True
            ).order_by('stock', 'name')
            low_products = Product.objects.none()
        else:
            critical_products = Product.objects.filter(
                stock__lte=CRITICAL_THRESHOLD,
                available=True
            ).order_by('stock', 'name')
            low_products = Product.objects.filter(
                stock__gt=CRITICAL_THRESHOLD,
                stock__lte=LOW_THRESHOLD,
                available=True
            ).order_by('stock', 'name')
        
        out_of_stock = critical_products.filter(stock=0)
        critical_stock = critical_products.filter(stock__gt=0, stock__lte=CRITICAL_THRESHOLD)
        
        # Estadísticas generales
        total_products = Product.objects.filter(available=True).count()
        good_stock = total_products - critical_products.count() - low_products.count()
        
        # Mostrar resumen
        self.stdout.write('\n' + '='*60)
        self.stdout.write('REPORTE DE ESTADO DE STOCK')
        self.stdout.write('='*60)
        self.stdout.write(f'Total de productos activos: {total_products}')
        self.stdout.write(f'Productos con buen stock (>{LOW_THRESHOLD}): {good_stock}')
        
        if not critical_only:
            self.stdout.write(
                self.style.WARNING(
                    f'Productos con stock bajo ({CRITICAL_THRESHOLD+1}-{LOW_THRESHOLD}): {low_products.count()}'
                )
            )
        
        self.stdout.write(
            self.style.ERROR(f'Productos con stock crítico (1-{CRITICAL_THRESHOLD}): {critical_stock.count()}')
        )
        self.stdout.write(
            self.style.ERROR(f'Productos agotados (0): {out_of_stock.count()}')
        )
        
        # Mostrar productos agotados
        if out_of_stock.exists():
            self.stdout.write('\n' + '🔴 PRODUCTOS AGOTADOS:')
            self.stdout.write('-' * 40)
            for product in out_of_stock:
                self.stdout.write(f'❌ {product.name} - Categoría: {product.category.name}')
                
                if create_movements:
                    ProductStock.objects.create(
                        product=product,
                        movement_type='adjustment',
                        quantity=0,
                        previous_stock=0,
                        new_stock=0,
                        reason='Alerta automática: Producto agotado',
                        reference=f'ALERT-{timezone.now().strftime("%Y%m%d-%H%M%S")}',
                        user=None
                    )
        
        # Mostrar productos con stock crítico
        if critical_stock.exists():
            self.stdout.write('\n' + '⚠️  PRODUCTOS CON STOCK CRÍTICO:')
            self.stdout.write('-' * 40)
            for product in critical_stock:
                self.stdout.write(f'⚡ {product.name} - Stock: {product.stock} - Categoría: {product.category.name}')
                
                if create_movements:
                    ProductStock.objects.create(
                        product=product,
                        movement_type='adjustment',
                        quantity=0,
                        previous_stock=product.stock,
                        new_stock=product.stock,
                        reason=f'Alerta automática: Stock crítico ({product.stock} unidades)',
                        reference=f'ALERT-{timezone.now().strftime("%Y%m%d-%H%M%S")}',
                        user=None
                    )
        
        # Mostrar productos con stock bajo (si no es solo crítico)
        if low_products.exists() and not critical_only:
            self.stdout.write('\n' + '📉 PRODUCTOS CON STOCK BAJO:')
            self.stdout.write('-' * 40)
            for product in low_products:
                self.stdout.write(f'📦 {product.name} - Stock: {product.stock} - Categoría: {product.category.name}')
        
        # Análisis de ventas recientes
        self.stdout.write('\n' + '📊 ANÁLISIS DE VENTAS RECIENTES (últimos 7 días):')
        self.stdout.write('-' * 50)
        
        recent_sales = ProductStock.objects.filter(
            movement_type='sale',
            created_at__gte=timezone.now() - timedelta(days=7)
        ).values('product').distinct()
        
        if recent_sales.exists():
            for sale in recent_sales:
                product = Product.objects.get(pk=sale['product'])
                recent_movements = ProductStock.objects.filter(
                    product=product,
                    movement_type='sale',
                    created_at__gte=timezone.now() - timedelta(days=7)
                )
                total_sold = sum(abs(m.quantity) for m in recent_movements)
                
                if product.stock <= CRITICAL_THRESHOLD or total_sold >= product.stock:
                    status = "🔥 URGENTE" if product.stock <= CRITICAL_THRESHOLD else "⚠️  MONITOREAR"
                    self.stdout.write(
                        f'{status} {product.name}: Vendido {total_sold} unidades, '
                        f'Stock actual: {product.stock}'
                    )
        else:
            self.stdout.write('No hay ventas registradas en los últimos 7 días')
        
        # Recomendaciones de reabastecimiento
        if critical_products.exists() or low_products.exists():
            self.stdout.write('\n' + '💡 RECOMENDACIONES DE REABASTECIMIENTO:')
            self.stdout.write('-' * 50)
            
            # Productos más críticos primero
            all_alert_products = list(critical_products) + list(low_products)
            
            for product in all_alert_products[:10]:  # Top 10 más críticos
                # Calcular sugerencia de reabastecimiento basada en ventas
                recent_sales_qty = ProductStock.objects.filter(
                    product=product,
                    movement_type='sale',
                    created_at__gte=timezone.now() - timedelta(days=30)
                ).count()
                
                if recent_sales_qty > 0:
                    monthly_avg = recent_sales_qty
                    suggested_order = max(50, monthly_avg * 2)  # Al menos 50 o 2 meses de inventario
                else:
                    suggested_order = 50  # Cantidad base
                
                priority = "🔥 ALTA" if product.stock <= CRITICAL_THRESHOLD else "📝 MEDIA"
                
                self.stdout.write(
                    f'{priority} {product.name}: Ordenar {suggested_order} unidades '
                    f'(Ventas mensuales aprox: {recent_sales_qty})'
                )
        
        # Enviar email si está configurado
        if send_email and (critical_products.exists() or low_products.exists()):
            self.send_stock_alert_email(critical_products, low_products, out_of_stock)
        
        # Mensaje de confirmación
        if create_movements:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✓ Se crearon {critical_products.count()} movimientos de alerta en el sistema'
                )
            )
        
        self.stdout.write('\n' + '='*60)
        if critical_products.exists():
            self.stdout.write(
                self.style.ERROR('⚠️  ACCIÓN REQUERIDA: Hay productos que necesitan reabastecimiento urgente')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('✅ Todos los productos tienen stock adecuado')
            )
        
        self.stdout.write('Comando completado.')

    def send_stock_alert_email(self, critical_products, low_products, out_of_stock):
        """Envía email con alertas de stock"""
        try:
            subject = f'🚨 Alerta de Stock - {out_of_stock.count()} agotados, {critical_products.count()} críticos'
            
            message = f"""
            ALERTA DE STOCK - {timezone.now().strftime('%d/%m/%Y %H:%M')}
            
            PRODUCTOS AGOTADOS ({out_of_stock.count()}):
            """
            
            for product in out_of_stock:
                message += f"\n❌ {product.name}"
            
            message += f"\n\nPRODUCTOS CON STOCK CRÍTICO ({critical_products.filter(stock__gt=0).count()}):"
            
            for product in critical_products.filter(stock__gt=0):
                message += f"\n⚠️  {product.name}: {product.stock} unidades"
            
            message += f"\n\nPRODUCTOS CON STOCK BAJO ({low_products.count()}):"
            
            for product in low_products:
                message += f"\n📦 {product.name}: {product.stock} unidades"
            
            message += "\n\nRevisa el panel de administración para tomar acciones."
            
            # Usar configuración de email de Django
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],  # Cambiar por emails de administradores
                fail_silently=False,
            )
            
            self.stdout.write(
                self.style.SUCCESS('✅ Email de alerta enviado exitosamente')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error enviando email: {str(e)}')
            )
