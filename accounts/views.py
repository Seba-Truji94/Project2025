from django.shortcuts import render
from django.views.generic import TemplateView

class CustomLoginView(TemplateView):
    template_name = 'accounts/login.html'

class RegisterView(TemplateView):
    template_name = 'accounts/register.html'

class ProfileView(TemplateView):
    template_name = 'accounts/profile.html'

class ProfileEditView(TemplateView):
    template_name = 'accounts/profile_edit.html'

class AddressListView(TemplateView):
    template_name = 'accounts/address_list.html'

class AddressCreateView(TemplateView):
    template_name = 'accounts/address_form.html'

class AddressEditView(TemplateView):
    template_name = 'accounts/address_form.html'

class AddressDeleteView(TemplateView):
    template_name = 'accounts/address_confirm_delete.html'

class WishlistView(TemplateView):
    template_name = 'accounts/wishlist.html'

def add_to_wishlist(request, product_id):
    return render(request, 'accounts/wishlist.html')

def remove_from_wishlist(request, product_id):
    return render(request, 'accounts/wishlist.html')
