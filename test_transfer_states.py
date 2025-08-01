#!/usr/bin/env python
"""
Script para probar los nuevos estados de transferencia
Ejecutar con: python manage.py shell < test_transfer_states.py
"""

from orders.models import Order, TransferPayment, BankAccount
from django.contrib.auth.models import User
from decimal import Decimal

def test_transfer_states():
    print("🔄 Probando los nuevos estados de transferencia...")
    
    # Buscar un usuario y crear datos de prueba si es necesario
    user = User.objects.first()
    if not user:
        print("❌ No hay usuarios en el sistema")
        return
    
    # Buscar un pedido con pago pendiente
    order = Order.objects.filter(
        payment_method='transfer', 
        payment_status='pending'
    ).first()
    
    if not order:
        print("⚠️ No se encontró ningún pedido con pago por transferencia pendiente")
        print("📋 Estados disponibles:")
        for order in Order.objects.filter(payment_method='transfer')[:5]:
            print(f"   - Pedido #{order.order_number}: payment_status={order.payment_status}")
        return
    
    print(f"📦 Usando pedido #{order.order_number}")
    print(f"   Estado inicial: payment_status={order.payment_status}")
    
    # Buscar transferencia asociada
    transfer = getattr(order, 'transfer_payment', None)
    if not transfer:
        print("⚠️ Este pedido no tiene transferencia asociada")
        return
    
    print(f"💳 Transferencia encontrada: status={transfer.status}")
    
    # Simular verificación (NO debe cambiar payment_status)
    if transfer.status == 'pending':
        print("\n🔍 Simulando verificación...")
        transfer.status = 'verified'
        transfer.verification_notes = 'Comprobante verificado correctamente, esperando aprobación'
        transfer.save()
        
        order.refresh_from_db()
        print(f"   ✅ Transfer status: {transfer.get_status_display()}")
        print(f"   📋 Order payment_status: {order.payment_status} (debe seguir siendo 'pending')")
        print(f"   📝 Notas: {transfer.verification_notes}")
        
        if order.payment_status == 'pending':
            print("   ✅ CORRECTO: El estado verificado NO marca el pago como completado")
        else:
            print("   ❌ ERROR: El estado verificado cambió el payment_status")
    
    # Simular aprobación (SÍ debe cambiar payment_status)
    if transfer.status == 'verified':
        print("\n✅ Simulando aprobación...")
        transfer.status = 'approved'
        transfer.verification_notes += ' - APROBADO por administrador'
        transfer.save()
        
        order.refresh_from_db()
        print(f"   ✅ Transfer status: {transfer.get_status_display()}")
        print(f"   📋 Order payment_status: {order.payment_status} (debe ser 'paid')")
        print(f"   📋 Order status: {order.status} (debe ser 'confirmed')")
        
        if order.payment_status == 'paid':
            print("   ✅ CORRECTO: El estado aprobado marca el pago como completado")
        else:
            print("   ❌ ERROR: El estado aprobado NO cambió el payment_status")
    
    print("\n📊 Resumen de comportamiento esperado:")
    print("   • 'pending' → transferencia enviada, esperando verificación")
    print("   • 'verified' → comprobante verificado, esperando aprobación (payment_status sigue 'pending')")
    print("   • 'approved' → pago aprobado y completado (payment_status cambia a 'paid')")
    print("   • 'rejected' → pago rechazado")
    print("   • 'expired' → pago expirado")

if __name__ == "__main__":
    test_transfer_states()
