from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Category, Product, ProductImage, Review

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
        'price', 'stock', 'featured', 'available', 'created_at'
    )
    list_filter = (
        'category', 'product_type', 'available', 'featured', 
        'created_at', 'updated_at'
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
            'fields': ('price', 'stock', 'weight')
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
    
    actions = ['make_featured', 'remove_featured', 'make_available', 'make_unavailable']
    
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
    
    def formatted_price_admin(self, obj):
        return obj.formatted_price
    formatted_price_admin.short_description = 'Precio'
    
    def stock_status(self, obj):
        if obj.stock > 10:
            color = 'green'
            status = f'{obj.stock} unidades'
        elif obj.stock > 0:
            color = 'orange'
            status = f'{obj.stock} unidades (Poco stock)'
        else:
            color = 'red'
            status = 'Agotado'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, status
        )
    stock_status.short_description = 'Stock'
    
    def featured_status(self, obj):
        if obj.featured:
            return format_html(
                '<span style="color: gold; font-weight: bold;">⭐ DESTACADO</span>'
            )
        return '-'
    featured_status.short_description = 'Destacado'
    
    # Acciones personalizadas
    def make_featured(self, request, queryset):
        updated = queryset.update(featured=True)
        self.message_user(
            request, 
            f'{updated} productos marcados como destacados. Aparecerán en la página de inicio.'
        )
    make_featured.short_description = "Marcar como destacados (página inicio)"
    
    def remove_featured(self, request, queryset):
        updated = queryset.update(featured=False)
        self.message_user(
            request, 
            f'{updated} productos removidos de destacados.'
        )
    remove_featured.short_description = "Quitar de destacados"
    
    def make_available(self, request, queryset):
        updated = queryset.update(available=True)
        self.message_user(request, f'{updated} productos marcados como disponibles.')
    make_available.short_description = "Marcar como disponibles"
    
    def make_unavailable(self, request, queryset):
        updated = queryset.update(available=False)
        self.message_user(request, f'{updated} productos marcados como no disponibles.')
    make_unavailable.short_description = "Marcar como no disponibles"

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
admin.site.site_header = "Dulce Bias - Administración"
admin.site.site_title = "Dulce Bias Admin"
admin.site.index_title = "Panel de Administración"
