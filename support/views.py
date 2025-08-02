from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse
from django.views.generic import ListView
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

from .models import (
    SupportCategory, SupportTicket, SupportMessage, 
    SupportFAQ, AIConversationHistory, SupportNotification
)
from .forms import SupportTicketForm
from .ai_assistant import AIAssistant
from .decorators import superuser_required
from .notification_service import NotificationService
from django.contrib.auth.models import User


def support_home(request):
    """Página principal del centro de soporte"""
    recent_tickets = []
    if request.user.is_authenticated:
        recent_tickets = SupportTicket.objects.filter(
            user=request.user
        ).order_by('-updated_at')[:5]
    
    context = {
        'recent_tickets': recent_tickets,
    }
    return render(request, 'support/home.html', context)


@login_required
def create_ticket(request):
    """Crear un nuevo ticket de soporte"""
    if request.method == 'POST':
        form = SupportTicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            
            # Crear mensaje inicial del usuario
            SupportMessage.objects.create(
                ticket=ticket,
                sender=request.user,
                content=ticket.description,
                message_type='user'
            )
            
            # Enviar notificaciones
            NotificationService.notify_ticket_created(ticket)
            
            messages.success(
                request, 
                f'Ticket #{ticket.ticket_number} creado exitosamente. '
                f'Te contactaremos pronto.'
            )
            return redirect('support:ticket_detail', ticket_id=ticket.id)
    else:
        form = SupportTicketForm()
    
    return render(request, 'support/create_ticket.html', {'form': form})


@login_required
def ticket_detail(request, ticket_id):
    """Ver detalles de un ticket específico"""
    ticket = get_object_or_404(SupportTicket, id=ticket_id, user=request.user)
    messages_list = ticket.messages.all().order_by('created_at')
    
    # Marcar notificaciones como leídas
    NotificationService.mark_notifications_as_read(request.user, ticket)
    
    context = {
        'ticket': ticket,
        'messages': messages_list,
    }
    return render(request, 'support/ticket_detail.html', context)


@login_required
@require_http_methods(["POST"])
def send_message(request, ticket_id):
    """Enviar un mensaje a un ticket"""
    ticket = get_object_or_404(SupportTicket, id=ticket_id, user=request.user)
    
    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
            if data.get('request_ai_help'):
                # Solicitar ayuda de IA
                ai_assistant = AIAssistant()
                response_data = ai_assistant.generate_response(
                    f"Ayuda con ticket: {ticket.subject}. Descripción: {ticket.description}",
                    request.user
                )
                
                # Crear mensaje de IA
                message = SupportMessage.objects.create(
                    ticket=ticket,
                    sender=None,
                    content=response_data['response'],
                    is_ai_response=True,
                    message_type='ai'
                )
                
                ticket.updated_at = timezone.now()
                ticket.save()
                
                # Notificar al usuario sobre la respuesta de IA
                NotificationService.notify_new_message(ticket, message)
                
                return JsonResponse({'success': True})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'})
    else:
        # Mensaje normal del formulario
        content = request.POST.get('content')
        if content:
            SupportMessage.objects.create(
                ticket=ticket,
                sender=request.user,
                content=content,
                is_ai_response=False
            )
            
            ticket.updated_at = timezone.now()
            ticket.save()
            
            messages.success(request, 'Mensaje enviado correctamente.')
        
        return redirect('support:ticket_detail', ticket_id=ticket.id)


@login_required
@require_http_methods(["POST"])
def rate_ticket(request, ticket_id):
    """Calificar un ticket resuelto"""
    ticket = get_object_or_404(SupportTicket, id=ticket_id, user=request.user)
    
    rating = request.POST.get('rating')
    feedback = request.POST.get('feedback', '')
    
    if rating and rating.isdigit() and 1 <= int(rating) <= 5:
        ticket.rating = int(rating)
        ticket.feedback = feedback
        ticket.save()
        
        messages.success(request, '¡Gracias por tu calificación!')
    else:
        messages.error(request, 'Calificación inválida.')
    
    return redirect('support:ticket_detail', ticket_id=ticket.id)


class TicketListView(LoginRequiredMixin, ListView):
    """Lista de tickets del usuario"""
    model = SupportTicket
    template_name = 'support/ticket_list.html'
    context_object_name = 'tickets'
    paginate_by = 10
    
    def get_queryset(self):
        return SupportTicket.objects.filter(
            user=self.request.user
        ).order_by('-updated_at')


