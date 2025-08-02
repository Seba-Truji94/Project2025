from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Order, OrderItem, TransferPayment


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
        
        # Buscar transferencias verificadas con comentarios para mostrar notificaciones
        verified_transfers_with_notes = TransferPayment.objects.filter(
            order__user=self.request.user,
            status='verified',
            verification_notes__isnull=False
        ).exclude(verification_notes='').select_related('order')
        
        context['verified_transfers_with_notes'] = verified_transfers_with_notes
        
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
        
        # Incluir información de transferencia si existe
        try:
            transfer_payment = self.object.transfer_payment
            context['transfer_payment'] = transfer_payment
        except:
            context['transfer_payment'] = None
            
        return context


@login_required
def cancel_order(request, order_number):
    """Cancelar un pedido (solo si está en estado pendiente o si es superusuario)"""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    
    # Verificar si el pedido puede ser cancelado
    can_cancel = False
    error_message = None
    
    if order.status == 'cancelled':
        error_message = f'❌ El pedido #{order.order_number} ya está cancelado'
    elif order.status == 'delivered':
        error_message = f'❌ No se puede cancelar un pedido ya entregado'
    elif order.payment_status == 'paid' and not request.user.is_superuser:
        error_message = f'❌ No se puede cancelar el pedido #{order.order_number} porque ya está pagado. Contacta al administrador si necesitas cancelarlo.'
    elif order.status == 'pending' or request.user.is_superuser:
        can_cancel = True
    else:
        error_message = f'❌ No se puede cancelar el pedido #{order.order_number} en estado {order.get_status_display()}'
    
    if can_cancel:
        order.status = 'cancelled'
        order.save()
        
        if request.user.is_superuser and order.payment_status == 'paid':
            messages.warning(request, f'⚠️ Pedido pagado #{order.order_number} cancelado por administrador')
        else:
            messages.success(request, f'✅ Pedido #{order.order_number} cancelado exitosamente')
    else:
        messages.error(request, error_message)
    
    return redirect('orders:order_detail', order_number=order.order_number)


# Vistas administrativas

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from .models import OrderStatusHistory, OrderPaymentStatusHistory


def is_superuser(user):
    """Verificar si el usuario es superusuario"""
    return user.is_authenticated and user.is_superuser


@user_passes_test(is_superuser)
def admin_orders_dashboard(request):
    """Panel de administración de órdenes con historial"""
    # Estadísticas generales
    total_orders = Order.objects.count()
    recent_cutoff = timezone.now() - timedelta(days=7)
    recent_orders = Order.objects.filter(created_at__gte=recent_cutoff).count()
    
    # Órdenes por estado
    status_stats = {}
    for status_code, status_name in Order.STATUS_CHOICES:
        count = Order.objects.filter(status=status_code).count()
        status_stats[status_name] = count
    
    # Órdenes por estado de pago
    payment_status_stats = {}
    for payment_code, payment_name in Order.PAYMENT_STATUS_CHOICES:
        count = Order.objects.filter(payment_status=payment_code).count()
        payment_status_stats[payment_name] = count
    
    # Órdenes recientes con historial
    recent_orders_with_history = Order.objects.filter(
        created_at__gte=recent_cutoff
    ).prefetch_related('status_history', 'payment_status_history').order_by('-created_at')[:10]
    
    # Cambios recientes de estado
    recent_status_changes = OrderStatusHistory.objects.filter(
        changed_at__gte=recent_cutoff
    ).select_related('order', 'changed_by').order_by('-changed_at')[:10]
    
    # Cambios recientes de estado de pago
    recent_payment_changes = OrderPaymentStatusHistory.objects.filter(
        changed_at__gte=recent_cutoff
    ).select_related('order', 'changed_by').order_by('-changed_at')[:10]
    
    context = {
        'total_orders': total_orders,
        'recent_orders': recent_orders,
        'status_stats': status_stats,
        'payment_status_stats': payment_status_stats,
        'recent_orders_with_history': recent_orders_with_history,
        'recent_status_changes': recent_status_changes,
        'recent_payment_changes': recent_payment_changes,
    }
    
    return render(request, 'orders/admin/dashboard.html', context)


