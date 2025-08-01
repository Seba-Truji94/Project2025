from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from orders.models import Order, TransferPayment
from django.contrib.auth.models import User


@staff_member_required
@require_POST
def verify_transfer_payment(request, order_number):
    """Verificar un pago por transferencia"""
    order = get_object_or_404(Order, order_number=order_number)
    
    try:
        transfer_payment = order.transfer_payment
    except TransferPayment.DoesNotExist:
        messages.error(request, 'No se encontró información de transferencia para este pedido.')
        return redirect('orders:admin_detail', order_number=order_number)
    
    # Cambiar estado a verificado
    transfer_payment.status = 'verified'
    transfer_payment.verified_by = request.user
    transfer_payment.verified_at = timezone.now()
    transfer_payment.verification_notes = request.POST.get('notes', '')
    transfer_payment.save()
    
    messages.success(request, f'Pago por transferencia del pedido #{order_number} verificado exitosamente.')
    return redirect('orders:admin_detail', order_number=order_number)


@staff_member_required
@require_POST
def approve_transfer_payment(request, order_number):
    """Aprobar un pago por transferencia"""
    order = get_object_or_404(Order, order_number=order_number)
    
    try:
        transfer_payment = order.transfer_payment
    except TransferPayment.DoesNotExist:
        messages.error(request, 'No se encontró información de transferencia para este pedido.')
        return redirect('orders:admin_detail', order_number=order_number)
    
    # Cambiar estado a aprobado
    transfer_payment.status = 'approved'
    transfer_payment.verified_by = request.user
    transfer_payment.verified_at = timezone.now()
    transfer_payment.verification_notes = request.POST.get('notes', '')
    transfer_payment.save()
    
    messages.success(request, f'Pago por transferencia del pedido #{order_number} aprobado exitosamente.')
    return redirect('orders:admin_detail', order_number=order_number)


@staff_member_required
@require_POST
def reject_transfer_payment(request, order_number):
    """Rechazar un pago por transferencia"""
    order = get_object_or_404(Order, order_number=order_number)
    
    try:
        transfer_payment = order.transfer_payment
    except TransferPayment.DoesNotExist:
        messages.error(request, 'No se encontró información de transferencia para este pedido.')
        return redirect('orders:admin_detail', order_number=order_number)
    
    # Cambiar estado a rechazado
    transfer_payment.status = 'rejected'
    transfer_payment.verified_by = request.user
    transfer_payment.verified_at = timezone.now()
    transfer_payment.verification_notes = request.POST.get('notes', 'Pago rechazado')
    transfer_payment.save()
    
    messages.warning(request, f'Pago por transferencia del pedido #{order_number} rechazado.')
    return redirect('orders:admin_detail', order_number=order_number)


@staff_member_required
@require_POST
def expire_transfer_payment(request, order_number):
    """Marcar como expirado un pago por transferencia"""
    order = get_object_or_404(Order, order_number=order_number)
    
    try:
        transfer_payment = order.transfer_payment
    except TransferPayment.DoesNotExist:
        messages.error(request, 'No se encontró información de transferencia para este pedido.')
        return redirect('orders:admin_detail', order_number=order_number)
    
    # Cambiar estado a expirado
    transfer_payment.status = 'expired'
    transfer_payment.verified_by = request.user
    transfer_payment.verified_at = timezone.now()
    transfer_payment.verification_notes = request.POST.get('notes', 'Pago expirado')
    transfer_payment.save()
    
    messages.info(request, f'Pago por transferencia del pedido #{order_number} marcado como expirado.')
    return redirect('orders:admin_detail', order_number=order_number)


@staff_member_required
def transfer_management_view(request):
    """Vista para gestionar todos los pagos por transferencia"""
    transfer_payments = TransferPayment.objects.select_related('order', 'bank_account', 'verified_by').order_by('-created_at')
    
    # Filtros
    status_filter = request.GET.get('status')
    if status_filter:
        transfer_payments = transfer_payments.filter(status=status_filter)
    
    context = {
        'transfer_payments': transfer_payments,
        'status_choices': TransferPayment.TRANSFER_STATUS_CHOICES,
        'current_status': status_filter,
        'pending_count': TransferPayment.objects.filter(status='pending').count(),
        'verified_count': TransferPayment.objects.filter(status='verified').count(),
        'approved_count': TransferPayment.objects.filter(status='approved').count(),
        'rejected_count': TransferPayment.objects.filter(status='rejected').count(),
        'expired_count': TransferPayment.objects.filter(status='expired').count(),
    }
    
    return render(request, 'orders/admin/transfer_management.html', context)
