from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Order, OrderItem


class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'
    paginate_by = 10
    
    def get_queryset(self):
        """Mostrar solo los pedidos del usuario autenticado"""
        return Order.objects.filter(user=self.request.user).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Estadísticas del usuario
        user_orders = self.get_queryset()
        context.update({
            'total_orders': user_orders.count(),
            'pending_orders': user_orders.filter(status='pending').count(),
            'processing_orders': user_orders.filter(status__in=['confirmed', 'processing']).count(),
            'completed_orders': user_orders.filter(status__in=['shipped', 'delivered']).count(),
        })
        return context


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'
    slug_field = 'order_number'
    slug_url_kwarg = 'order_number'
    
    def get_queryset(self):
        """Solo permitir ver pedidos del usuario autenticado"""
        return Order.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_items'] = self.object.items.all()
        return context


@login_required
def cancel_order(request, order_number):
    """Cancelar un pedido (solo si está en estado pendiente)"""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    
    if order.status == 'pending':
        order.status = 'cancelled'
        order.save()
        messages.success(request, f'✅ Pedido #{order.order_number} cancelado exitosamente')
    else:
        messages.error(request, f'❌ No se puede cancelar el pedido #{order.order_number} en estado {order.get_status_display()}')
    
    return redirect('orders:order_detail', order_number=order.order_number)
