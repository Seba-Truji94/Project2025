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
