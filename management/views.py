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
    template_name = 'management/coupon/form.html'
    fields = [
        'code', 'name', 'description', 'discount_type', 'discount_value',
        'minimum_order_amount', 'maximum_discount_amount', 'usage_type',
        'max_uses', 'valid_from', 'valid_until', 'is_active'
    ]
    success_url = reverse_lazy('management:coupon_management')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, f'Cupón "{form.instance.code}" creado exitosamente.')
        return super().form_valid(form)


class CouponUpdateView(SuperuserRequiredMixin, UpdateView):
    """Editar cupón de descuento"""
    model = DiscountCoupon
    template_name = 'management/coupon/form.html'
    fields = [
        'code', 'name', 'description', 'discount_type', 'discount_value',
        'minimum_order_amount', 'maximum_discount_amount', 'usage_type',
        'max_uses', 'valid_from', 'valid_until', 'is_active'
    ]
    success_url = reverse_lazy('management:coupon_management')
    
    def form_valid(self, form):
        messages.success(self.request, f'Cupón "{form.instance.code}" actualizado exitosamente.')
        return super().form_valid(form)


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
        
        context.update({
            'critical_stock': Product.objects.filter(stock__lte=5),
            'low_stock': Product.objects.filter(stock__lte=10, stock__gt=5),
            'out_of_stock': Product.objects.filter(stock=0),
        })
        
        return context


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