def faq_list(request):
    """Lista de preguntas frecuentes"""
    categories = SupportCategory.objects.filter(is_active=True)
    selected_category = None
    
    # Filtrar por categoría si se especifica
    category_id = request.GET.get('category')
    if category_id:
        try:
            selected_category = SupportCategory.objects.get(id=category_id)
            faqs = SupportFAQ.objects.filter(
                category=selected_category, 
                is_active=True
            )
        except SupportCategory.DoesNotExist:
            faqs = SupportFAQ.objects.filter(is_active=True)
    else:
        faqs = SupportFAQ.objects.filter(is_active=True)
    
    # Paginación
    paginator = Paginator(faqs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'faqs': page_obj,
        'categories': categories,
        'selected_category': selected_category,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
    }
    return render(request, 'support/faq_list.html', context)


def faq_detail(request, faq_id):
    """Detalle de una FAQ específica"""
    faq = get_object_or_404(SupportFAQ, id=faq_id, is_active=True)
    
    # Incrementar contador de vistas
    faq.view_count += 1
    faq.save(update_fields=['view_count'])
    
    context = {'faq': faq}
    return render(request, 'support/faq_detail.html', context)


@require_http_methods(["POST"])
def faq_vote(request, faq_id):
    """Votar si una FAQ fue útil o no"""
    faq = get_object_or_404(SupportFAQ, id=faq_id, is_active=True)
    
    try:
        data = json.loads(request.body)
        is_upvote = data.get('is_upvote')
        
        if is_upvote is True:
            faq.helpful_votes += 1
        elif is_upvote is False:
            faq.not_helpful_votes += 1
        
        faq.save(update_fields=['helpful_votes', 'not_helpful_votes'])
        
        return JsonResponse({
            'success': True,
            'upvotes': faq.helpful_votes,
            'downvotes': faq.not_helpful_votes
        })
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({'success': False, 'error': 'Invalid data'})


