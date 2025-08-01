from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import ListView, DetailView, UpdateView
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import timedelta
from .models import Order
from .admin_forms import OrderStatusForm, OrderNotesForm, BulkOrderUpdateForm, OrderFilterForm


def is_superuser(user):
    """Verificar si el usuario es superusuario"""
    return user.is_authenticated and user.is_superuser


class SuperuserRequiredMixin(UserPassesTestMixin):
    """Mixin para requerir permisos de superusuario"""
    def test_func(self):
        return self.request.user.is_superuser
    
    def handle_no_permission(self):
        messages.error(self.request, 'No tienes permisos para acceder a esta sección.')
        return redirect('shop:home')


class OrderManagementView(SuperuserRequiredMixin, ListView):
    """Vista principal de gestión de pedidos para superusuarios"""
    model = Order
    template_name = 'orders/admin/order_management.html'
    context_object_name = 'orders'
    paginate_by = 20  # Valor por defecto
    
    def get_paginate_by(self, queryset):
        """Obtener la cantidad de elementos por página desde el parámetro GET"""
        page_size = self.request.GET.get('page_size', '20')
        try:
            page_size = int(page_size)
            # Validar que sea uno de los valores permitidos
            if page_size in [10, 20, 50, 100]:
                return page_size
            else:
                return 20  # Valor por defecto si no es válido
        except (ValueError, TypeError):
            return 20  # Valor por defecto si no es un número válido
    
    def get_queryset(self):
        queryset = Order.objects.select_related('user').prefetch_related('items__product')
        
        # Filtros
        status_filter = self.request.GET.get('status')
        payment_status_filter = self.request.GET.get('payment_status')
        search_query = self.request.GET.get('search')
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        
        if status_filter and status_filter != 'all':
            queryset = queryset.filter(status=status_filter)
        
        if payment_status_filter and payment_status_filter != 'all':
            queryset = queryset.filter(payment_status=payment_status_filter)
        
        if search_query:
            queryset = queryset.filter(
                Q(order_number__icontains=search_query) |
                Q(user__username__icontains=search_query) |
                Q(user__email__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query)
            )
        
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estadísticas generales
        context['stats'] = {
            'total_orders': Order.objects.count(),
            'pending_orders': Order.objects.filter(status='pending').count(),
            'processing_orders': Order.objects.filter(status='processing').count(),
            'delivered_orders': Order.objects.filter(status='delivered').count(),
            'paid_orders': Order.objects.filter(payment_status='paid').count(),
            'unpaid_orders': Order.objects.filter(payment_status='pending').count(),
        }
        
        # Filtros actuales
        context['current_filters'] = {
            'status': self.request.GET.get('status', 'all'),
            'payment_status': self.request.GET.get('payment_status', 'all'),
            'search': self.request.GET.get('search', ''),
            'date_from': self.request.GET.get('date_from', ''),
            'date_to': self.request.GET.get('date_to', ''),
            'page_size': self.request.GET.get('page_size', '20'),
        }
        
        # Opciones de estado
        context['status_choices'] = Order.STATUS_CHOICES
        context['payment_status_choices'] = Order.PAYMENT_STATUS_CHOICES
        
        # Opciones de paginación
        context['page_size_options'] = [
            {'value': '10', 'label': '10 por página'},
            {'value': '20', 'label': '20 por página'},
            {'value': '50', 'label': '50 por página'},
            {'value': '100', 'label': '100 por página'},
        ]
        
        return context


class OrderDetailManagementView(SuperuserRequiredMixin, DetailView):
    """Vista detallada de pedido para administradores"""
    model = Order
    template_name = 'orders/admin/order_detail.html'
    context_object_name = 'order'
    slug_field = 'order_number'
    slug_url_kwarg = 'order_number'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_form'] = OrderStatusForm(instance=self.object)
        context['notes_form'] = OrderNotesForm(instance=self.object)
        # context['status_history'] = self.object.status_history.all()
        
        # Incluir información de transferencia si existe
        try:
            transfer_payment = self.object.transfer_payment
            context['transfer_payment'] = transfer_payment
        except:
            context['transfer_payment'] = None
            
        return context


