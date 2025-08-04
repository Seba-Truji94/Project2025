"""
Vistas para el sistema de notificaciones
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.urls import reverse_lazy
from .models import (
    Notification, UserNotificationPreference, 
    NotificationTemplate, NotificationStatus
)
from .services import NotificationFactory
from .forms import NotificationPreferenceForm, BulkNotificationForm
import json


@login_required
def notification_preferences(request):
    """Vista para gestionar preferencias de notificación del usuario"""
    preferences, created = UserNotificationPreference.objects.get_or_create(
        user=request.user
    )
    
    if request.method == 'POST':
        form = NotificationPreferenceForm(request.POST, instance=preferences)
        if form.is_valid():
            form.save()
            messages.success(request, 'Preferencias de notificación actualizadas correctamente.')
            return redirect('notifications:preferences')
    else:
        form = NotificationPreferenceForm(instance=preferences)
    
    return render(request, 'notifications/preferences.html', {
        'form': form,
        'preferences': preferences
    })


class NotificationListView(LoginRequiredMixin, ListView):
    """Lista de notificaciones del usuario"""
    model = Notification
    template_name = 'notifications/list.html'
    context_object_name = 'notifications'
    paginate_by = 20
    
    def get_queryset(self):
        return Notification.objects.filter(
            user=self.request.user
        ).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estadísticas
        user_notifications = Notification.objects.filter(user=self.request.user)
        context['stats'] = {
            'total': user_notifications.count(),
            'unread': user_notifications.filter(status__in=['pending', 'sent', 'delivered']).count(),
            'failed': user_notifications.filter(status='failed').count(),
        }
        
        return context


class NotificationDetailView(LoginRequiredMixin, DetailView):
    """Detalle de una notificación"""
    model = Notification
    template_name = 'notifications/detail.html'
    context_object_name = 'notification'
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Marcar como leída cuando se visualiza
        if obj.status != NotificationStatus.READ:
            obj.mark_as_read()
        return obj


@login_required
@require_POST
def mark_notification_read(request, notification_id):
    """Marcar notificación como leída vía AJAX"""
    try:
        notification = get_object_or_404(
            Notification, 
            id=notification_id, 
            user=request.user
        )
        notification.mark_as_read()
        
        return JsonResponse({
            'success': True,
            'message': 'Notificación marcada como leída'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@require_POST
def mark_all_read(request):
    """Marcar todas las notificaciones como leídas"""
    try:
        updated = Notification.objects.filter(
            user=request.user,
            status__in=['pending', 'sent', 'delivered']
        ).update(
            status=NotificationStatus.READ,
            read_at=timezone.now()
        )
        
        return JsonResponse({
            'success': True,
            'message': f'{updated} notificaciones marcadas como leídas'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
def test_notification(request):
    """Vista para enviar notificación de prueba"""
    if request.method == 'POST':
        channels = request.POST.getlist('channels[]')
        if not channels:
            channels = ['email']
        
        try:
            results = NotificationFactory.send_multi_channel_notification(
                user=request.user,
                notification_type='welcome',
                subject='🧪 Notificación de Prueba - Galletas Kati',
                message=f'Hola {request.user.first_name}, esta es una notificación de prueba para verificar que tu configuración funciona correctamente.',
                channels=channels,
                extra_data={'test': True}
            )
            
            success_channels = [ch for ch, success in results.items() if success]
            failed_channels = [ch for ch, success in results.items() if not success]
            
            if success_channels:
                messages.success(
                    request, 
                    f'Notificación de prueba enviada exitosamente por: {", ".join(success_channels)}'
                )
            
            if failed_channels:
                messages.warning(
                    request,
                    f'Error enviando por: {", ".join(failed_channels)}'
                )
            
        except Exception as e:
            messages.error(request, f'Error enviando notificación de prueba: {str(e)}')
    
    return render(request, 'notifications/test.html')


# Webhook para recibir estados de entrega (ej: desde Twilio, WhatsApp Business)
@csrf_exempt
def delivery_webhook(request):
    """Webhook para recibir confirmaciones de entrega"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        external_id = data.get('MessageSid') or data.get('id')
        status = data.get('MessageStatus') or data.get('status')
        
        if external_id:
            notifications = Notification.objects.filter(external_id=external_id)
            
            for notification in notifications:
                if status == 'delivered':
                    notification.mark_as_delivered()
                elif status == 'failed':
                    notification.mark_as_failed(data.get('ErrorMessage', 'Delivery failed'))
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


