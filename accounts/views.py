from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.views.generic import TemplateView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from .models import UserProfile, Address, Wishlist, WishlistItem
from .forms import UserRegistrationForm, UserProfileForm, UserForm, AddressForm
from shop.models import Product

# Importar modelos de notificaciones
try:
    from notifications.models import UserNotificationPreference, Notification
    from notifications.forms import NotificationPreferenceForm
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    NOTIFICATIONS_AVAILABLE = False

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('shop:home')
    
    def get_success_url(self):
        return self.success_url

class RegisterView(CreateView):
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')
    
    def form_valid(self, form):
        # Guardar el usuario
        response = super().form_valid(form)
        # Iniciar sesión automáticamente después del registro
        login(self.request, self.object)
        messages.success(self.request, '¡Cuenta creada exitosamente! Bienvenido a Dulce Bias.')
        return redirect('shop:home')

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'
    login_url = reverse_lazy('accounts:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Asegurar que el usuario tenga un perfil
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        context['profile'] = profile
        context['recent_orders'] = []  # Agregar órdenes recientes cuando esté implementado
        
        # Agregar información de notificaciones si está disponible
        if NOTIFICATIONS_AVAILABLE:
            try:
                notification_prefs, created = UserNotificationPreference.objects.get_or_create(
                    user=self.request.user
                )
                context['notification_prefs'] = notification_prefs
                context['has_notifications'] = True
                
                # Estadísticas de notificaciones para el usuario
                context['notification_stats'] = {
                    'total_received': Notification.objects.filter(recipient=self.request.user).count(),
                    'unread_count': Notification.objects.filter(
                        recipient=self.request.user, 
                        status='pending'
                    ).count(),
                    'recent_notifications': Notification.objects.filter(
                        recipient=self.request.user
                    ).order_by('-created_at')[:5]
                }
                
                # Si es superusuario, agregar estadísticas administrativas
                if self.request.user.is_superuser:
                    from django.db.models import Count, Q
                    from datetime import datetime, timedelta
                    
                    today = datetime.now().date()
                    week_ago = today - timedelta(days=7)
                    
                    context['is_admin'] = True
                    context['admin_stats'] = {
                        'total_notifications': Notification.objects.count(),
                        'sent_today': Notification.objects.filter(
                            created_at__date=today,
                            status='sent'
                        ).count(),
                        'failed_today': Notification.objects.filter(
                            created_at__date=today,
                            status='failed'
                        ).count(),
                        'pending_notifications': Notification.objects.filter(
                            status='pending'
                        ).count(),
                        'total_users': User.objects.count(),
                        'users_with_notifications': UserNotificationPreference.objects.count(),
                        'weekly_stats': Notification.objects.filter(
                            created_at__date__gte=week_ago
                        ).extra({
                            'day': 'date(created_at)'
                        }).values('day').annotate(
                            sent=Count('id', filter=Q(status='sent')),
                            failed=Count('id', filter=Q(status='failed'))
                        ).order_by('day')
                    }
                    
            except Exception as e:
                context['has_notifications'] = False
                context['notification_error'] = str(e)
        else:
            context['has_notifications'] = False
            
        return context

class ProfileEditView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile_edit.html'
    login_url = reverse_lazy('accounts:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Asegurar que el usuario tenga un perfil
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        
        context['user_form'] = UserForm(instance=self.request.user)
        context['profile_form'] = UserProfileForm(instance=profile)
        return context
    
    def post(self, request, *args, **kwargs):
        # Asegurar que el usuario tenga un perfil
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, '¡Tu perfil ha sido actualizado exitosamente! 🎉')
            return redirect('accounts:profile')
        else:
            # Recopilar todos los errores para mostrar un mensaje más específico
            error_messages = []
            
            if user_form.errors:
                for field, errors in user_form.errors.items():
                    for error in errors:
                        error_messages.append(f"{field.title()}: {error}")
            
            if profile_form.errors:
                for field, errors in profile_form.errors.items():
                    for error in errors:
                        error_messages.append(f"{field.title()}: {error}")
            
            if error_messages:
                messages.error(request, f'Por favor corrige los siguientes errores: {"; ".join(error_messages)}')
            else:
                messages.error(request, 'Por favor corrige los errores en el formulario.')
            
            context = self.get_context_data(**kwargs)
            context['user_form'] = user_form
            context['profile_form'] = profile_form
            return self.render_to_response(context)

class AddressListView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/address_list.html'
    login_url = reverse_lazy('accounts:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['addresses'] = Address.objects.filter(user=self.request.user)
        return context

class AddressCreateView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/address_form.html'
    login_url = reverse_lazy('accounts:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = AddressForm(user=self.request.user)
        context['form_title'] = 'Agregar Nueva Dirección'
        return context
    
    def post(self, request, *args, **kwargs):
        form = AddressForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Dirección agregada exitosamente!')
            return redirect('accounts:address_list')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
            context = self.get_context_data(**kwargs)
            context['form'] = form
            return self.render_to_response(context)

class AddressEditView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/address_form.html'
    login_url = reverse_lazy('accounts:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        address = get_object_or_404(Address, id=kwargs['pk'], user=self.request.user)
        context['form'] = AddressForm(instance=address, user=self.request.user)
        context['form_title'] = 'Editar Dirección'
        context['address'] = address
        return context
    
    def post(self, request, *args, **kwargs):
        address = get_object_or_404(Address, id=kwargs['pk'], user=request.user)
        form = AddressForm(request.POST, instance=address, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Dirección actualizada exitosamente!')
            return redirect('accounts:address_list')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
            context = self.get_context_data(**kwargs)
            context['form'] = form
            return self.render_to_response(context)

class AddressDeleteView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/address_confirm_delete.html'
    login_url = reverse_lazy('accounts:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['address'] = get_object_or_404(Address, id=kwargs['pk'], user=self.request.user)
        return context
    
    def post(self, request, *args, **kwargs):
        address = get_object_or_404(Address, id=kwargs['pk'], user=request.user)
        address.delete()
        messages.success(request, '¡Dirección eliminada exitosamente!')
        return redirect('accounts:address_list')

class WishlistView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/wishlist.html'
    login_url = reverse_lazy('accounts:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        wishlist, created = Wishlist.objects.get_or_create(user=self.request.user)
        context['wishlist_items'] = WishlistItem.objects.filter(wishlist=wishlist).select_related('product')
        return context

def add_to_wishlist(request, product_id):
    """Agregar producto a la lista de deseos"""
    if not request.user.is_authenticated:
        messages.warning(request, 'Debes iniciar sesión para agregar productos a tu lista de deseos.')
        return redirect('accounts:login')
    
    product = get_object_or_404(Product, id=product_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    
    wishlist_item, created = WishlistItem.objects.get_or_create(
        wishlist=wishlist,
        product=product
    )
    
    if created:
        messages.success(request, f'¡{product.name} agregado a tu lista de deseos!')
    else:
        messages.info(request, f'{product.name} ya está en tu lista de deseos.')
    
    # Redirigir de vuelta a la página anterior o a la wishlist
    return redirect(request.META.get('HTTP_REFERER', 'accounts:wishlist'))

def remove_from_wishlist(request, product_id):
    """Quitar producto de la lista de deseos"""
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    product = get_object_or_404(Product, id=product_id)
    wishlist = get_object_or_404(Wishlist, user=request.user)
    
    try:
        wishlist_item = WishlistItem.objects.get(wishlist=wishlist, product=product)
        wishlist_item.delete()
        messages.success(request, f'¡{product.name} eliminado de tu lista de deseos!')
    except WishlistItem.DoesNotExist:
        messages.error(request, 'Este producto no está en tu lista de deseos.')
    
    # Redirigir de vuelta a la página anterior o a la wishlist
    return redirect(request.META.get('HTTP_REFERER', 'accounts:wishlist'))


class NotificationPreferencesView(LoginRequiredMixin, TemplateView):
    """Vista para gestionar preferencias de notificaciones del usuario"""
    template_name = 'accounts/notification_preferences.html'
    login_url = reverse_lazy('accounts:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if NOTIFICATIONS_AVAILABLE:
            try:
                notification_prefs, created = UserNotificationPreference.objects.get_or_create(
                    user=self.request.user
                )
                context['form'] = NotificationPreferenceForm(instance=notification_prefs)
                context['has_notifications'] = True
                
                # Estadísticas personales de notificaciones
                context['user_stats'] = {
                    'total_received': Notification.objects.filter(recipient=self.request.user).count(),
                    'total_sent': Notification.objects.filter(
                        recipient=self.request.user, 
                        status__in=['sent', 'delivered']
                    ).count(),
                    'recent_notifications': Notification.objects.filter(
                        recipient=self.request.user
                    ).order_by('-created_at')[:10]
                }
                
            except Exception as e:
                context['has_notifications'] = False
                context['error_message'] = f"Error al cargar preferencias: {str(e)}"
        else:
            context['has_notifications'] = False
            context['error_message'] = "Sistema de notificaciones no disponible"
            
        return context
    
    def post(self, request, *args, **kwargs):
        if not NOTIFICATIONS_AVAILABLE:
            messages.error(request, 'Sistema de notificaciones no disponible.')
            return redirect('accounts:profile')
            
        try:
            notification_prefs, created = UserNotificationPreference.objects.get_or_create(
                user=request.user
            )
            form = NotificationPreferenceForm(request.POST, instance=notification_prefs)
            
            if form.is_valid():
                form.save()
                messages.success(request, '¡Preferencias de notificación actualizadas exitosamente! 📬')
                return redirect('accounts:profile')
            else:
                messages.error(request, 'Por favor corrige los errores en el formulario.')
                context = self.get_context_data(**kwargs)
                context['form'] = form
                return self.render_to_response(context)
                
        except Exception as e:
            messages.error(request, f'Error al actualizar preferencias: {str(e)}')
            return redirect('accounts:profile')


def admin_notification_dashboard(request):
    """Vista rápida para acceder al dashboard de notificaciones desde el perfil"""
    if not request.user.is_superuser:
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('accounts:profile')
    
    # Redirigir al dashboard de notificaciones
    return redirect('notifications_admin:dashboard')
