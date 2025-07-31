from django.contrib import admin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Order, OrderItem, OrderStatusHistory, BankAccount, TransferPayment

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('price',)
    extra = 0

class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    readonly_fields = ('changed_at',)
    extra = 0

class TransferPaymentInline(admin.StackedInline):
    model = TransferPayment
    readonly_fields = ('created_at', 'updated_at', 'verified_at')
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'status', 'payment_status', 'payment_method', 'total', 'created_at')
    list_filter = ('status', 'payment_status', 'payment_method', 'created_at')
    search_fields = ('order_number', 'user__username', 'user__email')
    readonly_fields = ('order_number', 'created_at', 'updated_at')
    inlines = [OrderItemInline, OrderStatusHistoryInline, TransferPaymentInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')
    search_fields = ('order__order_number', 'product__name')

@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('order', 'status', 'changed_at', 'notes')
    list_filter = ('status', 'changed_at')
    search_fields = ('order__order_number', 'notes')

@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ('bank_name', 'account_type', 'account_number', 'account_holder', 'is_active')
    list_filter = ('bank_name', 'account_type', 'is_active')
    search_fields = ('bank_name', 'account_number', 'account_holder', 'rut')
    list_editable = ('is_active',)

@admin.register(TransferPayment)
class TransferPaymentAdmin(admin.ModelAdmin):
    list_display = (
        'order_number', 'sender_name', 'transfer_amount', 'status', 
        'transfer_date', 'created_at', 'verified_by'
    )
    list_filter = ('status', 'bank_account', 'transfer_date', 'created_at')
    search_fields = (
        'order__order_number', 'sender_name', 'sender_rut', 
        'reference_number'
    )
    readonly_fields = ('created_at', 'updated_at', 'order_link', 'receipt_preview')
    
    # No permitir agregar nuevas transferencias directamente
    def has_add_permission(self, request):
        return False
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['title'] = 'Gestión de Pagos por Transferencia'
        extra_context['subtitle'] = 'Los pagos por transferencia se crean automáticamente cuando los clientes suben sus comprobantes'
        return super().changelist_view(request, extra_context=extra_context)
    
    # Solo permitir eliminar si está en estado pendiente
    def has_delete_permission(self, request, obj=None):
        if obj and obj.status != 'pending':
            return False
        return super().has_delete_permission(request, obj)
    
    fieldsets = (
        ('Información del Pedido', {
            'fields': ('order_link', 'bank_account')
        }),
        ('Datos de la Transferencia', {
            'fields': (
                'transfer_amount', 'transfer_date', 'reference_number',
                'sender_name', 'sender_rut', 'sender_bank'
            )
        }),
        ('Comprobante', {
            'fields': ('receipt_image', 'receipt_preview')
        }),
        ('Verificación', {
            'fields': ('status', 'verification_notes', 'verified_by', 'verified_at'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def order_number(self, obj):
        return obj.order.order_number
    order_number.short_description = 'Número de Pedido'
    
    def order_link(self, obj):
        if obj.order:
            url = reverse('admin:orders_order_change', args=[obj.order.id])
            return format_html('<a href="{}" target="_blank">Pedido #{}</a>', url, obj.order.order_number)
        return '-'
    order_link.short_description = 'Pedido'
    
    def receipt_preview(self, obj):
        if obj.receipt_image:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 200px;" />',
                obj.receipt_image.url
            )
        return 'No hay comprobante'
    receipt_preview.short_description = 'Vista Previa del Comprobante'
    
    def save_model(self, request, obj, form, change):
        # Auto-asignar el usuario que verifica
        if 'status' in form.changed_data and obj.status == 'verified':
            obj.verified_by = request.user
            obj.verified_at = timezone.now()
        super().save_model(request, obj, form, change)
    
    # Filtrar solo usuarios superuser para el campo verified_by
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "verified_by":
            kwargs["queryset"] = User.objects.filter(is_superuser=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
