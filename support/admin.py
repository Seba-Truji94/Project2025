from django.contrib import admin
from .models import (
    SupportCategory, SupportTicket, SupportMessage, 
    SupportFAQ, AIConversationHistory, SupportKnowledgeBase
)


@admin.register(SupportCategory)
class SupportCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    list_editable = ['is_active']


class SupportMessageInline(admin.TabularInline):
    model = SupportMessage
    extra = 0
    readonly_fields = ['created_at']
    fields = ['sender', 'content', 'is_ai_response', 'created_at']


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = [
        'ticket_number', 'user', 'subject', 'category', 
        'status', 'priority', 'created_at', 'updated_at'
    ]
    list_filter = [
        'status', 'priority', 'category', 'created_at', 
        'updated_at', 'is_resolved'
    ]
    search_fields = [
        'ticket_number', 'subject', 'description', 
        'user__username', 'user__email', 'user__first_name', 'user__last_name'
    ]
    readonly_fields = ['id', 'ticket_number', 'created_at', 'updated_at']
    ordering = ['-created_at']
    list_editable = ['status', 'priority']
    
    fieldsets = (
        ('Información del Ticket', {
            'fields': (
                'id', 'ticket_number', 'user', 'category', 
                'subject', 'description'
            )
        }),
        ('Estado y Prioridad', {
            'fields': ('status', 'priority', 'is_resolved')
        }),
        ('Calificación', {
            'fields': ('rating', 'feedback'),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [SupportMessageInline]
    
    def changelist_view(self, request, extra_context=None):
        # Estadísticas en tiempo real
        from django.db.models import Count, Q
        from django.contrib.auth.models import User
        
        extra_context = extra_context or {}
        
        # Contadores de tickets
        total_tickets = SupportTicket.objects.count()
        open_tickets = SupportTicket.objects.filter(status__in=['open', 'in_progress']).count()
        resolved_tickets = SupportTicket.objects.filter(status='resolved').count()
        
        # Contadores de usuarios
        total_users = User.objects.count()
        active_clients = User.objects.filter(
            is_superuser=False, 
            supportticket__isnull=False
        ).distinct().count()
        
        # Contadores de categorías
        total_categories = SupportCategory.objects.filter(is_active=True).count()
        
        extra_context.update({
            'total_tickets': total_tickets,
            'open_tickets': open_tickets,
            'resolved_tickets': resolved_tickets,
            'total_users': total_users,
            'active_clients': active_clients,
            'total_categories': total_categories,
            'has_real_data': total_tickets > 0,
        })
        
        return super().changelist_view(request, extra_context=extra_context)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'category')


@admin.register(SupportMessage)
class SupportMessageAdmin(admin.ModelAdmin):
    list_display = [
        'ticket', 'sender', 'is_ai_response', 'created_at'
    ]
    list_filter = ['is_ai_response', 'created_at', 'ticket__category']
    search_fields = [
        'content', 'ticket__ticket_number', 'ticket__subject',
        'sender__username', 'sender__email'
    ]
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('ticket', 'sender')


@admin.register(SupportFAQ)
class SupportFAQAdmin(admin.ModelAdmin):
    list_display = [
        'question', 'category', 'is_active', 'helpful_votes', 
        'not_helpful_votes', 'created_at', 'updated_at'
    ]
    list_filter = ['is_active', 'category', 'created_at']
    search_fields = ['question', 'answer']
    ordering = ['-created_at']
    list_editable = ['is_active']
    
    fieldsets = (
        ('Pregunta y Respuesta', {
            'fields': ('question', 'answer', 'category', 'is_active')
        }),
        ('Estadísticas', {
            'fields': ('helpful_votes', 'not_helpful_votes', 'view_count'),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'helpful_votes', 'not_helpful_votes', 'view_count']


@admin.register(AIConversationHistory)
class AIConversationHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'session_id', 'created_at', 'get_message_count'
    ]
    list_filter = ['created_at']
    search_fields = [
        'user__username', 'user__email', 'session_id',
        'conversation_data'
    ]
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_message_count(self, obj):
        import json
        try:
            data = json.loads(obj.conversation_data) if obj.conversation_data else {}
            return len(data.get('messages', []))
        except:
            return 0
    get_message_count.short_description = 'Mensajes'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(SupportKnowledgeBase)
class SupportKnowledgeBaseAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'category', 'is_active', 'times_used', 
        'created_at', 'updated_at'
    ]
    list_filter = ['is_active', 'category', 'created_at']
    search_fields = ['title', 'content', 'keywords']
    ordering = ['-times_used', '-created_at']
    list_editable = ['is_active']
    
    fieldsets = (
        ('Información Principal', {
            'fields': ('title', 'content', 'category', 'keywords')
        }),
        ('Configuración', {
            'fields': ('is_active',)
        }),
        ('Estadísticas', {
            'fields': ('times_used', 'effectiveness_score'),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'times_used', 'effectiveness_score']


# Personalización adicional del admin
admin.site.site_header = "Centro de Soporte - Galletas Kati"
admin.site.site_title = "Soporte Admin"
admin.site.index_title = "Panel de Administración de Soporte"
