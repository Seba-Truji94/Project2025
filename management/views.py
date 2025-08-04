"""
Vistas para el módulo de gestión empresarial
Solo accesible para superusuarios
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import (
    TemplateView, ListView, CreateView, UpdateView, DeleteView, View
)
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.db.models import Sum, Count, Q, Avg
from django.urls import reverse_lazy
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone

from .decorators import SuperuserRequiredMixin
from .forms import CouponForm
from shop.models import (
    Product, Category, TaxConfiguration, DiscountCoupon, CouponUsage,
    ProductStock, Supplier, ProductSupplier
)


class ManagementDashboardView(SuperuserRequiredMixin, TemplateView):
    """Dashboard principal del módulo de gestión"""
    template_name = 'management/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estadísticas generales
        context.update({
            'total_products': Product.objects.count(),
            'active_products': Product.objects.filter(available=True).count(),
            'total_suppliers': Supplier.objects.filter(is_active=True).count(),
            'active_coupons': DiscountCoupon.objects.filter(is_active=True).count(),
            'tax_configurations': TaxConfiguration.objects.filter(is_active=True).count(),
            
            # Productos con stock bajo
            'low_stock_products': Product.objects.filter(stock__lte=10).count(),
            
            # Cupones por expirar
            'expiring_coupons': DiscountCoupon.objects.filter(
                valid_until__lte=timezone.now() + timedelta(days=7),
                is_active=True
            ).count(),
            
            # Productos sin proveedor principal
            'products_without_supplier': Product.objects.filter(
                supplier_info__isnull=True
            ).count(),
            
            # Últimos movimientos de stock
            'recent_stock_movements': ProductStock.objects.select_related(
                'product'
            ).order_by('-created_at')[:5],
            
            # Año actual para el footer
            'current_year': timezone.now().year,
        })
        
        return context


class APIStatisticsView(SuperuserRequiredMixin, View):
    """Vista API para estadísticas del dashboard"""
    
    def get(self, request):
        data = {
            'total_products': Product.objects.count(),
            'active_products': Product.objects.filter(available=True).count(),
            'total_suppliers': Supplier.objects.filter(is_active=True).count(),
            'active_coupons': DiscountCoupon.objects.filter(is_active=True).count(),
            'tax_configurations': TaxConfiguration.objects.filter(is_active=True).count(),
            'low_stock_products': Product.objects.filter(stock__lte=10).count(),
            'timestamp': timezone.now().isoformat(),
        }
        return JsonResponse(data)


class StockAlertsView(SuperuserRequiredMixin, ListView):
    """Vista para productos con stock bajo"""
    model = Product
    template_name = 'management/stock/alerts.html'
    context_object_name = 'low_stock_products'
    
    def get_queryset(self):
        return Product.objects.filter(stock__lte=10).order_by('stock')


# ===== GESTIÓN DE IMPUESTOS =====

class TaxManagementView(SuperuserRequiredMixin, ListView):
    """Vista de gestión de configuraciones de impuesto"""
    model = TaxConfiguration
    template_name = 'management/tax/management.html'
    context_object_name = 'tax_configurations'
    paginate_by = 20
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estadísticas para la vista de impuestos
        context.update({
            'total_configurations': TaxConfiguration.objects.count(),
            'active_configurations': TaxConfiguration.objects.filter(is_active=True).count(),
            'average_rate': TaxConfiguration.objects.filter(is_active=True).aggregate(
                avg_rate=Avg('rate')
            )['avg_rate'] or 0,
            'unique_countries': 1,  # Por ahora solo Chile, ya que no hay campo country
        })
        
        return context


class TaxCreateView(SuperuserRequiredMixin, View):
    """Crear nueva configuración de impuesto"""
    
    def post(self, request):
        try:
            # Crear nueva configuración de impuesto
            tax_config = TaxConfiguration.objects.create(
                name=request.POST.get('name'),
                rate=float(request.POST.get('rate', 0)),
                applies_to_shipping=request.POST.get('applies_to_shipping') == 'on',
                is_active=request.POST.get('is_active') == 'on'
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Configuración de impuesto "{tax_config.name}" creada exitosamente.',
                'id': tax_config.id
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)


class TaxUpdateView(SuperuserRequiredMixin, View):
    """Editar configuración de impuesto"""
    
    def get(self, request, pk):
        try:
            tax_config = get_object_or_404(TaxConfiguration, pk=pk)
            return JsonResponse({
                'id': tax_config.id,
                'name': tax_config.name,
                'rate': float(tax_config.rate),
                'applies_to_shipping': tax_config.applies_to_shipping,
                'is_active': tax_config.is_active,
            })
        except TaxConfiguration.DoesNotExist:
            return JsonResponse({'error': 'Configuración no encontrada'}, status=404)
    
    def post(self, request, pk):
        try:
            tax_config = get_object_or_404(TaxConfiguration, pk=pk)
            
            # Actualizar campos
            tax_config.name = request.POST.get('name')
            tax_config.rate = float(request.POST.get('rate', 0))
            tax_config.applies_to_shipping = request.POST.get('applies_to_shipping') == 'on'
            tax_config.is_active = request.POST.get('is_active') == 'on'
            tax_config.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Configuración de impuesto "{tax_config.name}" actualizada exitosamente.'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)


class TaxDeleteView(SuperuserRequiredMixin, View):
    """Eliminar configuración de impuesto"""
    
    def post(self, request, pk):
        try:
            tax_config = get_object_or_404(TaxConfiguration, pk=pk)
            name = tax_config.name
            tax_config.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'Configuración de impuesto "{name}" eliminada exitosamente.'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)


class TaxToggleView(SuperuserRequiredMixin, View):
    """Activar/Desactivar configuración de impuesto"""
    
    def post(self, request, pk):
        try:
            tax_config = get_object_or_404(TaxConfiguration, pk=pk)
            is_active = request.POST.get('is_active') == 'true'
            tax_config.is_active = is_active
            tax_config.save()
            
            status = 'activada' if is_active else 'desactivada'
            return JsonResponse({
                'success': True,
                'message': f'Configuración de impuesto "{tax_config.name}" {status} exitosamente.'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(request, f'Configuración de impuesto "{obj.name}" eliminada exitosamente.')
        return super().delete(request, *args, **kwargs)


# ===== GESTIÓN DE CUPONES =====

class CouponManagementView(SuperuserRequiredMixin, ListView):
    """Vista de gestión de cupones de descuento"""
    model = DiscountCoupon
    template_name = 'management/coupon/list.html'
    context_object_name = 'coupons'
    paginate_by = 20
    
    def get_queryset(self):
        return DiscountCoupon.objects.select_related('created_by').order_by('-created_at')


class CouponCreateView(SuperuserRequiredMixin, CreateView):
    """Crear nuevo cupón de descuento"""
    model = DiscountCoupon
    form_class = CouponForm
    template_name = 'management/coupon/form.html'
    success_url = reverse_lazy('management:coupon_management')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, f'Cupón "{form.instance.code}" creado exitosamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        """Manejar errores de validación"""
        messages.error(
            self.request,
            'Por favor corrige los errores en el formulario.'
        )
        return super().form_invalid(form)


class CouponUpdateView(SuperuserRequiredMixin, UpdateView):
    """Editar cupón de descuento"""
    model = DiscountCoupon
    form_class = CouponForm
    template_name = 'management/coupon/form.html'
    success_url = reverse_lazy('management:coupon_management')
    
    def form_valid(self, form):
        messages.success(self.request, f'Cupón "{form.instance.code}" actualizado exitosamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        """Manejar errores de validación"""
        messages.error(
            self.request,
            'Por favor corrige los errores en el formulario.'
        )
        return super().form_invalid(form)


class CouponDeleteView(SuperuserRequiredMixin, DeleteView):
    """Eliminar cupón de descuento"""
    model = DiscountCoupon
    template_name = 'management/coupon/delete.html'
    success_url = reverse_lazy('management:coupon_management')
    
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(request, f'Cupón "{obj.code}" eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)


class CouponToggleView(SuperuserRequiredMixin, View):
    """Activar/desactivar cupón vía AJAX"""
    
    def post(self, request, pk):
        coupon = get_object_or_404(DiscountCoupon, pk=pk)
        coupon.is_active = not coupon.is_active
        coupon.save()
        
        return JsonResponse({
            'success': True,
            'is_active': coupon.is_active,
            'message': f'Cupón {coupon.code} {"activado" if coupon.is_active else "desactivado"} exitosamente.'
        })


# ===== GESTIÓN DE PROVEEDORES =====

class SupplierManagementView(SuperuserRequiredMixin, ListView):
    """Vista de gestión de proveedores"""
    model = Supplier
    template_name = 'management/supplier/list.html'
    context_object_name = 'suppliers'
    paginate_by = 20


class SupplierCreateView(SuperuserRequiredMixin, CreateView):
    """Crear nuevo proveedor"""
    model = Supplier
    template_name = 'management/supplier/form.html'
    fields = [
        'name', 'contact_person', 'email', 'phone', 'address', 'city',
        'tax_id', 'rating', 'is_active', 'notes'
    ]
    success_url = reverse_lazy('management:supplier_management')
    
    def form_valid(self, form):
        messages.success(self.request, f'Proveedor "{form.instance.name}" creado exitosamente.')
        return super().form_valid(form)


class SupplierUpdateView(SuperuserRequiredMixin, UpdateView):
    """Editar proveedor"""
    model = Supplier
    template_name = 'management/supplier/form.html'
    fields = [
        'name', 'contact_person', 'email', 'phone', 'address', 'city',
        'tax_id', 'rating', 'is_active', 'notes'
    ]
    success_url = reverse_lazy('management:supplier_management')
    
    def form_valid(self, form):
        messages.success(self.request, f'Proveedor "{form.instance.name}" actualizado exitosamente.')
        return super().form_valid(form)


class SupplierDeleteView(SuperuserRequiredMixin, DeleteView):
    """Eliminar proveedor"""
    model = Supplier
    template_name = 'management/supplier/delete.html'
    success_url = reverse_lazy('management:supplier_management')
    
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(request, f'Proveedor "{obj.name}" eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)


class SupplierProductsView(SuperuserRequiredMixin, TemplateView):
    """Ver productos de un proveedor específico"""
    template_name = 'management/supplier/products.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        supplier = get_object_or_404(Supplier, pk=kwargs['pk'])
        
        context.update({
            'supplier': supplier,
            'product_relations': ProductSupplier.objects.filter(
                supplier=supplier
            ).select_related('product'),
        })
        
        return context


# ===== GESTIÓN DE STOCK =====

class StockManagementView(SuperuserRequiredMixin, ListView):
    """Vista de gestión de stock"""
    model = ProductStock
    template_name = 'management/stock/list.html'
    context_object_name = 'stock_movements'
    paginate_by = 50
    
    def get_queryset(self):
        return ProductStock.objects.select_related('product').order_by('-created_at')


class StockMovementCreateView(SuperuserRequiredMixin, CreateView):
    """Crear movimiento de stock"""
    model = ProductStock
    template_name = 'management/stock/form.html'
    fields = ['product', 'movement_type', 'quantity', 'reason', 'reference']
    success_url = reverse_lazy('management:stock_management')
    
    def get_initial(self):
        """Preseleccionar producto si se pasa en la URL"""
        initial = super().get_initial()
        product_id = self.request.GET.get('product')
        if product_id:
            try:
                product = Product.objects.get(id=product_id)
                initial['product'] = product
            except Product.DoesNotExist:
                pass
        return initial
    
    def get_context_data(self, **kwargs):
        """Agregar contexto adicional"""
        context = super().get_context_data(**kwargs)
        product_id = self.request.GET.get('product')
        if product_id:
            try:
                product = Product.objects.get(id=product_id)
                context['preselected_product'] = product
            except Product.DoesNotExist:
                pass
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Movimiento de stock registrado exitosamente.')
        return super().form_valid(form)


class StockReportView(SuperuserRequiredMixin, TemplateView):
    """Reporte de stock"""
    template_name = 'management/stock/report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Productos con stock bajo
        low_stock = Product.objects.filter(stock__lte=10)
        
        # Productos sin stock
        no_stock = Product.objects.filter(stock=0)
        
        # Movimientos recientes
        recent_movements = ProductStock.objects.select_related(
            'product'
        ).order_by('-created_at')[:20]
        
        context.update({
            'low_stock_products': low_stock,
            'no_stock_products': no_stock,
            'recent_movements': recent_movements,
            'total_products': Product.objects.count(),
            'products_in_stock': Product.objects.filter(stock__gt=0).count(),
        })
        
        return context


class StockAlertsView(SuperuserRequiredMixin, TemplateView):
    """Alertas de stock"""
    template_name = 'management/stock/alerts.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Filtros desde la URL
        alert_type = self.request.GET.get('alert_type', '')
        category_id = self.request.GET.get('category', '')
        priority = self.request.GET.get('priority', '')
        
        # Productos base con stock
        products = Product.objects.filter(available=True).select_related('category')
        
        # Aplicar filtro por categoría si existe
        if category_id:
            products = products.filter(category_id=category_id)
        
        # Obtener productos críticos, con stock bajo y sin stock
        critical_stock = products.filter(stock__lte=5, stock__gt=0)
        low_stock = products.filter(stock__lte=20, stock__gt=5)
        out_of_stock = products.filter(stock=0)
        
        # Crear lista de alertas con información detallada
        alerts = []
        
        # Alertas críticas (stock ≤ 5)
        for product in critical_stock:
            alerts.append({
                'product': product,
                'type': 'critical',
                'priority': 'high' if product.stock <= 2 else 'medium',
                'current_stock': product.stock,
                'minimum_stock': 5,
                'recommended_order': max(50, product.stock * 10),
                'days_out': 0,
            })
        
        # Alertas de stock bajo (stock ≤ 20)
        for product in low_stock:
            alerts.append({
                'product': product,
                'type': 'low',
                'priority': 'medium' if product.stock <= 10 else 'low',
                'current_stock': product.stock,
                'minimum_stock': 20,
                'recommended_order': max(30, product.stock * 5),
                'days_out': 0,
            })
        
        # Alertas sin stock
        for product in out_of_stock:
            alerts.append({
                'product': product,
                'type': 'out',
                'priority': 'high',
                'current_stock': 0,
                'minimum_stock': 20,
                'recommended_order': 100,
                'days_out': 1,  # Esto se podría calcular basado en la última venta
            })
        
        # Aplicar filtros adicionales
        if alert_type:
            alerts = [alert for alert in alerts if alert['type'] == alert_type]
        
        if priority:
            alerts = [alert for alert in alerts if alert['priority'] == priority]
        
        # Ordenar por prioridad y luego por stock
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        alerts.sort(key=lambda x: (priority_order[x['priority']], x['current_stock']))
        
        # Estadísticas
        critical_alerts = len([a for a in alerts if a['type'] == 'critical'])
        low_stock_alerts = len([a for a in alerts if a['type'] == 'low'])
        out_of_stock_alerts = len([a for a in alerts if a['type'] == 'out'])
        
        context.update({
            'alerts': alerts,
            'critical_alerts': critical_alerts,
            'low_stock_alerts': low_stock_alerts,
            'out_of_stock': out_of_stock_alerts,
            'total_alerts': len(alerts),
            'categories': Category.objects.all(),
        })
        
        return context


class StockAlertsAPIView(SuperuserRequiredMixin, View):
    """API para obtener alertas de stock en tiempo real"""
    
    def get(self, request, *args, **kwargs):
        # Filtros desde la URL
        alert_type = request.GET.get('alert_type', '')
        category_id = request.GET.get('category', '')
        priority = request.GET.get('priority', '')
        
        # Productos base con stock
        products = Product.objects.filter(available=True).select_related('category')
        
        # Aplicar filtro por categoría si existe
        if category_id:
            products = products.filter(category_id=category_id)
        
        # Obtener productos críticos, con stock bajo y sin stock
        critical_stock = products.filter(stock__lte=5, stock__gt=0)
        low_stock = products.filter(stock__lte=20, stock__gt=5)
        out_of_stock = products.filter(stock=0)
        
        # Crear lista de alertas con información detallada
        alerts = []
        
        # Alertas críticas (stock ≤ 5)
        for product in critical_stock:
            alerts.append({
                'id': product.id,
                'name': product.name,
                'sku': f'PRD-{product.id:04d}',  # Crear SKU basado en ID
                'category': product.category.name if product.category else 'Sin categoría',
                'image_url': product.image.url if product.image else None,
                'type': 'critical',
                'priority': 'high' if product.stock <= 2 else 'medium',
                'current_stock': product.stock,
                'minimum_stock': 5,
                'recommended_order': max(50, product.stock * 10),
                'days_out': 0,
                'last_updated': timezone.now().isoformat(),
            })
        
        # Alertas de stock bajo (stock ≤ 20)
        for product in low_stock:
            alerts.append({
                'id': product.id,
                'name': product.name,
                'sku': f'PRD-{product.id:04d}',  # Crear SKU basado en ID
                'category': product.category.name if product.category else 'Sin categoría',
                'image_url': product.image.url if product.image else None,
                'type': 'low',
                'priority': 'medium' if product.stock <= 10 else 'low',
                'current_stock': product.stock,
                'minimum_stock': 20,
                'recommended_order': max(30, product.stock * 5),
                'days_out': 0,
                'last_updated': timezone.now().isoformat(),
            })
        
        # Alertas sin stock
        for product in out_of_stock:
            alerts.append({
                'id': product.id,
                'name': product.name,
                'sku': f'PRD-{product.id:04d}',  # Crear SKU basado en ID
                'category': product.category.name if product.category else 'Sin categoría',
                'image_url': product.image.url if product.image else None,
                'type': 'out',
                'priority': 'high',
                'current_stock': 0,
                'minimum_stock': 20,
                'recommended_order': 100,
                'days_out': 1,
                'last_updated': timezone.now().isoformat(),
            })
        
        # Aplicar filtros adicionales
        if alert_type:
            alerts = [alert for alert in alerts if alert['type'] == alert_type]
        
        if priority:
            alerts = [alert for alert in alerts if alert['priority'] == priority]
        
        # Ordenar por prioridad y luego por stock
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        alerts.sort(key=lambda x: (priority_order[x['priority']], x['current_stock']))
        
        # Estadísticas
        critical_alerts = len([a for a in alerts if a['type'] == 'critical'])
        low_stock_alerts = len([a for a in alerts if a['type'] == 'low'])
        out_of_stock_alerts = len([a for a in alerts if a['type'] == 'out'])
        
        return JsonResponse({
            'success': True,
            'data': {
                'alerts': alerts,
                'statistics': {
                    'critical_alerts': critical_alerts,
                    'low_stock_alerts': low_stock_alerts,
                    'out_of_stock': out_of_stock_alerts,
                    'total_alerts': len(alerts),
                },
                'last_updated': timezone.now().isoformat(),
            }
        })


# ===== RELACIONES PRODUCTO-PROVEEDOR =====

class ProductSupplierManagementView(SuperuserRequiredMixin, ListView):
    """Vista de gestión de relaciones producto-proveedor"""
    model = ProductSupplier
    template_name = 'management/relations/list.html'
    context_object_name = 'relations'
    paginate_by = 20
    
    def get_queryset(self):
        return ProductSupplier.objects.select_related('product', 'supplier')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Agregar datos necesarios para el modal
        context['suppliers'] = Supplier.objects.filter(is_active=True).order_by('name')
        context['products'] = Product.objects.filter(available=True).order_by('name')
        
        # Agregar estadísticas
        relations = ProductSupplier.objects.all()
        context['total_relations'] = relations.count()
        context['primary_relations'] = relations.filter(is_primary=True).count()
        
        return context


class ProductSupplierCreateView(SuperuserRequiredMixin, CreateView):
    """Crear relación producto-proveedor"""
    model = ProductSupplier
    template_name = 'management/relations/form.html'
    fields = [
        'product', 'supplier', 'supplier_sku', 'cost_price', 
        'minimum_order_quantity', 'lead_time_days', 'is_primary'
    ]
    success_url = reverse_lazy('management:relations_management')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Relación producto-proveedor creada exitosamente.')
        
        # Si es una petición AJAX, devolver JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Relación creada exitosamente',
                'relation_id': self.object.id
            })
        
        return response
    
    def form_invalid(self, form):
        # Si es una petición AJAX, devolver errores en JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'Error en el formulario',
                'errors': form.errors
            })
        
        return super().form_invalid(form)


class ProductSupplierUpdateView(SuperuserRequiredMixin, UpdateView):
    """Editar relación producto-proveedor"""
    model = ProductSupplier
    template_name = 'management/relations/form.html'
    fields = [
        'product', 'supplier', 'supplier_sku', 'cost_price', 
        'minimum_order_quantity', 'lead_time_days', 'is_primary'
    ]
    success_url = reverse_lazy('management:relations_management')
    
    def form_valid(self, form):
        messages.success(self.request, 'Relación producto-proveedor actualizada exitosamente.')
        return super().form_valid(form)


class ProductSupplierDeleteView(SuperuserRequiredMixin, DeleteView):
    """Eliminar relación producto-proveedor"""
    model = ProductSupplier
    template_name = 'management/relations/delete.html'
    success_url = reverse_lazy('management:relations_management')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Relación producto-proveedor eliminada exitosamente.')
        return super().delete(request, *args, **kwargs)


# ===== REPORTES =====

class ReportsView(SuperuserRequiredMixin, TemplateView):
    """Vista principal de reportes"""
    template_name = 'management/reports/dashboard.html'


class SalesReportView(SuperuserRequiredMixin, TemplateView):
    """Reporte de ventas"""
    template_name = 'management/reports/sales.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Aquí agregarías lógica de reportes de ventas cuando tengas el modelo Order
        return context


class ProductReportView(SuperuserRequiredMixin, TemplateView):
    """Reporte de productos"""
    template_name = 'management/reports/products.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context.update({
            'total_products': Product.objects.count(),
            'active_products': Product.objects.filter(available=True).count(),
            'featured_products': Product.objects.filter(featured=True).count(),
            'products_by_category': Category.objects.annotate(
                product_count=Count('products')
            ),
        })
        
        return context


class MarginsReportView(SuperuserRequiredMixin, TemplateView):
    """Reporte de márgenes de ganancia"""
    template_name = 'management/reports/margins.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Productos con relaciones de proveedor
        products_with_suppliers = ProductSupplier.objects.select_related(
            'product', 'supplier'
        ).filter(is_primary=True)
        
        context.update({
            'product_margins': products_with_suppliers,
        })
        
        return context


# ===== APIs para AJAX =====

class ProductsAPIView(SuperuserRequiredMixin, View):
    """API para obtener productos vía AJAX"""
    
    def get(self, request):
        search = request.GET.get('search', '')
        products = Product.objects.filter(
            Q(name__icontains=search) | Q(sku__icontains=search)
        )[:10]
        
        data = [{
            'id': p.id,
            'name': p.name,
            'sku': p.sku if hasattr(p, 'sku') else '',
            'price': str(p.price),
            'stock': p.stock,
        } for p in products]
        
        return JsonResponse({'products': data})


class StatisticsAPIView(SuperuserRequiredMixin, View):
    """API para estadísticas del dashboard"""
    
    def get(self, request):
        stats = {
            'total_products': Product.objects.count(),
            'active_products': Product.objects.filter(available=True).count(),
            'total_suppliers': Supplier.objects.filter(is_active=True).count(),
            'active_coupons': DiscountCoupon.objects.filter(is_active=True).count(),
            'low_stock_alert': Product.objects.filter(stock__lte=10).count(),
        }
        
        return JsonResponse(stats)


class StockMovementDetailView(SuperuserRequiredMixin, View):
    """API para obtener detalles de un movimiento de stock"""
    
    def get(self, request, movement_id):
        try:
            movement = ProductStock.objects.select_related('product', 'user').get(id=movement_id)
            
            data = {
                'id': movement.id,
                'product': {
                    'id': movement.product.id,
                    'name': movement.product.name,
                    'current_stock': movement.product.stock,
                    'category': movement.product.category.name if movement.product.category else 'Sin categoría'
                },
                'movement_type': movement.get_movement_type_display(),
                'movement_type_code': movement.movement_type,
                'quantity': movement.quantity,
                'previous_stock': movement.previous_stock,
                'new_stock': movement.new_stock,
                'reason': movement.reason or 'Sin motivo especificado',
                'reference': movement.reference or 'Sin referencia',
                'created_at': movement.created_at.strftime('%d/%m/%Y %H:%M:%S'),
                'user': movement.user.username if movement.user else 'Sistema',
                'user_full_name': movement.user.get_full_name() if movement.user and movement.user.get_full_name() else (movement.user.username if movement.user else 'Sistema'),
                'impact': {
                    'change': movement.quantity,
                    'percentage': round((abs(movement.quantity) / movement.previous_stock * 100), 2) if movement.previous_stock > 0 else 0,
                    'direction': 'increase' if movement.quantity > 0 else 'decrease' if movement.quantity < 0 else 'neutral'
                }
            }
            
            return JsonResponse({
                'success': True,
                'data': data
            })
            
        except ProductStock.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Movimiento no encontrado'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


class StockHistoryView(SuperuserRequiredMixin, TemplateView):
    """Vista para mostrar el historial de movimientos de stock de un producto"""
    template_name = 'management/stock/history.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product_id = kwargs.get('product_id')
        
        try:
            # Obtener el producto
            product = get_object_or_404(Product, id=product_id)
            context['product'] = product
            
            # Obtener historial de movimientos
            movements = ProductStock.objects.filter(
                product=product
            ).select_related('user').order_by('-created_at')
            
            context['movements'] = movements
            
            # Estadísticas del historial
            context['stats'] = {
                'total_movements': movements.count(),
                'total_inbound': movements.filter(movement_type='entry').aggregate(
                    total=Sum('quantity')
                )['total'] or 0,
                'total_outbound': movements.filter(movement_type='exit').aggregate(
                    total=Sum('quantity')  
                )['total'] or 0,
                'total_adjustments': movements.filter(movement_type='adjustment').count(),
                'current_stock': product.stock,
                'minimum_stock': product.minimum_stock if hasattr(product, 'minimum_stock') else 0,
            }
            
            # Calcular valor total del inventario histórico
            if hasattr(product, 'price'):
                context['stats']['current_value'] = product.stock * product.price
            
            # Obtener categoría del producto
            if product.category:
                context['category'] = product.category
                
        except Product.DoesNotExist:
            context['error'] = 'Producto no encontrado'
            context['product'] = None
            context['movements'] = []
            context['stats'] = {}
            
        return context