# === VISTAS PARA ADMINISTRADORES ===

from django.utils.decorators import method_decorator


@method_decorator(staff_member_required, name='dispatch')
class AdminNotificationListView(ListView):
    """Lista de todas las notificaciones para administradores"""
    model = Notification
    template_name = 'notifications/admin/list.html'
    context_object_name = 'notifications'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = Notification.objects.all().select_related('user').order_by('-created_at')
        
        # Filtros
        status = self.request.GET.get('status')
        channel = self.request.GET.get('channel')
        notification_type = self.request.GET.get('type')
        
        if status:
            queryset = queryset.filter(status=status)
        if channel:
            queryset = queryset.filter(channel=channel)
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estadísticas generales
        all_notifications = Notification.objects.all()
        context['stats'] = {
            'total': all_notifications.count(),
            'pending': all_notifications.filter(status='pending').count(),
            'sent': all_notifications.filter(status='sent').count(),
            'failed': all_notifications.filter(status='failed').count(),
        }
        
        # Para filtros
        context['statuses'] = NotificationStatus.choices
        context['channels'] = [('email', 'Email'), ('sms', 'SMS'), ('whatsapp', 'WhatsApp')]
        
        return context


@staff_member_required
def admin_send_bulk_notification(request):
    """Vista para enviar notificaciones masivas"""
    if request.method == 'POST':
        form = BulkNotificationForm(request.POST)
        if form.is_valid():
            try:
                # Enviar notificación masiva usando Celery
                from .tasks import send_bulk_notification
                
                user_ids = list(form.cleaned_data['recipients'].values_list('id', flat=True))
                
                task = send_bulk_notification.delay(
                    user_ids=user_ids,
                    notification_type=form.cleaned_data['notification_type'],
                    subject=form.cleaned_data['subject'],
                    message=form.cleaned_data['message'],
                    channels=form.cleaned_data['channels']
                )
                
                messages.success(
                    request, 
                    f'Notificación masiva enviada a {len(user_ids)} usuarios. Task ID: {task.id}'
                )
                return redirect('notifications:admin_bulk')
                
            except ImportError:
                # Fallback sin Celery
                from .services import NotificationFactory
                sent_count = 0
                
                for user in form.cleaned_data['recipients']:
                    results = NotificationFactory.send_multi_channel_notification(
                        user=user,
                        notification_type=form.cleaned_data['notification_type'],
                        subject=form.cleaned_data['subject'],
                        message=form.cleaned_data['message'],
                        channels=form.cleaned_data['channels']
                    )
                    if any(results.values()):
                        sent_count += 1
                
                messages.success(request, f'Notificación enviada a {sent_count} usuarios')
                return redirect('notifications:admin_bulk')
                
    else:
        form = BulkNotificationForm()
    
    return render(request, 'notifications/admin/bulk.html', {'form': form})


@staff_member_required
def admin_notification_stats(request):
    """Dashboard de estadísticas de notificaciones"""
    from django.db.models import Count, Q
    from datetime import datetime, timedelta
    
    # Estadísticas de los últimos 30 días
    thirty_days_ago = datetime.now() - timedelta(days=30)
    
    stats = {
        'total_notifications': Notification.objects.count(),
        'last_30_days': Notification.objects.filter(created_at__gte=thirty_days_ago).count(),
        'by_status': Notification.objects.values('status').annotate(count=Count('id')),
        'by_channel': Notification.objects.values('channel').annotate(count=Count('id')),
        'by_type': Notification.objects.values('notification_type').annotate(count=Count('id')),
        'success_rate': 0,
    }
    
    # Calcular tasa de éxito
    total = stats['total_notifications']
    if total > 0:
        successful = Notification.objects.filter(
            status__in=['sent', 'delivered', 'read']
        ).count()
        stats['success_rate'] = round((successful / total) * 100, 2)
    
    return render(request, 'notifications/admin/stats.html', {'stats': stats})
