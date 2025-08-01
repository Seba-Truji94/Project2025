# orders/admin_urls.py
from django.urls import path
from . import admin_views
from . import transfer_admin_views

# Definir URLs con orden específico para evitar conflictos
urlpatterns = [
    # Ruta raíz del admin
    path('', admin_views.OrderManagementView.as_view(), name='admin_management'),
    
    # RUTAS ESPECÍFICAS PRIMERO
    path('statistics/', admin_views.order_statistics, name='admin_statistics'),
    path('bulk/update-status/', admin_views.bulk_update_orders, name='admin_bulk_update_status'),
    path('ajax/change-status/', admin_views.ajax_change_status, name='admin_ajax_change_status'),
    path('ajax/change-payment-status/', admin_views.ajax_change_payment_status, name='admin_ajax_change_payment_status'),
    path('ajax/stats/', admin_views.ajax_stats, name='admin_ajax_stats'),
    
    # Rutas de gestión de transferencias
    path('transfers/', transfer_admin_views.transfer_management_view, name='admin_transfer_management'),
    
    # RUTAS DINÁMICAS AL FINAL
    path('<str:order_number>/', admin_views.OrderDetailManagementView.as_view(), name='admin_detail'),
    path('<str:order_number>/update-status/', admin_views.update_order_status, name='admin_update_status'),
    path('<str:order_number>/update-notes/', admin_views.update_order_notes, name='admin_update_notes'),
    
    # Acciones de transferencia
    path('<str:order_number>/transfer/verify/', transfer_admin_views.verify_transfer_payment, name='admin_verify_transfer'),
    path('<str:order_number>/transfer/approve/', transfer_admin_views.approve_transfer_payment, name='admin_approve_transfer'),
    path('<str:order_number>/transfer/reject/', transfer_admin_views.reject_transfer_payment, name='admin_reject_transfer'),
    path('<str:order_number>/transfer/expire/', transfer_admin_views.expire_transfer_payment, name='admin_expire_transfer'),
]
