from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.db.models import Q, Sum, Count
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import path, reverse
from django.utils import timezone
from django.contrib import messages
from django.db import transaction
from .models import (
    Category, Product, ProductImage, Review, TaxConfiguration,
    DiscountCoupon, CouponUsage, ProductStock, Supplier, ProductSupplier
)
import csv
from datetime import datetime, timedelta

class LowStockFilter(admin.SimpleListFilter):
    title = 'Estado de Stock'
    parameter_name = 'stock_status'

    def lookups(self, request, model_admin):
        return (
            ('low', 'Stock Bajo (≤ 10)'),
            ('out', 'Agotado (0)'),
            ('available', 'Con Stock (> 10)'),
            ('critical', 'Crítico (≤ 5)'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'low':
            return queryset.filter(stock__lte=10, stock__gt=0)
        if self.value() == 'out':
            return queryset.filter(stock=0)
        if self.value() == 'available':
            return queryset.filter(stock__gt=10)
        if self.value() == 'critical':
            return queryset.filter(stock__lte=5, stock__gt=0)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'product_count', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at',)
    
    def product_count(self, obj):
        count = obj.products.count()
        return format_html(f'<strong>{count} productos</strong>')
    product_count.short_description = 'Total Productos'

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'alt_text', 'is_featured')
    readonly_fields = ('created_at',)


class ProductSupplierInline(admin.TabularInline):
    model = ProductSupplier
    extra = 1
    fields = ('supplier', 'supplier_sku', 'cost_price', 'minimum_order_quantity', 'lead_time_days', 'is_primary')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'image_thumbnail', 'name', 'category', 'product_type', 'price',
        'price_display', 'tax_display', 'stock', 'stock_display', 'featured', 'available', 'updated_at'
    )
    list_filter = (
        'category', 'product_type', 'available', 'featured', 'is_tax_exempt',
        'tax_configuration', LowStockFilter, 'created_at', 'updated_at'
    )
    search_fields = ('name', 'description', 'ingredients')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductSupplierInline]
    list_editable = ('price', 'stock', 'featured', 'available')
    readonly_fields = ('created_at', 'updated_at', 'image_preview', 'price_breakdown', 'supplier_info')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'slug', 'category', 'product_type')
        }),
        ('Contenido', {
            'fields': ('description', 'ingredients', 'nutrition_facts')
        }),
        ('Precio y Stock', {
            'fields': ('price', 'discount_percentage', 'discount_price', 'is_on_sale', 'stock', 'min_stock_alert', 'weight'),
            'description': 'Gestión de precios e inventario'
        }),
        ('Configuración de Impuestos', {
            'fields': ('tax_configuration', 'is_tax_exempt', 'price_breakdown'),
            'description': 'Configuración de IVA y otros impuestos'
        }),
        ('Imagen Principal', {
            'fields': ('image', 'image_preview')
        }),
        ('Configuración', {
            'fields': ('available', 'featured'),
            'description': 'Productos destacados aparecerán en la página de inicio'
        }),
        ('Información de Proveedores', {
            'fields': ('supplier_info',),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = [
        'make_featured', 'remove_featured', 'make_available', 'make_unavailable',
        'increase_stock', 'decrease_stock', 'export_stock_report', 'export_low_stock_report',
        'apply_tax_exempt', 'remove_tax_exempt', 'bulk_price_update'
    ]
    
    def image_thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 5px;" />',
                obj.image.url
            )
        return "Sin imagen"
    image_thumbnail.short_description = 'Imagen'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 200px; object-fit: cover;" />',
                obj.image.url
            )
        return "Sin imagen"
    image_preview.short_description = 'Vista previa'
    
    def price_display(self, obj):
        price_html = f'<div><strong>${int(obj.current_price):,}</strong>'
        if obj.has_discount:
            price_html += f'<br><small style="text-decoration: line-through; color: #6c757d;">${int(obj.price):,}</small>'
            price_html += f'<br><small style="color: #28a745;">-{obj.discount_percentage}%</small>'
        price_html += '</div>'
        return format_html(price_html)
    price_display.short_description = 'Precio'
    price_display.admin_order_field = 'price'
    
    def tax_display(self, obj):
        if obj.is_tax_exempt:
            return format_html('<span style="color: #dc3545;">🚫 Exento</span>')
        elif obj.tax_configuration:
            return format_html(
                '<span style="color: #28a745;">✅ {}%</span>',
                obj.tax_configuration.rate
            )
        else:
            return format_html('<span style="color: #ffc107;">⚠️ Sin config</span>')
    tax_display.short_description = 'IVA'
    
    def price_breakdown(self, obj):
        if not obj.pk:
            return "Guarda el producto para ver desglose"
        
        breakdown_html = '<div style="background: #f8f9fa; padding: 10px; border-radius: 8px;">'
        breakdown_html += '<strong>Desglose de Precios:</strong><br>'
        
        if obj.is_tax_exempt:
            breakdown_html += f'💰 Precio final: ${int(obj.current_price):,}<br>'
            breakdown_html += '🚫 Exento de impuestos<br>'
        elif obj.tax_configuration:
            price_without_tax = obj.price_without_tax
            tax_amount = obj.tax_amount
            breakdown_html += f'💵 Precio sin IVA: ${int(price_without_tax):,}<br>'
            breakdown_html += f'📊 {obj.tax_configuration.name} ({obj.tax_configuration.rate}%): ${int(tax_amount):,}<br>'
            breakdown_html += f'💰 <strong>Precio final: ${int(obj.current_price):,}</strong><br>'
        else:
            breakdown_html += f'💰 Precio: ${int(obj.current_price):,}<br>'
            breakdown_html += '⚠️ Sin configuración de impuesto<br>'
        
        breakdown_html += '</div>'
        return format_html(breakdown_html)
    price_breakdown.short_description = 'Desglose de Precio'
    
    def supplier_info(self, obj):
        if not obj.pk:
            return "Guarda el producto para ver proveedores"
        
        suppliers = obj.supplier_info.all()
        if not suppliers:
            return "Sin proveedores configurados"
        
        info_html = '<div style="background: #f8f9fa; padding: 10px; border-radius: 8px;">'
        info_html += '<strong>Información de Proveedores:</strong><br>'
        
        for supplier_rel in suppliers:
            primary = "⭐ " if supplier_rel.is_primary else ""
            info_html += f'{primary}{supplier_rel.supplier.name}<br>'
            info_html += f'  💵 Costo: ${int(supplier_rel.cost_price):,}<br>'
            info_html += f'  📈 Margen: {supplier_rel.formatted_profit_margin}<br>'
            info_html += f'  📦 Min. orden: {supplier_rel.minimum_order_quantity}<br><br>'
        
        info_html += '</div>'
        return format_html(info_html)
    supplier_info.short_description = 'Información de Proveedores'
    
    def stock_display(self, obj):
        if obj.stock == 0:
            color = 'red'
            status = '🔴 AGOTADO'
            badge = 'danger'
        elif obj.stock <= 5:
            color = 'red'
            status = f'⚠️ CRÍTICO ({obj.stock})'
            badge = 'danger'
        elif obj.stock <= 10:
            color = 'orange'
            status = f'⚡ BAJO ({obj.stock})'
            badge = 'warning'
        else:
            color = 'green'
            status = f'✅ BIEN ({obj.stock})'
            badge = 'success'
        
        return format_html(
            '<span class="badge badge-{}" style="color: {}; font-weight: bold; padding: 5px 10px; border-radius: 15px; background: rgba({}, 0.1);">{}</span>',
            badge, color, 
            '255,0,0' if color == 'red' else '255,165,0' if color == 'orange' else '0,128,0',
            status
        )
    stock_display.short_description = 'Estado Stock'
    stock_display.admin_order_field = 'stock'
    
    # Acciones personalizadas
    def make_featured(self, request, queryset):
        updated = queryset.update(featured=True)
        self.message_user(
            request, 
            f'{updated} productos marcados como destacados. Aparecerán en la página de inicio.'
        )
    make_featured.short_description = "⭐ Marcar como destacados"
    
    def remove_featured(self, request, queryset):
        updated = queryset.update(featured=False)
        self.message_user(request, f'{updated} productos removidos de destacados.')
    remove_featured.short_description = "❌ Quitar de destacados"
    
    def make_available(self, request, queryset):
        updated = queryset.update(available=True)
        self.message_user(request, f'{updated} productos marcados como disponibles.')
    make_available.short_description = "✅ Marcar como disponibles"
    
    def make_unavailable(self, request, queryset):
        updated = queryset.update(available=False)
        self.message_user(request, f'{updated} productos marcados como no disponibles.')
    make_unavailable.short_description = "🚫 Marcar como no disponibles"
    
    def increase_stock(self, request, queryset):
        for product in queryset:
            product.stock += 10
            product.save()
        count = queryset.count()
        self.message_user(request, f'✅ Stock aumentado en 10 unidades para {count} productos.')
    increase_stock.short_description = "📈 Aumentar stock (+10)"
    
    def decrease_stock(self, request, queryset):
        for product in queryset:
            if product.stock >= 10:
                product.stock -= 10
                product.save()
        count = queryset.count()
        self.message_user(request, f'📉 Stock reducido en 10 unidades para productos con stock suficiente.')
    decrease_stock.short_description = "📉 Reducir stock (-10)"
    
    def export_stock_report(self, request, queryset):
        """Exportar reporte de stock a CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="reporte_stock.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Producto', 'Categoría', 'Stock', 'Precio', 'Estado', 'Última Actualización'])
        
        for product in queryset:
            status = 'Agotado' if product.stock == 0 else 'Crítico' if product.stock <= 5 else 'Bajo' if product.stock <= 10 else 'Normal'
            writer.writerow([
                product.name,
                product.category.name,
                product.stock,
                product.price,
                status,
                product.updated_at.strftime('%d/%m/%Y %H:%M')
            ])
        
        return response
    export_stock_report.short_description = "📊 Exportar reporte de stock"
    
    def export_low_stock_report(self, request, queryset):
        """Exportar productos con stock bajo"""
        low_stock_products = queryset.filter(stock__lte=10)
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="productos_stock_bajo.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Producto', 'Categoría', 'Stock Actual', 'Precio', 'Estado', 'Acción Requerida'])
        
        for product in low_stock_products:
            if product.stock == 0:
                action = 'REABASTECER URGENTE'
                status = 'AGOTADO'
            elif product.stock <= 5:
                action = 'Reabastecer pronto'
                status = 'CRÍTICO'
            else:
                action = 'Monitorear'
                status = 'BAJO'
                
            writer.writerow([
                product.name,
                product.category.name,
                product.stock,
                f'${product.price:,.0f}',
                status,
                action
            ])
        
        return response
    export_low_stock_report.short_description = "📋 Exportar productos stock bajo"
    
    def apply_tax_exempt(self, request, queryset):
        updated = queryset.update(is_tax_exempt=True)
        self.message_user(request, f'{updated} productos marcados como exentos de impuesto.')
    apply_tax_exempt.short_description = "🚫 Marcar como exento de IVA"
    
    def remove_tax_exempt(self, request, queryset):
        updated = queryset.update(is_tax_exempt=False)
        self.message_user(request, f'{updated} productos ya no son exentos de impuesto.')
    remove_tax_exempt.short_description = "✅ Quitar exención de IVA"
    
    def bulk_price_update(self, request, queryset):
        """Acción personalizada para actualización masiva de precios"""
        if 'apply' in request.POST:
            percentage = float(request.POST.get('percentage', 0))
            if percentage != 0:
                updated_count = 0
                for product in queryset:
                    old_price = product.price
                    if percentage > 0:
                        new_price = old_price * (1 + percentage / 100)
                    else:
                        new_price = old_price * (1 + percentage / 100)
                    
                    product.price = round(new_price, 0)  # Redondear a entero para CLP
                    product.save()
                    
                    # Registrar movimiento en ProductStock si se desea
                    updated_count += 1
                
                self.message_user(
                    request, 
                    f'Precios actualizados para {updated_count} productos con {percentage:+.1f}%'
                )
                return
        
        # Renderizar formulario para el porcentaje
        context = {
            'products': queryset,
            'action_name': 'bulk_price_update',
            'title': 'Actualización Masiva de Precios'
        }
        return render(request, 'admin/bulk_price_update.html', context)
    bulk_price_update.short_description = "💰 Actualización masiva de precios"

    class Media:
        css = {
            'all': ('admin/css/stock_management.css',)
        }
        js = ('admin/js/stock_management.js',)

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image_thumbnail', 'alt_text', 'is_featured', 'created_at')
    list_filter = ('is_featured', 'created_at')
    search_fields = ('product__name', 'alt_text')
    
    def image_thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 5px;" />',
                obj.image.url
            )
        return "Sin imagen"
    image_thumbnail.short_description = 'Imagen'

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating_stars', 'comment_preview', 'created_at')
    list_filter = ('rating', 'created_at', 'product__category')
    search_fields = ('product__name', 'user__username', 'comment')
    readonly_fields = ('created_at',)
    
    def rating_stars(self, obj):
        stars = '⭐' * obj.rating
        return format_html(f'<span>{stars} ({obj.rating})</span>')
    rating_stars.short_description = 'Calificación'
    
    def comment_preview(self, obj):
        return obj.comment[:50] + '...' if len(obj.comment) > 50 else obj.comment
    comment_preview.short_description = 'Comentario'

# Configuración del título del admin
admin.site.site_header = "🍪 Dulce Bias - Panel de Administración"
admin.site.site_title = "Dulce Bias Admin"
admin.site.index_title = "Gestión de Tienda Online"


# ====================== NUEVOS MODELOS ADMINISTRATIVOS ======================

@admin.register(TaxConfiguration)
class TaxConfigurationAdmin(admin.ModelAdmin):
    list_display = ('name', 'formatted_rate', 'is_active', 'applies_to_shipping', 'products_count', 'updated_at')
    list_filter = ('is_active', 'applies_to_shipping', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('is_active', 'applies_to_shipping')
    
    actions = ['activate_taxes', 'deactivate_taxes']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'rate')
        }),
        ('Configuración', {
            'fields': ('is_active', 'applies_to_shipping')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def formatted_rate(self, obj):
        return format_html(
            '<span style="font-weight: bold; color: #28a745;">{}</span>',
            f"{obj.rate}%"
        )
    formatted_rate.short_description = 'Tasa'
    formatted_rate.admin_order_field = 'rate'
    
    def products_count(self, obj):
        count = obj.product_set.count()
        return format_html(
            '<span class="badge" style="background: #007bff; color: white; padding: 3px 8px; border-radius: 12px;">{} productos</span>',
            count
        )
    products_count.short_description = 'Productos'
    
    def activate_taxes(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} configuraciones de impuesto activadas.')
    activate_taxes.short_description = "✅ Activar configuraciones"
    
    def deactivate_taxes(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} configuraciones de impuesto desactivadas.')
    deactivate_taxes.short_description = "❌ Desactivar configuraciones"


class CouponUsageInline(admin.TabularInline):
    model = CouponUsage
    extra = 0
    readonly_fields = ('user', 'order', 'discount_amount', 'used_at')
    can_delete = False


@admin.register(DiscountCoupon)
class DiscountCouponAdmin(admin.ModelAdmin):
    list_display = (
        'code', 'name', 'discount_display', 'status_badge', 'usage_info', 
        'valid_period', 'current_uses', 'created_at'
    )
    list_filter = (
        'discount_type', 'usage_type', 'is_active', 'valid_from', 'valid_until', 'created_at'
    )
    search_fields = ('code', 'name', 'description')
    readonly_fields = ('current_uses', 'created_at', 'updated_at', 'usage_statistics')
    filter_horizontal = ('categories', 'products', 'excluded_products')
    inlines = [CouponUsageInline]
    
    actions = [
        'activate_coupons', 'deactivate_coupons', 'reset_usage_count', 
        'export_coupon_report', 'extend_validity'
    ]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('code', 'name', 'description')
        }),
        ('Configuración de Descuento', {
            'fields': ('discount_type', 'discount_value', 'minimum_order_amount', 'maximum_discount_amount')
        }),
        ('Restricciones de Uso', {
            'fields': ('usage_type', 'max_uses', 'current_uses')
        }),
        ('Período de Validez', {
            'fields': ('valid_from', 'valid_until', 'is_active')
        }),
        ('Productos Aplicables', {
            'fields': ('categories', 'products', 'excluded_products'),
            'classes': ('collapse',)
        }),
        ('Estadísticas', {
            'fields': ('usage_statistics',),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def discount_display(self, obj):
        if obj.discount_type == 'percentage':
            return format_html(
                '<span style="background: #e3f2fd; color: #1976d2; padding: 4px 8px; border-radius: 12px; font-weight: bold;">{}%</span>',
                obj.discount_value
            )
        elif obj.discount_type == 'fixed_amount':
            return format_html(
                '<span style="background: #e8f5e8; color: #2e7d32; padding: 4px 8px; border-radius: 12px; font-weight: bold;">${:,}</span>',
                int(obj.discount_value)
            )
        else:
            return format_html(
                '<span style="background: #fff3e0; color: #f57c00; padding: 4px 8px; border-radius: 12px; font-weight: bold;">📦 Envío Gratis</span>'
            )
    discount_display.short_description = 'Descuento'
    
    def status_badge(self, obj):
        status = obj.status_display
        if "Activo" in status:
            color = "#28a745"
            bg = "#d4edda"
        elif "Expirado" in status or "Agotado" in status:
            color = "#dc3545"
            bg = "#f8d7da"
        elif "Programado" in status:
            color = "#17a2b8"
            bg = "#d1ecf1"
        else:
            color = "#6c757d"
            bg = "#e2e3e5"
        
        return format_html(
            '<span style="background: {}; color: {}; padding: 4px 8px; border-radius: 12px; font-weight: bold;">{}</span>',
            bg, color, status
        )
    status_badge.short_description = 'Estado'
    
    def usage_info(self, obj):
        remaining = obj.remaining_uses
        if remaining == "Ilimitado":
            return format_html('<span style="color: #28a745;">♾️ Ilimitado</span>')
        elif remaining == 0:
            return format_html('<span style="color: #dc3545;">🚫 Agotado</span>')
        else:
            return format_html('<span style="color: #17a2b8;">📊 {} restantes</span>', remaining)
    usage_info.short_description = 'Usos'
    
    def valid_period(self, obj):
        now = timezone.now()
        if now < obj.valid_from:
            return format_html(
                '<span style="color: #17a2b8;">⏳ Inicia: {}</span>',
                obj.valid_from.strftime('%d/%m/%Y')
            )
        elif now > obj.valid_until:
            return format_html(
                '<span style="color: #dc3545;">⏰ Expiró: {}</span>',
                obj.valid_until.strftime('%d/%m/%Y')
            )
        else:
            return format_html(
                '<span style="color: #28a745;">✅ Hasta: {}</span>',
                obj.valid_until.strftime('%d/%m/%Y')
            )
    valid_period.short_description = 'Período'
    
    def usage_statistics(self, obj):
        if not obj.pk:
            return "Guarda el cupón para ver estadísticas"
        
        total_uses = obj.usages.count()
        total_discount = obj.usages.aggregate(total=Sum('discount_amount'))['total'] or 0
        
        return format_html(
            '<div style="background: #f8f9fa; padding: 10px; border-radius: 8px;">'
            '<strong>Estadísticas de Uso:</strong><br>'
            '📊 Total de usos: {}<br>'
            '💰 Descuento total otorgado: ${:,}<br>'
            '👥 Usuarios únicos: {}<br>'
            '</div>',
            total_uses,
            int(total_discount),
            obj.usages.values('user').distinct().count()
        )
    usage_statistics.short_description = 'Estadísticas'
    
    def activate_coupons(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} cupones activados.')
    activate_coupons.short_description = "✅ Activar cupones"
    
    def deactivate_coupons(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} cupones desactivados.')
    deactivate_coupons.short_description = "❌ Desactivar cupones"
    
    def reset_usage_count(self, request, queryset):
        updated = queryset.update(current_uses=0)
        self.message_user(request, f'Contador de uso reiniciado para {updated} cupones.')
    reset_usage_count.short_description = "🔄 Reiniciar contador de uso"
    
    def export_coupon_report(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="reporte_cupones.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Código', 'Nombre', 'Tipo', 'Valor', 'Estado', 'Usos Actuales', 
            'Usos Máximos', 'Válido Desde', 'Válido Hasta', 'Descuento Total'
        ])
        
        for coupon in queryset:
            total_discount = coupon.usages.aggregate(total=Sum('discount_amount'))['total'] or 0
            writer.writerow([
                coupon.code,
                coupon.name,
                coupon.get_discount_type_display(),
                coupon.discount_value,
                coupon.status_display,
                coupon.current_uses,
                coupon.max_uses or 'Ilimitado',
                coupon.valid_from.strftime('%d/%m/%Y'),
                coupon.valid_until.strftime('%d/%m/%Y'),
                f'${int(total_discount):,}'
            ])
        
        return response
    export_coupon_report.short_description = "📊 Exportar reporte de cupones"


@admin.register(ProductStock)
class ProductStockAdmin(admin.ModelAdmin):
    list_display = (
        'product', 'movement_type_display', 'quantity_display', 'stock_change', 
        'reason', 'user', 'created_at'
    )
    list_filter = ('movement_type', 'created_at', 'product__category')
    search_fields = ('product__name', 'reason', 'reference')
    readonly_fields = ('created_at',)
    autocomplete_fields = ('product', 'user')
    
    actions = ['export_stock_movements']
    
    def movement_type_display(self, obj):
        colors = {
            'entry': '#28a745',
            'exit': '#dc3545',
            'adjustment': '#17a2b8',
            'sale': '#007bff',
            'return': '#28a745',
            'damage': '#6c757d',
            'expired': '#ffc107'
        }
        
        icons = {
            'entry': '📈',
            'exit': '📉',
            'adjustment': '⚖️',
            'sale': '🛒',
            'return': '↩️',
            'damage': '⚠️',
            'expired': '⏰'
        }
        
        color = colors.get(obj.movement_type, '#6c757d')
        icon = icons.get(obj.movement_type, '📦')
        
        return format_html(
            '<span style="color: {};">{} {}</span>',
            color, icon, obj.get_movement_type_display()
        )
    movement_type_display.short_description = 'Tipo de Movimiento'
    
    def quantity_display(self, obj):
        color = '#28a745' if obj.quantity > 0 else '#dc3545'
        symbol = '+' if obj.quantity > 0 else ''
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}{}</span>',
            color, symbol, obj.quantity
        )
    quantity_display.short_description = 'Cantidad'
    quantity_display.admin_order_field = 'quantity'
    
    def stock_change(self, obj):
        return format_html(
            '<span style="color: #6c757d;">{} → {}</span>',
            obj.previous_stock, obj.new_stock
        )
    stock_change.short_description = 'Cambio de Stock'
    
    def export_stock_movements(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="movimientos_stock.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Producto', 'Tipo', 'Cantidad', 'Stock Anterior', 'Stock Nuevo', 
            'Motivo', 'Referencia', 'Usuario', 'Fecha'
        ])
        
        for movement in queryset:
            writer.writerow([
                movement.product.name,
                movement.get_movement_type_display(),
                movement.quantity,
                movement.previous_stock,
                movement.new_stock,
                movement.reason,
                movement.reference,
                movement.user.username if movement.user else 'Sistema',
                movement.created_at.strftime('%d/%m/%Y %H:%M')
            ])
        
        return response
    export_stock_movements.short_description = "📊 Exportar movimientos"


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'contact_person', 'city', 'rating_display', 'products_count', 
        'is_active', 'updated_at'
    )
    list_filter = ('is_active', 'country', 'city', 'rating', 'created_at')
    search_fields = ('name', 'contact_person', 'email', 'tax_id')
    readonly_fields = ('created_at', 'updated_at', 'supplier_statistics')
    list_editable = ('is_active',)
    
    actions = ['activate_suppliers', 'deactivate_suppliers', 'export_supplier_report']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'contact_person', 'email', 'phone')
        }),
        ('Ubicación', {
            'fields': ('address', 'city', 'country')
        }),
        ('Información Fiscal', {
            'fields': ('tax_id',)
        }),
        ('Evaluación', {
            'fields': ('rating', 'is_active')
        }),
        ('Notas', {
            'fields': ('notes',)
        }),
        ('Estadísticas', {
            'fields': ('supplier_statistics',),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def rating_display(self, obj):
        if obj.rating:
            stars = '⭐' * int(obj.rating)
            return format_html(
                '<span style="font-size: 16px;">{} ({})</span>',
                stars, obj.rating
            )
        return '⚫ Sin calificar'
    rating_display.short_description = 'Calificación'
    rating_display.admin_order_field = 'rating'
    
    def products_count(self, obj):
        count = obj.products.count()
        return format_html(
            '<span class="badge" style="background: #007bff; color: white; padding: 3px 8px; border-radius: 12px;">{} productos</span>',
            count
        )
    products_count.short_description = 'Productos'
    
    def supplier_statistics(self, obj):
        if not obj.pk:
            return "Guarda el proveedor para ver estadísticas"
        
        products_count = obj.products.count()
        primary_products = obj.products.filter(is_primary=True).count()
        
        return format_html(
            '<div style="background: #f8f9fa; padding: 10px; border-radius: 8px;">'
            '<strong>Estadísticas del Proveedor:</strong><br>'
            '📦 Total de productos: {}<br>'
            '⭐ Productos principales: {}<br>'
            '📧 Email: {}<br>'
            '📞 Teléfono: {}<br>'
            '</div>',
            products_count,
            primary_products,
            obj.email or 'No especificado',
            obj.phone or 'No especificado'
        )
    supplier_statistics.short_description = 'Estadísticas'
    
    def activate_suppliers(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} proveedores activados.')
    activate_suppliers.short_description = "✅ Activar proveedores"
    
    def deactivate_suppliers(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} proveedores desactivados.')
    deactivate_suppliers.short_description = "❌ Desactivar proveedores"


@admin.register(ProductSupplier)
class ProductSupplierAdmin(admin.ModelAdmin):
    list_display = (
        'product', 'supplier', 'cost_price', 'profit_margin_display', 
        'minimum_order_quantity', 'lead_time_days', 'is_primary'
    )
    list_filter = ('is_primary', 'supplier', 'lead_time_days')
    search_fields = ('product__name', 'supplier__name', 'supplier_sku')
    readonly_fields = ('created_at', 'updated_at', 'profit_analysis')
    list_editable = ('is_primary',)
    
    fieldsets = (
        ('Relación Producto-Proveedor', {
            'fields': ('product', 'supplier', 'supplier_sku')
        }),
        ('Información Comercial', {
            'fields': ('cost_price', 'minimum_order_quantity', 'lead_time_days', 'is_primary')
        }),
        ('Análisis de Rentabilidad', {
            'fields': ('profit_analysis',),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('last_order_date', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def profit_margin_display(self, obj):
        margin = obj.profit_margin
        if margin > 50:
            color = '#28a745'  # Verde
        elif margin > 25:
            color = '#ffc107'  # Amarillo
        else:
            color = '#dc3545'  # Rojo
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1f}%</span>',
            color, margin
        )
    profit_margin_display.short_description = 'Margen'
    profit_margin_display.admin_order_field = 'cost_price'
    
    def profit_analysis(self, obj):
        if not obj.pk:
            return "Guarda la relación para ver análisis"
        
        margin = obj.profit_margin
        profit_amount = obj.product.price - obj.cost_price
        
        status_color = '#28a745' if margin > 50 else '#ffc107' if margin > 25 else '#dc3545'
        status_text = 'Excelente' if margin > 50 else 'Bueno' if margin > 25 else 'Bajo'
        
        return format_html(
            '<div style="background: #f8f9fa; padding: 10px; border-radius: 8px;">'
            '<strong>Análisis de Rentabilidad:</strong><br>'
            '💰 Precio de venta: ${:,}<br>'
            '💵 Costo: ${:,}<br>'
            '📈 Ganancia: ${:,}<br>'
            '📊 Margen: <span style="color: {}; font-weight: bold;">{:.1f}% ({})</span><br>'
            '</div>',
            int(obj.product.price),
            int(obj.cost_price),
            int(profit_amount),
            status_color, margin, status_text
        )
    profit_analysis.short_description = 'Análisis de Rentabilidad'
