"""
Decorador para verificar que el usuario sea superusuario
"""
from functools import wraps
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages


def superuser_required(function=None, redirect_url='/'):
    """
    Decorador que requiere que el usuario sea superusuario
    """
    def check_superuser(user):
        return user.is_authenticated and user.is_superuser
    
    actual_decorator = user_passes_test(
        check_superuser,
        login_url=redirect_url
    )
    
    if function:
        return actual_decorator(function)
    return actual_decorator


class SuperuserRequiredMixin(UserPassesTestMixin):
    """
    Mixin que requiere que el usuario sea superusuario
    """
    
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_superuser
    
    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect('accounts:login')
        
        messages.error(
            self.request, 
            '🔒 Solo los superusuarios pueden acceder al módulo de gestión empresarial.'
        )
        return redirect('accounts:profile')
