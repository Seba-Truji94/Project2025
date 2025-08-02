from django.urls import path
from . import views

app_name = 'security'

urlpatterns = [
    path('dashboard/', views.security_dashboard, name='dashboard'),
    path('api/check-password/', views.check_password_api, name='check_password_api'),
]
