"""
URL Configuration for Railway deployment health checks
"""
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt

@never_cache
@csrf_exempt
def health_check(request):
    """
    Health check endpoint for Railway
    Returns status 200 if the application is running
    """
    return JsonResponse({
        'status': 'healthy',
        'service': 'Dulce Bias E-commerce',
        'message': 'Galletas Kati online! 🍪'
    })
