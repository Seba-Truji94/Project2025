from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def notification_list_temp(request):
    """Vista temporal para notificaciones mientras se configuran las tablas"""
    context = {
        'needs_migration': True,
        'total_count': 0,
        'unread_count': 0,
        'email_count': 0,
        'sms_count': 0,
        'whatsapp_count': 0,
        'notifications': []
    }
    return render(request, 'notifications/list.html', context)
