from django.shortcuts import render
from django.views.generic import TemplateView

class CartDetailView(TemplateView):
    template_name = 'cart/cart_detail.html'

def add_to_cart(request, product_id):
    return render(request, 'cart/cart_detail.html')

def remove_from_cart(request, product_id):
    return render(request, 'cart/cart_detail.html')

def update_cart(request, product_id):
    return render(request, 'cart/cart_detail.html')

def clear_cart(request):
    return render(request, 'cart/cart_detail.html')
