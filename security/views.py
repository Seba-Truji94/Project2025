"""
Vistas de seguridad
"""
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from .utils import SecurityAudit, check_password_strength
import json


def csrf_failure(request, reason=""):
    """Vista personalizada para fallos de CSRF"""
    context = {
        'title': 'Error de Seguridad',
        'message': 'Su sesión ha expirado o el formulario no es válido. Por favor, recargue la página e intente nuevamente.',
        'reason': reason
    }
    return render(request, 'security/csrf_failure.html', context, status=403)


@user_passes_test(lambda u: u.is_superuser)
def security_dashboard(request):
    """Dashboard de seguridad para administradores"""
    audit_report = SecurityAudit.generate_security_report()
    
    context = {
        'title': 'Dashboard de Seguridad',
        'audit_report': audit_report,
    }
    return render(request, 'security/dashboard.html', context)


@csrf_exempt
def check_password_api(request):
    """API para verificar fortaleza de contraseña en tiempo real"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            password = data.get('password', '')
            
            strength_result = check_password_strength(password)
            
            return JsonResponse({
                'success': True,
                'strength': strength_result
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'})
