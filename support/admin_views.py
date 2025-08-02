# support/admin_views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test, login_required
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.utils import timezone
import json

from .models import (
    SupportTicket, SupportMessage, SupportCategory, 
    SupportNotification, SupportFAQ
)
from .notification_service import NotificationService


def is_superuser(user):
    """Verificar si el usuario es superusuario"""
    return user.is_authenticated and user.is_superuser


@method_decorator(user_passes_test(is_superuser), name='dispatch')
class SupportManagementView(ListView):
    """Vista principal de gestión de soporte para superusuarios"""
    model = SupportTicket
    template_name = 'support/admin/management.html'
    context_object_name = 'tickets'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = SupportTicket.objects.select_related(
            'user', 'category'
        ).prefetch_related('messages').order_by('-created_at')
        
        # Filtros
        status = self.request.GET.get('status')
        priority = self.request.GET.get('priority')
        category = self.request.GET.get('category')
        search = self.request.GET.get('search')
        
        if status:
            queryset = queryset.filter(status=status)
        if priority:
            queryset = queryset.filter(priority=priority)
        if category:
            queryset = queryset.filter(category_id=category)
        if search:
            queryset = queryset.filter(
                Q(ticket_number__icontains=search) |
                Q(subject__icontains=search) |
                Q(user__username__icontains=search) |
                Q(user__email__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estadísticas
        total_tickets = SupportTicket.objects.count()
        open_tickets = SupportTicket.objects.filter(
            status__in=['open', 'in_progress']
        ).count()
        resolved_tickets = SupportTicket.objects.filter(
            status='resolved'
        ).count()
        
        # Tickets por categoría
        category_stats = SupportTicket.objects.values(
            'category__name'
        ).annotate(count=Count('id')).order_by('-count')
        
        # Tickets recientes (últimas 24 horas)
        recent_cutoff = timezone.now() - timedelta(hours=24)
        recent_tickets = SupportTicket.objects.filter(
            created_at__gte=recent_cutoff
        ).count()
        
        context.update({
            'total_tickets': total_tickets,
            'open_tickets': open_tickets,
            'resolved_tickets': resolved_tickets,
            'recent_tickets': recent_tickets,
            'category_stats': category_stats,
            'categories': SupportCategory.objects.filter(is_active=True),
            'status_choices': SupportTicket.STATUS_CHOICES,
            'priority_choices': SupportTicket.PRIORITY_CHOICES,
        })
        
        return context


@method_decorator(user_passes_test(is_superuser), name='dispatch')
class SupportTicketDetailManagementView(DetailView):
    """Vista de detalle para gestión de tickets individuales"""
    model = SupportTicket
    template_name = 'support/admin/ticket_detail.html'
    context_object_name = 'ticket'
    slug_field = 'ticket_number'
    slug_url_kwarg = 'ticket_number'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ticket = self.get_object()
        
        # Mensajes del ticket
        messages = ticket.messages.select_related('sender').order_by('created_at')
        
        # Usuarios staff para asignación
        staff_users = User.objects.filter(
            Q(is_staff=True) | Q(is_superuser=True)
        ).order_by('username')
        
        context.update({
            'messages': messages,
            'staff_users': staff_users,
            'status_choices': SupportTicket.STATUS_CHOICES,
            'priority_choices': SupportTicket.PRIORITY_CHOICES,
        })
        
        return context


@user_passes_test(is_superuser)
def support_statistics(request):
    """Vista de estadísticas detalladas"""
    # Estadísticas generales
    total_tickets = SupportTicket.objects.count()
    
    # Contadores específicos por estado
    open_tickets_count = SupportTicket.objects.filter(status='open').count()
    in_progress_tickets_count = SupportTicket.objects.filter(status='in_progress').count()
    resolved_tickets_count = SupportTicket.objects.filter(status='resolved').count()
    closed_tickets_count = SupportTicket.objects.filter(status='closed').count()
    
    # Tickets por estado
    status_stats = {}
    for status_code, status_name in SupportTicket.STATUS_CHOICES:
        count = SupportTicket.objects.filter(status=status_code).count()
        status_stats[status_name] = count
    
    # Tickets por prioridad
    priority_stats = {}
    for priority_code, priority_name in SupportTicket.PRIORITY_CHOICES:
        count = SupportTicket.objects.filter(priority=priority_code).count()
        priority_stats[priority_name] = count
    
    # Tickets por categoría
    category_stats = list(SupportTicket.objects.values(
        'category__name'
    ).annotate(count=Count('id')).order_by('-count'))
    
    # Tickets por mes (últimos 6 meses)
    monthly_stats = []
    for i in range(6):
        date = timezone.now() - timedelta(days=30*i)
        start_date = date.replace(day=1)
        if i == 0:
            end_date = timezone.now()
        else:
            end_date = start_date.replace(month=start_date.month+1) - timedelta(days=1)
        
        count = SupportTicket.objects.filter(
            created_at__range=[start_date, end_date]
        ).count()
        
        monthly_stats.append({
            'month': start_date.strftime('%B %Y'),
            'count': count
        })
    
    monthly_stats.reverse()
    
    context = {
        'total_tickets': total_tickets,
        'open_tickets_count': open_tickets_count,
        'in_progress_tickets_count': in_progress_tickets_count,
        'resolved_tickets_count': resolved_tickets_count,
        'closed_tickets_count': closed_tickets_count,
        'status_stats': status_stats,
        'priority_stats': priority_stats,
        'category_stats': category_stats,
        'monthly_stats': monthly_stats,
    }
    
    return render(request, 'support/admin/statistics.html', context)


@user_passes_test(is_superuser)
def bulk_update_tickets(request):
    """Actualización masiva de tickets"""
    if request.method == 'POST':
        ticket_ids = request.POST.getlist('ticket_ids')
        action = request.POST.get('action')
        
        if not ticket_ids:
            messages.error(request, 'No se seleccionaron tickets.')
            return redirect('support:admin_management')
        
        tickets = SupportTicket.objects.filter(id__in=ticket_ids)
        
        if action == 'change_status':
            new_status = request.POST.get('new_status')
            if new_status:
                updated = tickets.update(status=new_status)
                messages.success(
                    request, 
                    f'Se actualizó el estado de {updated} tickets.'
                )
        
        elif action == 'change_priority':
            new_priority = request.POST.get('new_priority')
            if new_priority:
                updated = tickets.update(priority=new_priority)
                messages.success(
                    request, 
                    f'Se actualizó la prioridad de {updated} tickets.'
                )
    
    return redirect('support:admin_management')


@user_passes_test(is_superuser)
def ajax_change_status(request):
    """Cambiar estado de ticket vía AJAX"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            ticket_id = data.get('ticket_id')
            new_status = data.get('status')
            
            ticket = get_object_or_404(SupportTicket, id=ticket_id)
            old_status = ticket.status
            ticket.status = new_status
            ticket.save()
            
            # Crear mensaje de cambio de estado
            SupportMessage.objects.create(
                ticket=ticket,
                sender=request.user,
                content=f'Estado cambiado de "{ticket.get_status_display()}" a "{ticket.get_status_display()}"',
                message_type='status_change',
                is_ai_response=False
            )
            
            # Notificar al usuario
            notification_service = NotificationService()
            notification_service.notify_status_change(ticket, old_status, new_status)
            
            return JsonResponse({
                'success': True,
                'message': 'Estado actualizado correctamente'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})


@user_passes_test(is_superuser)
def ajax_assign_ticket(request):
    """Asignar ticket a usuario vía AJAX"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            ticket_id = data.get('ticket_id')
            user_id = data.get('user_id')
            
            ticket = get_object_or_404(SupportTicket, id=ticket_id)
            assigned_user = get_object_or_404(User, id=user_id) if user_id else None
            
            ticket.assigned_to = assigned_user
            ticket.save()
            
            # Crear mensaje de asignación
            if assigned_user:
                message_content = f'Ticket asignado a {assigned_user.username}'
            else:
                message_content = 'Ticket sin asignar'
            
            SupportMessage.objects.create(
                ticket=ticket,
                sender=request.user,
                content=message_content,
                message_type='assignment',
                is_ai_response=False
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Ticket asignado correctamente'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})


@user_passes_test(is_superuser)
def ajax_stats(request):
    """Obtener estadísticas en tiempo real vía AJAX"""
    total_tickets = SupportTicket.objects.count()
    open_tickets = SupportTicket.objects.filter(
        status__in=['open', 'in_progress']
    ).count()
    resolved_tickets = SupportTicket.objects.filter(status='resolved').count()
    
    # Tickets recientes (últimas 24 horas)
    recent_cutoff = timezone.now() - timedelta(hours=24)
    recent_tickets = SupportTicket.objects.filter(
        created_at__gte=recent_cutoff
    ).count()
    
    return JsonResponse({
        'total_tickets': total_tickets,
        'open_tickets': open_tickets,
        'resolved_tickets': resolved_tickets,
        'recent_tickets': recent_tickets,
    })


@user_passes_test(is_superuser)
def category_management_view(request):
    """Gestión de categorías de soporte"""
    categories = SupportCategory.objects.annotate(
        ticket_count=Count('supportticket')
    ).order_by('name')
    
    return render(request, 'support/admin/categories.html', {
        'categories': categories
    })


@user_passes_test(is_superuser)
def create_category(request):
    """Crear nueva categoría"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        
        if name:
            category = SupportCategory.objects.create(
                name=name,
                description=description,
                is_active=True
            )
            messages.success(request, f'Categoría "{name}" creada correctamente.')
        else:
            messages.error(request, 'El nombre de la categoría es requerido.')
    
    return redirect('support:admin_category_management')


@user_passes_test(is_superuser)
def edit_category(request, category_id):
    """Editar categoría existente"""
    category = get_object_or_404(SupportCategory, id=category_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        is_active = request.POST.get('is_active') == 'on'
        
        if name:
            category.name = name
            category.description = description
            category.is_active = is_active
            category.save()
            messages.success(request, f'Categoría "{name}" actualizada correctamente.')
        else:
            messages.error(request, 'El nombre de la categoría es requerido.')
    
    return redirect('support:admin_category_management')


@user_passes_test(is_superuser)
def toggle_category(request, category_id):
    """Activar/desactivar categoría"""
    category = get_object_or_404(SupportCategory, id=category_id)
    
    if request.method == 'POST':
        is_active = request.POST.get('is_active') == 'true'
        category.is_active = is_active
        category.save()
        
        action = "activada" if is_active else "desactivada"
        messages.success(request, f'Categoría "{category.name}" {action} correctamente.')
    
    return redirect('support:admin_category_management')


@user_passes_test(is_superuser)
def delete_category(request, category_id):
    """Eliminar categoría (solo si no tiene tickets)"""
    category = get_object_or_404(SupportCategory, id=category_id)
    
    if request.method == 'POST':
        if category.supportticket_set.count() == 0:
            category_name = category.name
            category.delete()
            messages.success(request, f'Categoría "{category_name}" eliminada correctamente.')
        else:
            messages.error(request, 'No se puede eliminar una categoría que tiene tickets asociados.')
    
    return redirect('support:admin_category_management')


@user_passes_test(is_superuser)
def update_ticket_status(request, ticket_number):
    """Actualizar estado de un ticket específico"""
    if request.method == 'POST':
        ticket = get_object_or_404(SupportTicket, ticket_number=ticket_number)
        new_status = request.POST.get('status')
        notes = request.POST.get('notes', '')
        
        if new_status:
            old_status = ticket.status
            ticket.status = new_status
            ticket.save()
            
            # Crear mensaje del cambio
            message_content = f'Estado cambiado de "{ticket.get_status_display()}" a "{ticket.get_status_display()}"'
            if notes:
                message_content += f'\n\nNotas: {notes}'
            
            SupportMessage.objects.create(
                ticket=ticket,
                sender=request.user,
                content=message_content,
                message_type='status_change',
                is_ai_response=False
            )
            
            # Notificar al usuario
            notification_service = NotificationService()
            notification_service.notify_status_change(ticket, old_status, new_status)
            
            messages.success(request, 'Estado del ticket actualizado.')
    
    return redirect('support:admin_detail', ticket_number=ticket_number)


@user_passes_test(is_superuser)
def assign_ticket(request, ticket_number):
    """Asignar ticket a un usuario"""
    if request.method == 'POST':
        ticket = get_object_or_404(SupportTicket, ticket_number=ticket_number)
        user_id = request.POST.get('assigned_to')
        
        if user_id:
            assigned_user = get_object_or_404(User, id=user_id)
            ticket.assigned_to = assigned_user
        else:
            ticket.assigned_to = None
        
        ticket.save()
        
        # Crear mensaje de asignación
        if ticket.assigned_to:
            message_content = f'Ticket asignado a {ticket.assigned_to.username}'
        else:
            message_content = 'Ticket sin asignar'
        
        SupportMessage.objects.create(
            ticket=ticket,
            sender=request.user,
            content=message_content,
            message_type='assignment',
            is_ai_response=False
        )
        
        messages.success(request, 'Ticket asignado correctamente.')
    
    return redirect('support:admin_detail', ticket_number=ticket_number)


@user_passes_test(is_superuser)
def resolve_ticket(request, ticket_number):
    """Resolver ticket"""
    if request.method == 'POST':
        ticket = get_object_or_404(SupportTicket, ticket_number=ticket_number)
        resolution_message = request.POST.get('resolution_message', '')
        
        # Cambiar estado a resuelto
        old_status = ticket.status
        ticket.status = 'resolved'
        ticket.is_resolved = True
        ticket.save()
        
        # Crear mensaje de resolución
        if resolution_message:
            SupportMessage.objects.create(
                ticket=ticket,
                sender=request.user,
                content=resolution_message,
                message_type='resolution',
                is_ai_response=False
            )
        
        # Notificar resolución
        notification_service = NotificationService()
        notification_service.notify_ticket_resolved(ticket)
        
        messages.success(request, 'Ticket resuelto correctamente.')
    
    return redirect('support:admin_detail', ticket_number=ticket_number)


@user_passes_test(is_superuser)
def add_admin_message(request, ticket_number):
    """Agregar mensaje como administrador"""
    if request.method == 'POST':
        ticket = get_object_or_404(SupportTicket, ticket_number=ticket_number)
        content = request.POST.get('content')
        
        if content:
            message = SupportMessage.objects.create(
                ticket=ticket,
                sender=request.user,
                content=content,
                message_type='admin_response',
                is_ai_response=False
            )
            
            # Notificar al usuario
            notification_service = NotificationService()
            notification_service.notify_new_message(ticket, message)
            
            messages.success(request, 'Mensaje enviado correctamente.')
    
    return redirect('support:admin_detail', ticket_number=ticket_number)


@user_passes_test(is_superuser)
@require_http_methods(["POST"])
def admin_respond_ticket(request, ticket_number):
    """Responder a un ticket desde el panel administrativo"""
    ticket = get_object_or_404(SupportTicket, ticket_number=ticket_number)
    
    content = request.POST.get('content')
    new_status = request.POST.get('status')
    attachment = request.FILES.get('attachment')
    
    if content and content.strip():
        # Crear mensaje de respuesta del staff
        message = SupportMessage.objects.create(
            ticket=ticket,
            sender=request.user,
            content=content.strip(),
            is_ai_response=False,
            message_type='human',
            attachment=attachment
        )
        
        # Actualizar estado si se especifica
        if new_status and new_status != ticket.status:
            old_status = ticket.status
            ticket.status = new_status
            ticket.save()
            
            # Notificar cambio de estado
            NotificationService.notify_status_changed(ticket, old_status, ticket.status, request.user)
        
        # Notificar nueva respuesta
        NotificationService.notify_new_message(ticket, message)
        
        messages.success(request, 'Respuesta enviada exitosamente')
    else:
        messages.error(request, 'Debe incluir un mensaje de respuesta')
    
    return redirect('support:admin_detail', ticket_number=ticket.ticket_number)


@user_passes_test(is_superuser)
@require_http_methods(["POST"])
def update_ticket(request, ticket_number):
    """Actualizar múltiples campos de un ticket (estado, prioridad, asignación, etc.)"""
    ticket = get_object_or_404(SupportTicket, ticket_number=ticket_number)
    changes = []
    
    # Actualizar estado
    new_status = request.POST.get('status')
    if new_status and new_status != ticket.status:
        old_status = ticket.status
        old_status_display = ticket.get_status_display()
        ticket.status = new_status
        new_status_display = dict(SupportTicket.STATUS_CHOICES)[new_status]
        changes.append(f'Estado: {old_status_display} → {new_status_display}')
        
        # Notificar cambio de estado
        NotificationService.notify_status_changed(ticket, old_status, new_status, request.user)
    
    # Actualizar prioridad  
    new_priority = request.POST.get('priority')
    if new_priority and new_priority != ticket.priority:
        old_priority_display = ticket.get_priority_display()
        ticket.priority = new_priority
        new_priority_display = dict(SupportTicket.PRIORITY_CHOICES)[new_priority]
        changes.append(f'Prioridad: {old_priority_display} → {new_priority_display}')
    
    # Actualizar asignación
    assigned_to_id = request.POST.get('assigned_to')
    if assigned_to_id != str(ticket.assigned_to.id if ticket.assigned_to else ''):
        old_assigned = ticket.assigned_to.get_full_name() if ticket.assigned_to else 'Sin asignar'
        
        if assigned_to_id:
            new_assigned_user = get_object_or_404(User, id=assigned_to_id)
            ticket.assigned_to = new_assigned_user
            new_assigned = new_assigned_user.get_full_name()
            
            # Notificar asignación
            NotificationService.notify_ticket_assigned(ticket, new_assigned_user, request.user)
        else:
            ticket.assigned_to = None
            new_assigned = 'Sin asignar'
        
        changes.append(f'Asignación: {old_assigned} → {new_assigned}')
    
    # Guardar cambios
    if changes:
        ticket.save()
        
        # Crear mensaje de cambio
        message_content = 'Ticket actualizado:\n' + '\n'.join(f'• {change}' for change in changes)
        notes = request.POST.get('notes', '')
        if notes:
            message_content += f'\n\nNotas: {notes}'
        
        SupportMessage.objects.create(
            ticket=ticket,
            sender=request.user,
            content=message_content,
            message_type='admin_update',
            is_ai_response=False
        )
        
        messages.success(request, f'Ticket actualizado: {", ".join(changes)}')
    else:
        messages.info(request, 'No se realizaron cambios')
    
    return redirect('support:admin_detail', ticket_number=ticket_number)
