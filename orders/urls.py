from django.urls import path, include
from . import views
from . import transfer_views

app_name = 'orders'

urlpatterns = [
    # URLs de administración (solo superusuarios) - DEBE IR PRIMERO
    path('admin/', include('orders.admin_urls')),
    
    # URLs de transferencia - específicas antes que dinámicas
    path('transfer/instructions/', transfer_views.transfer_instructions_view, name='transfer_instructions'),
    
    # URLs de usuario
    path('', views.OrderListView.as_view(), name='order_list'),
    path('<str:order_number>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('<str:order_number>/cancel/', views.cancel_order, name='cancel_order'),
    
    # URLs de transferencia dinámicas
    path('<str:order_number>/transfer/', transfer_views.transfer_payment_view, name='transfer_payment'),
]
