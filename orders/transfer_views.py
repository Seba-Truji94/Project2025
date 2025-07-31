from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.urls import reverse
from orders.models import Order, BankAccount, TransferPayment
from cart.models import Cart


@login_required
def transfer_payment_view(request, order_number):
    """Vista para mostrar información de transferencia y formulario de comprobante"""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    
    # Verificar que el pedido esté en estado correcto
    if order.payment_method != 'transfer':
        messages.error(request, 'Este pedido no está configurado para pago por transferencia.')
        return redirect('orders:order_detail', order_number=order_number)
    
    if order.payment_status == 'paid':
        messages.info(request, 'Este pedido ya ha sido pagado.')
        return redirect('orders:order_detail', order_number=order_number)
    
    # Obtener cuentas bancarias activas
    bank_accounts = BankAccount.objects.filter(is_active=True)
    
    if not bank_accounts.exists():
        messages.error(request, 'No hay cuentas bancarias disponibles. Contacta con atención al cliente.')
        return redirect('orders:order_detail', order_number=order_number)
    
    # Verificar si ya existe un pago por transferencia
    transfer_payment = None
    try:
        transfer_payment = TransferPayment.objects.get(order=order)
    except TransferPayment.DoesNotExist:
        pass
    
    if request.method == 'POST':
        return handle_transfer_payment_submission(request, order, bank_accounts)
    
    context = {
        'order': order,
        'bank_accounts': bank_accounts,
        'transfer_payment': transfer_payment,
    }
    
    return render(request, 'orders/transfer_payment.html', context)


def handle_transfer_payment_submission(request, order, bank_accounts):
    """Manejar el envío del comprobante de transferencia"""
    # Obtener datos del formulario
    bank_account_id = request.POST.get('bank_account')
    transfer_amount = request.POST.get('transfer_amount')
    transfer_date = request.POST.get('transfer_date')
    reference_number = request.POST.get('reference_number')
    sender_name = request.POST.get('sender_name')
    sender_rut = request.POST.get('sender_rut')
    sender_bank = request.POST.get('sender_bank')
    receipt_image = request.FILES.get('receipt_image')
    
    # Validaciones
    if not all([bank_account_id, transfer_amount, transfer_date, reference_number, 
                sender_name, sender_rut, sender_bank, receipt_image]):
        messages.error(request, 'Por favor completa todos los campos y sube el comprobante.')
        return redirect('orders:transfer_payment', order_number=order.order_number)
    
    try:
        bank_account = BankAccount.objects.get(id=bank_account_id, is_active=True)
    except BankAccount.DoesNotExist:
        messages.error(request, 'Cuenta bancaria no válida.')
        return redirect('orders:transfer_payment', order_number=order.order_number)
    
    # Validar que el monto coincida con el total del pedido
    try:
        transfer_amount_decimal = float(transfer_amount)
        if abs(transfer_amount_decimal - float(order.total)) > 100:  # Tolerancia de $100
            messages.warning(
                request, 
                f'El monto transferido (${transfer_amount_decimal:,.0f}) no coincide exactamente '
                f'con el total del pedido (${order.total:,.0f}). El pedido será revisado.'
            )
    except ValueError:
        messages.error(request, 'Monto de transferencia no válido.')
        return redirect('orders:transfer_payment', order_number=order.order_number)
    
    # Crear o actualizar el pago por transferencia
    transfer_payment, created = TransferPayment.objects.get_or_create(
        order=order,
        defaults={
            'bank_account': bank_account,
            'transfer_amount': transfer_amount,
            'transfer_date': transfer_date,
            'reference_number': reference_number,
            'sender_name': sender_name,
            'sender_rut': sender_rut,
            'sender_bank': sender_bank,
            'receipt_image': receipt_image,
            'status': 'pending'
        }
    )
    
    if not created:
        # Actualizar pago existente
        transfer_payment.bank_account = bank_account
        transfer_payment.transfer_amount = transfer_amount
        transfer_payment.transfer_date = transfer_date
        transfer_payment.reference_number = reference_number
        transfer_payment.sender_name = sender_name
        transfer_payment.sender_rut = sender_rut
        transfer_payment.sender_bank = sender_bank
        transfer_payment.receipt_image = receipt_image
        transfer_payment.status = 'pending'
        transfer_payment.save()
    
    messages.success(
        request,
        '✅ Comprobante de transferencia enviado exitosamente. '
        'Tu pago será verificado en un plazo máximo de 24 horas.'
    )
    
    return redirect('orders:order_detail', order_number=order.order_number)


@login_required
def transfer_instructions_view(request):
    """Vista para mostrar instrucciones generales de transferencia"""
    bank_accounts = BankAccount.objects.filter(is_active=True)
    
    context = {
        'bank_accounts': bank_accounts,
    }
    
    return render(request, 'orders/transfer_instructions.html', context)
