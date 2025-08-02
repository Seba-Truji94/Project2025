from django.urls import path, include
from . import views

app_name = 'support'

urlpatterns = [
    # URLs de administración (solo superusuarios) - DEBE IR PRIMERO
    path('admin/', include('support.admin_urls')),
    
    # Página principal
    path('', views.support_home, name='home'),
    
    # Tickets
    path('tickets/', views.TicketListView.as_view(), name='ticket_list'),
    path('tickets/create/', views.create_ticket, name='create_ticket'),
    path('tickets/<uuid:ticket_id>/', views.ticket_detail, name='ticket_detail'),
    path('tickets/<uuid:ticket_id>/message/', views.send_message, name='send_message'),
    path('tickets/<uuid:ticket_id>/rate/', views.rate_ticket, name='rate_ticket'),
    
    # Notificaciones
    path('notifications/', views.notifications, name='notifications'),
    path('api/notifications/unread-count/', views.get_unread_notifications_count, name='unread_notifications_count'),
    
    # FAQs
    path('faq/', views.faq_list, name='faq_list'),
    path('faq/<int:faq_id>/', views.faq_detail, name='faq_detail'),
    path('faq/<int:faq_id>/vote/', views.faq_vote, name='faq_vote'),
    
    # Chat rápido
    path('quick-chat/', views.quick_support, name='quick_support'),
]
