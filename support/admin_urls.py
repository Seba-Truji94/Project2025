# support/admin_urls.py
from django.urls import path
from . import admin_views

# URLs de administración de soporte (solo superusuarios)
urlpatterns = [
    # Ruta raíz del admin de soporte
    path('', admin_views.SupportManagementView.as_view(), name='admin_management'),
    
    # RUTAS ESPECÍFICAS PRIMERO
    path('statistics/', admin_views.support_statistics, name='admin_statistics'),
    path('bulk/update-status/', admin_views.bulk_update_tickets, name='admin_bulk_update_status'),
    path('ajax/change-status/', admin_views.ajax_change_status, name='admin_ajax_change_status'),
    path('ajax/assign-ticket/', admin_views.ajax_assign_ticket, name='admin_ajax_assign_ticket'),
    path('ajax/stats/', admin_views.ajax_stats, name='admin_ajax_stats'),
    
    # Gestión de categorías
    path('categories/', admin_views.category_management_view, name='admin_category_management'),
    path('categories/create/', admin_views.create_category, name='admin_create_category'),
    path('categories/<int:category_id>/edit/', admin_views.edit_category, name='admin_edit_category'),
    path('categories/<int:category_id>/toggle/', admin_views.toggle_category, name='admin_toggle_category'),
    path('categories/<int:category_id>/delete/', admin_views.delete_category, name='admin_delete_category'),
    
    # RUTAS DINÁMICAS AL FINAL
    path('<str:ticket_number>/', admin_views.SupportTicketDetailManagementView.as_view(), name='admin_detail'),
    path('<str:ticket_number>/update-status/', admin_views.update_ticket_status, name='admin_update_status'),
    path('<str:ticket_number>/assign/', admin_views.assign_ticket, name='admin_assign_ticket'),
    path('<str:ticket_number>/resolve/', admin_views.resolve_ticket, name='admin_resolve_ticket'),
    path('<str:ticket_number>/add-message/', admin_views.add_admin_message, name='admin_add_message'),
]