@user_passes_test(is_superuser)
def admin_order_detail(request, order_number):
    """Vista detallada de orden para administradores con historial completo"""
    order = get_object_or_404(Order, order_number=order_number)
    
    # Historial completo de estados
    status_history = order.status_history.select_related('changed_by').order_by('-changed_at')
    payment_history = order.payment_status_history.select_related('changed_by').order_by('-changed_at')
    
    # Items de la orden
    order_items = order.items.select_related('product').all()
    
    context = {
        'order': order,
        'order_items': order_items,
        'status_history': status_history,
        'payment_history': payment_history,
        'status_choices': Order.STATUS_CHOICES,
        'payment_status_choices': Order.PAYMENT_STATUS_CHOICES,
    }
    
    return render(request, 'orders/admin/order_detail.html', context)


@user_passes_test(is_superuser)
def admin_update_order_status(request, order_number):
    """Actualizar estado de orden desde el panel administrativo"""
    if request.method == 'POST':
        order = get_object_or_404(Order, order_number=order_number)
        new_status = request.POST.get('status')
        new_payment_status = request.POST.get('payment_status')
        notes = request.POST.get('notes', '')
        
        # Configurar usuario y notas para el historial
        order._changed_by = request.user
        order._change_notes = notes or f'Actualizado desde panel administrativo por {request.user.get_full_name() or request.user.username}'
        
        changes = []
        
        # Actualizar estado de orden
        if new_status and new_status != order.status:
            old_status_display = order.get_status_display()
            order.status = new_status
            new_status_display = dict(Order.STATUS_CHOICES)[new_status]
            changes.append(f'Estado: {old_status_display} → {new_status_display}')
        
        # Actualizar estado de pago
        if new_payment_status and new_payment_status != order.payment_status:
            old_payment_display = order.get_payment_status_display()
            order.payment_status = new_payment_status
            new_payment_display = dict(Order.PAYMENT_STATUS_CHOICES)[new_payment_status]
            changes.append(f'Estado de pago: {old_payment_display} → {new_payment_display}')
        
        if changes:
            order.save()
            messages.success(request, f'Orden #{order.order_number} actualizada: {", ".join(changes)}')
        else:
            messages.info(request, 'No se realizaron cambios')
    
    return redirect('orders:admin_order_detail', order_number=order_number)


@user_passes_test(is_superuser)
def admin_order_history_ajax(request, order_number):
    """Obtener historial de orden vía AJAX"""
    order = get_object_or_404(Order, order_number=order_number)
    
    # Historial de estados
    status_history = []
    for entry in order.status_history.select_related('changed_by').order_by('-changed_at'):
        status_history.append({
            'type': 'status',
            'change': entry.status_change_display,
            'changed_by': entry.changed_by.get_full_name() if entry.changed_by else 'Sistema',
            'changed_at': entry.changed_at.strftime('%d/%m/%Y %H:%M'),
            'notes': entry.notes
        })
    
    # Historial de pagos
    payment_history = []
    for entry in order.payment_status_history.select_related('changed_by').order_by('-changed_at'):
        payment_history.append({
            'type': 'payment',
            'change': entry.payment_status_change_display,
            'changed_by': entry.changed_by.get_full_name() if entry.changed_by else 'Sistema',
            'changed_at': entry.changed_at.strftime('%d/%m/%Y %H:%M'),
            'notes': entry.notes
        })
    
    # Combinar y ordenar por fecha
    combined_history = sorted(
        status_history + payment_history,
        key=lambda x: x['changed_at'],
        reverse=True
    )
    
    return JsonResponse({
        'success': True,
        'history': combined_history,
        'order_number': order.order_number
    })
