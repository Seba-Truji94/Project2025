"""
URL configuration for dulce_bias_project project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from .health import health_check

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('shop.urls')),
    path('accounts/', include('accounts.urls')),
    path('cart/', include('cart.urls')),
    path('orders/', include('orders.urls')),
    path('support/', include('support.urls')),
    path('security/', include('security.urls')),
    path('management/', include('management.urls')),  # Módulo de gestión empresarial
    path('notifications/', include('notifications.urls')),  # Sistema de notificaciones
    path('notifications/', include('notifications.admin_urls')),  # Admin de notificaciones
    
    # Health check para Railway
    path('health/', health_check, name='health_check'),
    
    # Favicon
    path('favicon.ico', RedirectView.as_view(url=settings.STATIC_URL + 'favicon.ico', permanent=True)),
]

# Configuración para servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Personalización del admin
admin.site.site_header = "Dulces Bias Admin"
admin.site.site_title = "Dulces Bias"
admin.site.index_title = "Panel de Administración"
