"""
URLs para el sistema de notificaciones
"""
from django.urls import path
from . import views, temp_views

app_name = 'notifications'

urlpatterns = [
    # URLs para usuarios (temporal)
    path('', temp_views.notification_list_temp, name='list'),
    path('preferences/', views.notification_preferences, name='preferences'),
    path('detail/<uuid:pk>/', views.NotificationDetailView.as_view(), name='detail'),
    path('mark-read/<uuid:notification_id>/', views.mark_notification_read, name='mark_read'),
    path('mark-all-read/', views.mark_all_read, name='mark_all_read'),
    path('test/', views.test_notification, name='test'),
    
    # Webhook para confirmaciones de entrega
    path('webhook/delivery/', views.delivery_webhook, name='delivery_webhook'),
    
    # URLs para administradores (cambiadas para evitar conflicto)
    path('admin-list/', views.AdminNotificationListView.as_view(), name='admin_list'),
    path('admin-bulk/', views.admin_send_bulk_notification, name='admin_bulk'),
    path('admin-stats/', views.admin_notification_stats, name='admin_stats'),
]