def quick_support(request):
    """Chat rápido con IA"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()
            
            if not user_message:
                return JsonResponse({
                    'success': False, 
                    'error': 'Mensaje vacío'
                })
            
            # Generar respuesta con IA
            ai_assistant = AIAssistant()
            response_data = ai_assistant.generate_response(
                user_message, 
                request.user if request.user.is_authenticated else None
            )
            
            # Guardar conversación si el usuario está autenticado
            if request.user.is_authenticated:
                session_id = request.session.get('ai_session_id')
                if not session_id:
                    # Crear nueva sesión de conversación
                    conversation = AIConversationHistory.objects.create(
                        user=request.user
                    )
                    session_id = str(conversation.session_id)
                    request.session['ai_session_id'] = session_id
                
                # Actualizar historial de conversación
                try:
                    conversation = AIConversationHistory.objects.get(
                        session_id=session_id
                    )
                    conversation_data = conversation.conversation_data
                    if 'messages' not in conversation_data:
                        conversation_data['messages'] = []
                    
                    conversation_data['messages'].extend([
                        {
                            'role': 'user',
                            'content': user_message,
                            'timestamp': timezone.now().isoformat()
                        },
                        {
                            'role': 'assistant',
                            'content': response_data['response'],
                            'timestamp': timezone.now().isoformat()
                        }
                    ])
                    
                    conversation.conversation_data = conversation_data
                    conversation.total_messages += 2
                    conversation.save()
                    
                except AIConversationHistory.DoesNotExist:
                    pass
            
            return JsonResponse({
                'success': True,
                'response': response_data['response']
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Error en el formato de datos'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': 'Error interno del servidor'
            })
    
    # GET request - mostrar página de chat
    return render(request, 'support/quick_support.html', {
        'now': timezone.now()
    })


@login_required
def notifications(request):
    """Ver notificaciones del usuario"""
    user_notifications = SupportNotification.objects.filter(
        user=request.user
    ).order_by('-created_at')
    
    # Marcar todas como leídas cuando se visita la página
    unread_count = user_notifications.filter(is_read=False).count()
    user_notifications.filter(is_read=False).update(is_read=True)
    
    # Paginación
    paginator = Paginator(user_notifications, 20)
    page = request.GET.get('page')
    notifications_page = paginator.get_page(page)
    
    context = {
        'notifications': notifications_page,
        'unread_count': unread_count,
    }
    return render(request, 'support/notifications.html', context)


@login_required
def get_unread_notifications_count(request):
    """API para obtener el número de notificaciones no leídas"""
    count = SupportNotification.objects.filter(
        user=request.user, 
        is_read=False
    ).count()
    
    return JsonResponse({'count': count})


# ========================================
# VISTAS ADMINISTRATIVAS (SOLO SUPERUSUARIOS)
# ========================================

@superuser_required
def admin_ticket_dashboard(request):
    """Dashboard principal para gestión de tickets por superusuarios"""
    # Estadísticas generales
    total_tickets = SupportTicket.objects.count()
    open_tickets = SupportTicket.objects.filter(status='open').count()
    in_progress_tickets = SupportTicket.objects.filter(status='in_progress').count()
    resolved_tickets = SupportTicket.objects.filter(status='resolved').count()
    closed_tickets = SupportTicket.objects.filter(status='closed').count()
    
    # Tickets recientes
    recent_tickets = SupportTicket.objects.all().order_by('-created_at')[:10]
    
    # Tickets por prioridad
    urgent_tickets = SupportTicket.objects.filter(priority='urgent').count()
    high_tickets = SupportTicket.objects.filter(priority='high').count()
    
    # Tickets sin asignar
    unassigned_tickets = SupportTicket.objects.filter(assigned_to__isnull=True).count()
    
    context = {
        'total_tickets': total_tickets,
        'open_tickets': open_tickets,
        'in_progress_tickets': in_progress_tickets,
        'resolved_tickets': resolved_tickets,
        'closed_tickets': closed_tickets,
        'recent_tickets': recent_tickets,
        'urgent_tickets': urgent_tickets,
        'high_tickets': high_tickets,
        'unassigned_tickets': unassigned_tickets,
    }
    
    return render(request, 'support/admin/dashboard.html', context)


@superuser_required
def admin_ticket_list(request):
    """Lista completa de tickets para administración"""
    tickets = SupportTicket.objects.all().select_related('user', 'category', 'assigned_to')
    
    # Filtros
    status_filter = request.GET.get('status')
    priority_filter = request.GET.get('priority')
    category_filter = request.GET.get('category')
    assigned_filter = request.GET.get('assigned')
    search_query = request.GET.get('search')
    
    if status_filter:
        tickets = tickets.filter(status=status_filter)
    
    if priority_filter:
        tickets = tickets.filter(priority=priority_filter)
    
    if category_filter:
        tickets = tickets.filter(category_id=category_filter)
    
    if assigned_filter == 'unassigned':
        tickets = tickets.filter(assigned_to__isnull=True)
    elif assigned_filter and assigned_filter != 'all':
        tickets = tickets.filter(assigned_to_id=assigned_filter)
    
    if search_query:
        tickets = tickets.filter(
            Q(ticket_number__icontains=search_query) |
            Q(subject__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(user__email__icontains=search_query)
        )
    
    # Ordenamiento
    order_by = request.GET.get('order_by', '-created_at')
    tickets = tickets.order_by(order_by)
    
    # Paginación
    paginator = Paginator(tickets, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Datos para filtros
    categories = SupportCategory.objects.filter(is_active=True)
    staff_users = User.objects.filter(is_staff=True)
    
    context = {
        'tickets': page_obj,
        'categories': categories,
        'staff_users': staff_users,
        'current_filters': {
            'status': status_filter,
            'priority': priority_filter,
            'category': category_filter,
            'assigned': assigned_filter,
            'search': search_query,
            'order_by': order_by,
        },
        'status_choices': SupportTicket.STATUS_CHOICES,
        'priority_choices': SupportTicket.PRIORITY_CHOICES,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
    }
    
    return render(request, 'support/admin/ticket_list.html', context)


@superuser_required
def admin_ticket_detail(request, ticket_id):
    """Vista detallada de un ticket para administración"""
    ticket = get_object_or_404(SupportTicket, id=ticket_id)
    messages_list = ticket.messages.all().order_by('created_at')
    staff_users = User.objects.filter(is_staff=True)
    
    context = {
        'ticket': ticket,
        'messages': messages_list,
        'staff_users': staff_users,
        'status_choices': SupportTicket.STATUS_CHOICES,
        'priority_choices': SupportTicket.PRIORITY_CHOICES,
    }
    
    return render(request, 'support/admin/ticket_detail.html', context)


@superuser_required
@require_http_methods(["POST"])
def admin_update_ticket(request, ticket_id):
    """Actualizar un ticket desde el panel administrativo"""
    ticket = get_object_or_404(SupportTicket, id=ticket_id)
    
    # Guardar estados originales para comparación
    old_status = ticket.status
    old_assigned_to = ticket.assigned_to
    
    # Actualizar campos básicos
    new_status = request.POST.get('status')
    new_priority = request.POST.get('priority')
    assigned_to_id = request.POST.get('assigned_to')
    admin_notes = request.POST.get('admin_notes')
    
    if new_status and new_status in dict(SupportTicket.STATUS_CHOICES):
        ticket.status = new_status
        
        # Marcar como resuelto si cambia a resolved
        if new_status == 'resolved' and old_status != 'resolved':
            ticket.is_resolved = True
            ticket.resolved_at = timezone.now()
        
        # Notificar cambio de estado
        if old_status != new_status:
            NotificationService.notify_status_changed(ticket, old_status, new_status, request.user)
        
        messages.success(request, f'Estado del ticket actualizado a {ticket.get_status_display()}')
    
    if new_priority and new_priority in dict(SupportTicket.PRIORITY_CHOICES):
        ticket.priority = new_priority
        messages.success(request, f'Prioridad actualizada a {ticket.get_priority_display()}')
    
    if assigned_to_id:
        if assigned_to_id == 'unassign':
            ticket.assigned_to = None
            messages.success(request, 'Ticket desasignado')
        else:
            try:
                user = User.objects.get(id=assigned_to_id, is_staff=True)
                ticket.assigned_to = user
                messages.success(request, f'Ticket asignado a {user.get_full_name() or user.username}')
            except User.DoesNotExist:
                messages.error(request, 'Usuario no válido para asignación')
        
        # Notificar cambio de asignación
        if old_assigned_to != ticket.assigned_to:
            NotificationService.notify_ticket_assigned(ticket, ticket.assigned_to, request.user)
    
    # Agregar nota administrativa si se proporcionó
    if admin_notes and admin_notes.strip():
        message = SupportMessage.objects.create(
            ticket=ticket,
            sender=request.user,
            content=f"[NOTA ADMINISTRATIVA] {admin_notes.strip()}",
            is_ai_response=False,
            message_type='system',
            is_internal=True  # Solo visible para staff
        )
        messages.success(request, 'Nota administrativa agregada')
    
    ticket.updated_at = timezone.now()
    ticket.save()
    
    return redirect('support:admin_detail', ticket_number=ticket.ticket_number)


@superuser_required
@require_http_methods(["POST"])
def admin_respond_ticket(request, ticket_id):
    """Responder a un ticket desde el panel administrativo"""
    ticket = get_object_or_404(SupportTicket, id=ticket_id)
    
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
        
        # Guardar estado anterior
        old_status = ticket.status
        
        # Cambiar estado si es necesario
        if ticket.status == 'open':
            ticket.status = 'in_progress'
        
        # Aplicar nuevo estado si se especificó
        if new_status and new_status in dict(SupportTicket.STATUS_CHOICES):
            ticket.status = new_status
            
            # Marcar como resuelto si cambia a resolved
            if new_status == 'resolved':
                ticket.is_resolved = True
                ticket.resolved_at = timezone.now()
        
        ticket.updated_at = timezone.now()
        ticket.save()
        
        # Notificar al usuario sobre la nueva respuesta
        NotificationService.notify_new_message(ticket, message)
        
        # Notificar cambio de estado si aplica
        if old_status != ticket.status:
            NotificationService.notify_status_changed(ticket, old_status, ticket.status, request.user)
        
        messages.success(request, 'Respuesta enviada exitosamente')
    else:
        messages.error(request, 'Debe incluir un mensaje de respuesta')
    
    return redirect('support:admin_detail', ticket_number=ticket.ticket_number)


@superuser_required
@require_http_methods(["POST"])
def admin_bulk_actions(request):
    """Acciones en lote para múltiples tickets"""
    ticket_ids = request.POST.getlist('ticket_ids')
    action = request.POST.get('bulk_action')
    
    if not ticket_ids:
        messages.error(request, 'No se seleccionaron tickets')
        return redirect('support:admin_ticket_list')
    
    tickets = SupportTicket.objects.filter(id__in=ticket_ids)
    count = tickets.count()
    
    if action == 'mark_in_progress':
        tickets.update(status='in_progress', updated_at=timezone.now())
        messages.success(request, f'{count} tickets marcados como "En Progreso"')
    
    elif action == 'mark_resolved':
        tickets.update(
            status='resolved', 
            is_resolved=True, 
            resolved_at=timezone.now(),
            updated_at=timezone.now()
        )
        messages.success(request, f'{count} tickets marcados como "Resueltos"')
    
    elif action == 'assign_to_me':
        tickets.update(assigned_to=request.user, updated_at=timezone.now())
        messages.success(request, f'{count} tickets asignados a ti')
    
    elif action == 'unassign':
        tickets.update(assigned_to=None, updated_at=timezone.now())
        messages.success(request, f'{count} tickets desasignados')
    
    else:
        messages.error(request, 'Acción no válida')
    
    return redirect('support:admin_ticket_list')
