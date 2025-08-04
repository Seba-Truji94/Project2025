"""
URLs administrativas para el sistema de notificaciones
Solo accesibles para superusuarios
"""

from django.urls import path
from . import admin_views

app_name = 'notifications_admin'

urlpatterns = [
    # Dashboard principal
    path('admin/', admin_views.admin_dashboard, name='dashboard'),
    
    # Gestión de notificaciones
    path('admin/bulk-send/', admin_views.bulk_send, name='bulk_send'),
    path('admin/logs/', admin_views.notification_logs, name='logs'),
    path('admin/retry-failed/', admin_views.retry_failed_notifications, name='retry_failed'),
    path('admin/clear-logs/', admin_views.clear_old_logs, name='clear_logs'),
    
    # Gestión de plantillas
    path('admin/templates/', admin_views.template_management, name='templates'),
    path('admin/templates/create/', admin_views.template_create, name='template_create'),
    path('admin/templates/<int:template_id>/edit/', admin_views.template_edit, name='template_edit'),
    path('admin/templates/<int:template_id>/delete/', admin_views.template_delete, name='template_delete'),
    path('admin/templates/<int:template_id>/preview/', admin_views.template_preview, name='template_preview'),
    
    # Gestión de usuarios
    path('admin/user-preferences/', admin_views.user_preferences, name='user_preferences'),
    path('admin/user-preferences/<int:user_id>/', admin_views.user_preference_detail, name='user_preference_detail'),
    path('admin/users/export/', admin_views.export_user_preferences, name='export_users'),
    
    # Campañas
    path('admin/campaigns/', admin_views.campaign_management, name='campaigns'),
    path('admin/campaigns/create/', admin_views.campaign_create, name='campaign_create'),
    path('admin/campaigns/<int:campaign_id>/', admin_views.campaign_detail, name='campaign_detail'),
    
    # Sistema y configuración
    path('admin/system-status/', admin_views.system_status, name='system_status'),
    path('admin/config/', admin_views.system_config, name='config'),
    path('admin/test/', admin_views.test_notification, name='test'),
    
    # Exportación y reportes
    path('admin/export/', admin_views.export_notifications, name='export'),
    path('admin/analytics/', admin_views.analytics_dashboard, name='analytics'),
    path('admin/reports/', admin_views.reports, name='reports'),
    
    # API endpoints para dashboard
    path('admin/api/stats/', admin_views.api_dashboard_stats, name='api_stats'),
    path('admin/api/chart-data/', admin_views.api_chart_data, name='api_chart_data'),
    path('admin/api/recent-logs/', admin_views.api_recent_logs, name='api_recent_logs'),
]
