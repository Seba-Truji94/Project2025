from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.views.generic import TemplateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('shop:home')
    
    def get_success_url(self):
        return self.success_url

class RegisterView(CreateView):
    form_class = UserCreationForm
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

class ProfileEditView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile_edit.html'
    login_url = reverse_lazy('accounts:login')

class AddressListView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/address_list.html'
    login_url = reverse_lazy('accounts:login')

class AddressCreateView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/address_form.html'
    login_url = reverse_lazy('accounts:login')

class AddressEditView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/address_form.html'
    login_url = reverse_lazy('accounts:login')

class AddressDeleteView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/address_confirm_delete.html'
    login_url = reverse_lazy('accounts:login')

class WishlistView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/wishlist.html'
    login_url = reverse_lazy('accounts:login')

def add_to_wishlist(request, product_id):
    # Esta función manejará agregar productos a la wishlist
    return render(request, 'accounts/wishlist.html')

def remove_from_wishlist(request, product_id):
    # Esta función manejará quitar productos de la wishlist
    return render(request, 'accounts/wishlist.html')
