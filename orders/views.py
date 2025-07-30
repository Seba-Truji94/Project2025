from django.shortcuts import render
from django.views.generic import TemplateView

class OrderListView(TemplateView):
    template_name = 'orders/order_list.html'

class OrderDetailView(TemplateView):
    template_name = 'orders/order_detail.html'

class OrderCreateView(TemplateView):
    template_name = 'orders/order_create.html'

def cancel_order(request, order_number):
    return render(request, 'orders/order_detail.html')