@user_passes_test(is_superuser)
def update_order_status(request, order_number):
    """Vista para actualizar el estado de un pedido"""
    order = get_object_or_404(Order, order_number=order_number)
    
    if request.method == 'POST':
        form = OrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            old_status = order.status
            new_status = form.cleaned_data['status']
            notes = form.cleaned_data.get('status_notes', '')
            
            # Actualizar el pedido
            order = form.save()
            
            # Registrar el cambio en el historial
            # OrderStatusHistory.objects.create(
            #     order=order,
            #     status=new_status,
            #     notes=notes,
            #     changed_by=request.user
            # )
            
            # Actualizar fechas especiales
            if new_status == 'shipped' and not order.shipped_at:
                order.shipped_at = timezone.now()
                order.save()
            elif new_status == 'delivered' and not order.delivered_at:
                order.delivered_at = timezone.now()
                order.save()
            
            messages.success(
                request, 
                f'✅ Estado del pedido #{order.order_number} actualizado de "{old_status}" a "{new_status}"'
            )
            
            # Respuesta AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Estado actualizado a {order.get_status_display()}',
                    'new_status': new_status,
                    'new_status_display': order.get_status_display()
                })
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                })
            messages.error(request, 'Error al actualizar el estado del pedido.')
    
    return redirect('orders:admin_detail', order_number=order.order_number)


@user_passes_test(is_superuser)
def update_order_notes(request, order_number):
    """Vista para actualizar las notas de un pedido"""
    order = get_object_or_404(Order, order_number=order_number)
    
    if request.method == 'POST':
        form = OrderNotesForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, f'✅ Notas del pedido #{order.order_number} actualizadas.')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Notas actualizadas correctamente'
                })
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                })
    
    return redirect('orders:admin_detail', order_number=order.order_number)


@user_passes_test(is_superuser)
def bulk_update_orders(request):
    """Vista para actualización masiva de pedidos"""
    if request.method == 'POST':
        order_ids = request.POST.getlist('order_ids')
        new_status = request.POST.get('new_status')
        
        if not order_ids or not new_status:
            messages.error(request, 'Selecciona al menos un pedido y un estado.')
            return redirect('orders:admin_management')
        
        # Actualizar pedidos seleccionados
        orders = Order.objects.filter(id__in=order_ids)
        updated_count = 0
        
        for order in orders:
            old_status = order.status
            order.status = new_status
            order.save()
            
            # Registrar en historial
            # OrderStatusHistory.objects.create(
            #     order=order,
            #     status=new_status,
            #     notes=f'Actualización masiva desde {old_status}',
            #     changed_by=request.user
            # )
            
            updated_count += 1
        
        messages.success(
            request, 
            f'✅ {updated_count} pedidos actualizados a "{dict(Order.STATUS_CHOICES)[new_status]}"'
        )
    
    return redirect('orders:admin_management')


@user_passes_test(is_superuser)
def order_statistics(request):
    """Vista de estadísticas de pedidos"""
    from django.db.models import Sum, Avg
    from datetime import datetime, timedelta
    
    # Estadísticas generales
    total_orders = Order.objects.count()
    total_revenue = Order.objects.filter(payment_status='paid').aggregate(Sum('total'))['total__sum'] or 0
    avg_order_value = Order.objects.aggregate(Avg('total'))['total__avg'] or 0
    
    # Estadísticas por estado
    status_stats = {}
    for status, display in Order.STATUS_CHOICES:
        count = Order.objects.filter(status=status).count()
        status_stats[status] = {
            'count': count,
            'display': display,
            'percentage': (count / total_orders * 100) if total_orders > 0 else 0
        }
    
    # Pedidos recientes (últimos 30 días)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_orders = Order.objects.filter(created_at__gte=thirty_days_ago).count()
    
    context = {
        'total_orders': total_orders,
        'total_revenue': f"${int(total_revenue):,}".replace(',', '.'),
        'avg_order_value': f"${int(avg_order_value):,}".replace(',', '.'),
        'status_stats': status_stats,
        'recent_orders': recent_orders,
    }
    
    return render(request, 'orders/admin/order_statistics.html', context)


