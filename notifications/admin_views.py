"""
Vistas administrativas para el sistema de notificaciones
Solo accesible para superusuarios
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime, timedelta

from .models import (
    Notification, 
    UserNotificationPreference, 
    NotificationTemplate,
    NotificationLog,
    NotificationQueue
)
from .services import NotificationService
from .forms import BulkNotificationForm, NotificationTemplateForm


def is_superuser(user):
    """Verificar que el usuario sea superusuario"""
    return user.is_superuser


@login_required
@user_passes_test(is_superuser)
def admin_dashboard(request):
    """Dashboard principal de administración de notificaciones"""
    
    # Estadísticas generales
    stats = {
        'total_notifications': Notification.objects.count(),
        'pending_notifications': Notification.objects.filter(status='pending').count(),
        'sent_today': Notification.objects.filter(
            sent_at__date=timezone.now().date()
        ).count(),
        'failed_notifications': Notification.objects.filter(status='failed').count(),
        'total_users': User.objects.count(),
        'users_with_preferences': UserNotificationPreference.objects.values('user').distinct().count(),
    }
    
    # Notificaciones recientes
    recent_notifications = Notification.objects.select_related('user').order_by('-created_at')[:10]
    
    # Estadísticas por canal
    channel_stats = Notification.objects.values('channel').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Notificaciones por día (últimos 7 días)
    seven_days_ago = timezone.now() - timedelta(days=7)
    daily_stats = []
    for i in range(7):
        date = seven_days_ago + timedelta(days=i)
        count = Notification.objects.filter(
            created_at__date=date.date()
        ).count()
        daily_stats.append({
            'date': date.strftime('%Y-%m-%d'),
            'count': count
        })
    
    context = {
        'stats': stats,
        'recent_notifications': recent_notifications,
        'channel_stats': channel_stats,
        'daily_stats': daily_stats,
    }
    
    return render(request, 'notifications/admin/dashboard.html', context)


@login_required
@user_passes_test(is_superuser)
def bulk_send(request):
    """Envío masivo de notificaciones"""
    
    if request.method == 'POST':
        form = BulkNotificationForm(request.POST)
        if form.is_valid():
            # Obtener usuarios según los filtros
            users = User.objects.all()
            
            if form.cleaned_data['user_filter'] == 'active':
                users = users.filter(is_active=True)
            elif form.cleaned_data['user_filter'] == 'staff':
                users = users.filter(is_staff=True)
            elif form.cleaned_data['user_filter'] == 'has_orders':
                # Usuarios que han hecho pedidos
                users = users.filter(orders__isnull=False).distinct()
            
            # Enviar notificaciones
            sent_count = 0
            for user in users:
                try:
                    NotificationService.send_notification(
                        user=user,
                        notification_type=form.cleaned_data['notification_type'],
                        message=form.cleaned_data['message'],
                        channels=form.cleaned_data['channels'],
                        extra_data=form.cleaned_data.get('extra_data', {})
                    )
                    sent_count += 1
                except Exception as e:
                    messages.error(request, f'Error enviando a {user.username}: {str(e)}')
            
            messages.success(request, f'Notificaciones enviadas a {sent_count} usuarios')
            return redirect('notifications:admin_dashboard')
    else:
        form = BulkNotificationForm()
    
    return render(request, 'notifications/admin/bulk_send.html', {'form': form})


@login_required
@user_passes_test(is_superuser)
def notification_logs(request):
    """Ver logs de notificaciones"""
    
    # Filtros
    status_filter = request.GET.get('status', '')
    channel_filter = request.GET.get('channel', '')
    date_filter = request.GET.get('date', '')
    user_filter = request.GET.get('user', '')
    
    logs = NotificationLog.objects.select_related('notification', 'notification__user').order_by('-timestamp')
    
    if status_filter:
        logs = logs.filter(status=status_filter)
    if channel_filter:
        logs = logs.filter(channel=channel_filter)
    if date_filter:
        logs = logs.filter(timestamp__date=date_filter)
    if user_filter:
        logs = logs.filter(notification__user__username__icontains=user_filter)
    
    # Paginación
    paginator = Paginator(logs, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'channel_filter': channel_filter,
        'date_filter': date_filter,
        'user_filter': user_filter,
    }
    
    return render(request, 'notifications/admin/logs.html', context)


@login_required
@user_passes_test(is_superuser)
def template_management(request):
    """Gestión de plantillas de notificación"""
    
    templates = NotificationTemplate.objects.all().order_by('name')
    
    return render(request, 'notifications/admin/templates.html', {
        'templates': templates
    })


@login_required
@user_passes_test(is_superuser)
def template_create(request):
    """Crear nueva plantilla"""
    
    if request.method == 'POST':
        form = NotificationTemplateForm(request.POST)
        if form.is_valid():
            template = form.save()
            messages.success(request, f'Plantilla "{template.name}" creada exitosamente')
            return redirect('notifications_admin:templates')
    else:
        form = NotificationTemplateForm()
    
    return render(request, 'notifications/admin/template_form.html', {
        'form': form,
        'title': 'Crear Nueva Plantilla'
    })


@login_required
@user_passes_test(is_superuser)
def template_edit(request, template_id):
    """Editar plantilla existente"""
    
    template = get_object_or_404(NotificationTemplate, id=template_id)
    
    if request.method == 'POST':
        form = NotificationTemplateForm(request.POST, instance=template)
        if form.is_valid():
            template = form.save()
            messages.success(request, f'Plantilla "{template.name}" actualizada exitosamente')
            return redirect('notifications:admin_templates')
    else:
        form = NotificationTemplateForm(instance=template)
    
    return render(request, 'notifications/admin/template_form.html', {
        'form': form,
        'template': template,
        'title': f'Editar Plantilla: {template.name}'
    })


@login_required
@user_passes_test(is_superuser)
def user_preferences(request):
    """Gestión de preferencias de usuarios"""
    
    search = request.GET.get('search', '')
    
    users = User.objects.all()
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    # Agregar información de preferencias
    users_with_prefs = []
    for user in users:
        try:
            prefs = UserNotificationPreference.objects.get(user=user)
        except UserNotificationPreference.DoesNotExist:
            prefs = None
        
        users_with_prefs.append({
            'user': user,
            'preferences': prefs,
            'notification_count': Notification.objects.filter(user=user).count()
        })
    
    # Paginación
    paginator = Paginator(users_with_prefs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'notifications/admin/user_preferences.html', {
        'page_obj': page_obj,
        'search': search
    })


@login_required
@user_passes_test(is_superuser)
def system_status(request):
    """Estado del sistema de notificaciones"""
    
    # Verificar configuración
    config_status = NotificationService.test_configuration()
    
    # Estadísticas de rendimiento
    now = timezone.now()
    last_hour = now - timedelta(hours=1)
    last_day = now - timedelta(days=1)
    
    performance_stats = {
        'notifications_last_hour': Notification.objects.filter(
            created_at__gte=last_hour
        ).count(),
        'notifications_last_day': Notification.objects.filter(
            created_at__gte=last_day
        ).count(),
        'failed_last_hour': Notification.objects.filter(
            created_at__gte=last_hour,
            status='failed'
        ).count(),
        'pending_notifications': Notification.objects.filter(
            status='pending'
        ).count(),
    }
    
    # Queue status
    queue_stats = {
        'queued_notifications': NotificationQueue.objects.filter(
            processed_at__isnull=True
        ).count(),
        'failed_queue_items': NotificationQueue.objects.filter(
            status='failed'
        ).count(),
    }
    
    return render(request, 'notifications/admin/system_status.html', {
        'config_status': config_status,
        'performance_stats': performance_stats,
        'queue_stats': queue_stats,
    })


@login_required
@user_passes_test(is_superuser)
@require_POST
def retry_failed_notifications(request):
    """Reintentar notificaciones fallidas"""
    
    failed_notifications = Notification.objects.filter(status='failed')
    retry_count = 0
    
    for notification in failed_notifications:
        try:
            # Reintentar envío
            success = NotificationService._retry_notification(notification)
            if success:
                retry_count += 1
        except Exception as e:
            continue
    
    return JsonResponse({
        'success': True,
        'message': f'Se reintentaron {retry_count} notificaciones',
        'retry_count': retry_count
    })


@login_required
@user_passes_test(is_superuser)
@require_POST
def clear_old_logs(request):
    """Limpiar logs antiguos"""
    
    days = int(request.POST.get('days', 30))
    cutoff_date = timezone.now() - timedelta(days=days)
    
    deleted_count = NotificationLog.objects.filter(
        timestamp__lt=cutoff_date
    ).delete()[0]
    
    return JsonResponse({
        'success': True,
        'message': f'Se eliminaron {deleted_count} logs antiguos',
        'deleted_count': deleted_count
    })


@login_required
@user_passes_test(is_superuser)
def export_notifications(request):
    """Exportar notificaciones a CSV"""
    
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="notificaciones.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Usuario', 'Tipo', 'Canal', 'Estado', 
        'Fecha Creación', 'Fecha Envío', 'Mensaje'
    ])
    
    notifications = Notification.objects.select_related('user').order_by('-created_at')
    
    for notification in notifications:
        writer.writerow([
            notification.id,
            notification.user.username if notification.user else 'N/A',
            notification.get_notification_type_display(),
            notification.get_channel_display(),
            notification.get_status_display(),
            notification.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            notification.sent_at.strftime('%Y-%m-%d %H:%M:%S') if notification.sent_at else 'N/A',
            notification.message[:100] + '...' if len(notification.message) > 100 else notification.message
        ])
    
    return response


@login_required
@user_passes_test(is_superuser)
def template_delete(request, template_id):
    """Eliminar plantilla de notificación"""
    try:
        template = NotificationTemplate.objects.get(id=template_id)
    except NotificationTemplate.DoesNotExist:
        messages.error(request, 'Plantilla no encontrada.')
        return redirect('notifications_admin:templates')
    
    if request.method == 'POST':
        template_name = template.name
        template.delete()
        messages.success(request, f'Plantilla "{template_name}" eliminada exitosamente.')
        return redirect('notifications_admin:templates')
    
    context = {
        'template': template,
        'title': 'Eliminar Plantilla'
    }
    
    return render(request, 'notifications/admin/template_confirm_delete.html', context)


@login_required
@user_passes_test(is_superuser)
def template_preview(request, template_id):
    """Vista previa de plantilla"""
    try:
        template = NotificationTemplate.objects.get(id=template_id)
    except NotificationTemplate.DoesNotExist:
        messages.error(request, 'Plantilla no encontrada.')
        return redirect('notifications_admin:templates')
    
    # Variables de ejemplo para la vista previa
    example_vars = {
        'user': {
            'first_name': 'Juan',
            'last_name': 'Pérez',
            'email': 'juan.perez@example.com'
        },
        'company': 'Galletas Kati',
        'date': timezone.now().strftime('%d/%m/%Y'),
        'time': timezone.now().strftime('%H:%M')
    }
    
    try:
        # Renderizar plantilla con variables de ejemplo
        rendered_content = template.template_body
        for key, value in example_vars.items():
            if isinstance(value, dict):
                for subkey, subvalue in value.items():
                    rendered_content = rendered_content.replace(f'{{{key}.{subkey}}}', str(subvalue))
            else:
                rendered_content = rendered_content.replace(f'{{{key}}}', str(value))
        
        context = {
            'template': template,
            'rendered_content': rendered_content,
            'example_vars': example_vars
        }
        
        return render(request, 'notifications/admin/template_preview.html', context)
        
    except Exception as e:
        messages.error(request, f'Error al generar vista previa: {str(e)}')
        return redirect('notifications_admin:templates')


@login_required
@user_passes_test(is_superuser)
def user_preference_detail(request, user_id):
    """Detalle y edición de preferencias de un usuario específico"""
    try:
        user = User.objects.get(id=user_id)
        preference, created = UserNotificationPreference.objects.get_or_create(user=user)
    except User.DoesNotExist:
        messages.error(request, 'Usuario no encontrado.')
        return redirect('notifications_admin:user_preferences')
    
    if request.method == 'POST':
        from .admin_forms import AdminUserPreferenceForm
        form = AdminUserPreferenceForm(request.POST, instance=preference)
        if form.is_valid():
            form.save()
            messages.success(request, f'Preferencias de {user.username} actualizadas exitosamente.')
            return redirect('notifications_admin:user_preferences')
    else:
        from .admin_forms import AdminUserPreferenceForm
        form = AdminUserPreferenceForm(instance=preference)
    
    # Estadísticas del usuario
    user_stats = {
        'total_notifications': Notification.objects.filter(recipient=user).count(),
        'sent_notifications': Notification.objects.filter(recipient=user, status='sent').count(),
        'failed_notifications': Notification.objects.filter(recipient=user, status='failed').count(),
        'recent_notifications': Notification.objects.filter(recipient=user).order_by('-created_at')[:10]
    }
    
    context = {
        'selected_user': user,
        'form': form,
        'user_stats': user_stats,
        'title': f'Preferencias de {user.username}'
    }
    
    return render(request, 'notifications/admin/user_preference_detail.html', context)


@login_required
@user_passes_test(is_superuser)
def export_user_preferences(request):
    """Exportar preferencias de usuarios a CSV"""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="preferencias_usuarios.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Usuario', 'Email', 'Email Habilitado', 'SMS Habilitado', 
        'WhatsApp Habilitado', 'Push Habilitado', 'Teléfono', 'WhatsApp',
        'Fecha Registro'
    ])
    
    preferences = UserNotificationPreference.objects.select_related('user').all()
    
    for pref in preferences:
        writer.writerow([
            pref.user.username,
            pref.user.email,
            'Sí' if pref.email_enabled else 'No',
            'Sí' if pref.sms_enabled else 'No',
            'Sí' if pref.whatsapp_enabled else 'No',
            'Sí' if pref.push_enabled else 'No',
            pref.phone_number or 'N/A',
            pref.whatsapp_number or 'N/A',
            pref.created_at.strftime('%Y-%m-%d') if pref.created_at else 'N/A'
        ])
    
    return response


@login_required
@user_passes_test(is_superuser)
def campaign_management(request):
    """Gestión de campañas de notificación"""
    
    context = {
        'title': 'Gestión de Campañas',
        'campaigns': [],  # Implementar modelo Campaign si es necesario
        'total_campaigns': 0,
        'active_campaigns': 0,
        'scheduled_campaigns': 0
    }
    
    return render(request, 'notifications/admin/campaigns.html', context)


@login_required
@user_passes_test(is_superuser)
def campaign_create(request):
    """Crear nueva campaña"""
    
    if request.method == 'POST':
        from .admin_forms import AdminCampaignForm
        form = AdminCampaignForm(request.POST)
        if form.is_valid():
            # Aquí iría la lógica para crear la campaña
            messages.success(request, 'Campaña creada exitosamente.')
            return redirect('notifications_admin:campaigns')
    else:
        from .admin_forms import AdminCampaignForm
        form = AdminCampaignForm()
    
    context = {
        'form': form,
        'title': 'Nueva Campaña'
    }
    
    return render(request, 'notifications/admin/campaign_form.html', context)


@login_required
@user_passes_test(is_superuser)
def campaign_detail(request, campaign_id):
    """Detalle de campaña específica"""
    
    context = {
        'campaign_id': campaign_id,
        'title': f'Campaña #{campaign_id}'
    }
    
    return render(request, 'notifications/admin/campaign_detail.html', context)


@login_required
@user_passes_test(is_superuser)
def system_config(request):
    """Configuración del sistema de notificaciones"""
    
    if request.method == 'POST':
        from .admin_forms import AdminSystemConfigForm
        form = AdminSystemConfigForm(request.POST)
        if form.is_valid():
            # Aquí iría la lógica para guardar configuración
            messages.success(request, 'Configuración guardada exitosamente.')
            return redirect('notifications_admin:system_status')
    else:
        from .admin_forms import AdminSystemConfigForm
        form = AdminSystemConfigForm()
    
    context = {
        'form': form,
        'title': 'Configuración del Sistema'
    }
    
    return render(request, 'notifications/admin/system_config.html', context)


@login_required
@user_passes_test(is_superuser)
def test_notification(request):
    """Enviar notificación de prueba"""
    
    if request.method == 'POST':
        from .admin_forms import AdminTestNotificationForm
        form = AdminTestNotificationForm(request.POST)
        if form.is_valid():
            try:
                channel = form.cleaned_data['channel']
                recipient = form.cleaned_data['recipient']
                message = form.cleaned_data['message']
                include_info = form.cleaned_data['include_system_info']
                
                if include_info:
                    message += f"\n\n--- INFO DEL SISTEMA ---\nFecha: {timezone.now()}\nUsuario: {request.user.username}\nIP: {request.META.get('REMOTE_ADDR', 'Unknown')}"
                
                # Crear notificación de prueba
                notification = Notification.objects.create(
                    recipient=request.user,  # Enviar al admin que está haciendo la prueba
                    notification_type='system',
                    channel=channel,
                    subject='🧪 Prueba del Sistema de Notificaciones',
                    message=message,
                    extra_data={'test': True, 'admin_user': request.user.username}
                )
                
                # Enviar inmediatamente
                from .services import NotificationService
                service = NotificationService()
                success = service.send_notification(notification)
                
                if success:
                    messages.success(request, f'Notificación de prueba enviada exitosamente a {recipient} por {channel}.')
                else:
                    messages.error(request, 'Error al enviar la notificación de prueba.')
                    
            except Exception as e:
                messages.error(request, f'Error al procesar la prueba: {str(e)}')
                
            return redirect('notifications_admin:test')
    else:
        from .admin_forms import AdminTestNotificationForm
        form = AdminTestNotificationForm()
    
    context = {
        'form': form,
        'title': 'Prueba de Notificaciones'
    }
    
    return render(request, 'notifications/admin/test_notification.html', context)


@login_required
@user_passes_test(is_superuser)
def analytics_dashboard(request):
    """Dashboard de análisis y estadísticas"""
    from datetime import datetime, timedelta
    from django.db.models import Count, Q
    
    # Estadísticas por período
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    analytics = {
        'daily_stats': Notification.objects.filter(
            created_at__date=today
        ).aggregate(
            total=Count('id'),
            sent=Count('id', filter=Q(status='sent')),
            failed=Count('id', filter=Q(status='failed'))
        ),
        'weekly_stats': Notification.objects.filter(
            created_at__date__gte=week_ago
        ).extra({
            'day': 'date(created_at)'
        }).values('day').annotate(
            total=Count('id'),
            sent=Count('id', filter=Q(status='sent')),
            failed=Count('id', filter=Q(status='failed'))
        ).order_by('day'),
        'channel_stats': Notification.objects.values('channel').annotate(
            count=Count('id')
        ).order_by('-count'),
        'type_stats': Notification.objects.values('notification_type').annotate(
            count=Count('id')
        ).order_by('-count')
    }
    
    context = {
        'analytics': analytics,
        'title': 'Análisis y Estadísticas'
    }
    
    return render(request, 'notifications/admin/analytics.html', context)


@login_required
@user_passes_test(is_superuser)
def reports(request):
    """Reportes del sistema"""
    
    context = {
        'title': 'Reportes del Sistema'
    }
    
    return render(request, 'notifications/admin/reports.html', context)


# API Endpoints para AJAX
@login_required
@user_passes_test(is_superuser)
def api_dashboard_stats(request):
    """API para estadísticas del dashboard"""
    from django.http import JsonResponse
    from datetime import datetime, timedelta
    
    today = datetime.now().date()
    
    stats = {
        'total_notifications': Notification.objects.count(),
        'sent_today': Notification.objects.filter(
            created_at__date=today, 
            status='sent'
        ).count(),
        'failed_today': Notification.objects.filter(
            created_at__date=today, 
            status='failed'
        ).count(),
        'pending': Notification.objects.filter(status='pending').count(),
        'total_users': User.objects.count(),
        'active_templates': NotificationTemplate.objects.filter(is_active=True).count()
    }
    
    return JsonResponse(stats)


@login_required
@user_passes_test(is_superuser)
def api_chart_data(request):
    """API para datos de gráficos"""
    from django.http import JsonResponse
    from datetime import datetime, timedelta
    from django.db.models import Count, Q
    
    # Últimos 7 días
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=6)
    
    chart_data = Notification.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date
    ).extra({
        'day': 'date(created_at)'
    }).values('day').annotate(
        sent=Count('id', filter=Q(status='sent')),
        failed=Count('id', filter=Q(status='failed'))
    ).order_by('day')
    
    labels = []
    sent_data = []
    failed_data = []
    
    for item in chart_data:
        labels.append(item['day'].strftime('%d/%m'))
        sent_data.append(item['sent'])
        failed_data.append(item['failed'])
    
    return JsonResponse({
        'labels': labels,
        'sent': sent_data,
        'failed': failed_data
    })


@login_required
@user_passes_test(is_superuser)
def api_recent_logs(request):
    """API para logs recientes"""
    from django.http import JsonResponse
    from django.template.loader import render_to_string
    
    recent_logs = Notification.objects.select_related('recipient').order_by('-created_at')[:10]
    
    html = render_to_string('notifications/admin/recent_logs_partial.html', {
        'recent_logs': recent_logs
    })
    
    return JsonResponse({'html': html})
