from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from .models import Category, Product, ProductImage, Review
import csv

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

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'image_thumbnail', 'name', 'category', 'product_type', 
        'price', 'stock', 'stock_display', 'featured', 'available', 'updated_at'
    )
    list_filter = (
        'category', 'product_type', 'available', 'featured', 
        LowStockFilter, 'created_at', 'updated_at'
    )
    search_fields = ('name', 'description', 'ingredients')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]
    list_editable = ('price', 'stock', 'featured', 'available')
    readonly_fields = ('created_at', 'updated_at', 'image_preview')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'slug', 'category', 'product_type')
        }),
        ('Contenido', {
            'fields': ('description', 'ingredients', 'nutrition_facts')
        }),
        ('Precio y Stock', {
            'fields': ('price', 'stock', 'weight'),
            'description': 'Gestión de precios e inventario'
        }),
        ('Imagen Principal', {
            'fields': ('image', 'image_preview')
        }),
        ('Configuración', {
            'fields': ('available', 'featured'),
            'description': 'Productos destacados aparecerán en la página de inicio'
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = [
        'make_featured', 'remove_featured', 'make_available', 'make_unavailable',
        'increase_stock', 'decrease_stock', 'export_stock_report', 'export_low_stock_report'
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