# Vistas AJAX adicionales
@require_POST
@csrf_exempt
@require_POST
@user_passes_test(is_superuser)
def ajax_change_status(request):
    """Cambio de estado vía AJAX"""
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Sin permisos'})
    
    try:
        data = json.loads(request.body)
        order_id = data.get('order_id')
        order_number = data.get('order_number')
        new_status = data.get('status')
        notes = data.get('notes', '')
        
        # Buscar por ID o por número de orden
        if order_id:
            order = get_object_or_404(Order, id=order_id)
        elif order_number:
            order = get_object_or_404(Order, order_number=order_number)
        else:
            return JsonResponse({'success': False, 'error': 'ID de orden requerido'})
        
        old_status = order.status
        
        order.status = new_status
        if notes:
            order.notes = notes
        
        # Actualizar timestamps
        if new_status == 'shipped' and old_status != 'shipped':
            order.shipped_at = timezone.now()
        elif new_status == 'delivered' and old_status != 'delivered':
            order.delivered_at = timezone.now()
        
        order.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Estado del pedido #{order.order_number} actualizado a {order.get_status_display()}',
            'new_status': new_status,
            'status_display': order.get_status_display(),
            'order_number': order.order_number
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def ajax_stats(request):
    """Estadísticas vía AJAX"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Sin permisos'})
    
    stats = {
        'total': Order.objects.count(),
        'pending': Order.objects.filter(status='pending').count(),
        'confirmed': Order.objects.filter(status='confirmed').count(),
        'processing': Order.objects.filter(status='processing').count(),
        'shipped': Order.objects.filter(status='shipped').count(),
        'delivered': Order.objects.filter(status='delivered').count(),
        'cancelled': Order.objects.filter(status='cancelled').count(),
    }
    
    return JsonResponse(stats)


@require_POST
@user_passes_test(is_superuser)
def ajax_change_payment_status(request):
    """Cambio de estado de pago vía AJAX"""
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Sin permisos'})
    
    try:
        data = json.loads(request.body)
        order_id = data.get('order_id')
        new_payment_status = data.get('payment_status')
        action = data.get('action')
        
        if not order_id or not new_payment_status:
            return JsonResponse({'success': False, 'error': 'Datos incompletos'})
        
        order = get_object_or_404(Order, id=order_id)
        old_payment_status = order.payment_status
        
        # Validar transición de estado
        valid_transitions = {
            'pending': ['paid', 'failed'],
            'paid': ['pending', 'refunded'],
            'failed': ['pending', 'paid'],
            'refunded': ['pending']
        }
        
        if new_payment_status not in valid_transitions.get(old_payment_status, []):
            return JsonResponse({
                'success': False, 
                'error': f'Transición inválida de {old_payment_status} a {new_payment_status}'
            })
        
        # Actualizar estado de pago
        order.payment_status = new_payment_status
        
        # Lógica adicional según el nuevo estado
        if new_payment_status == 'paid' and old_payment_status == 'pending':
            # Si se marca como pagado, confirmar el pedido si está pendiente
            if order.status == 'pending':
                order.status = 'confirmed'
                status_message = " y confirmado"
            else:
                status_message = ""
        elif new_payment_status == 'pending' and old_payment_status == 'paid':
            # Si se desmarca como pagado, podría requerir revisión
            status_message = " - requiere revisión"
        else:
            status_message = ""
        
        order.save()
        
        # Crear mensaje de éxito
        action_text = "marcado como pagado" if action == "mark_paid" else "marcado como no pagado"
        message = f'Pedido #{order.order_number} {action_text} exitosamente{status_message}'
        
        return JsonResponse({
            'success': True,
            'message': message,
            'order_id': order.id,
            'order_number': order.order_number,
            'old_payment_status': old_payment_status,
            'new_payment_status': new_payment_status,
            'current_status': order.status,
            'status_display': order.get_status_display(),
            'payment_status_display': order.get_payment_status_display()
        })
        
    except Order.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Pedido no encontrado'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Error interno: {str(e)}'})
