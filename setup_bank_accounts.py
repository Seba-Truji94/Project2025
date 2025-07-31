#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dulce_bias_project.settings')
django.setup()

from orders.models import BankAccount

def setup_bank_accounts():
    """Crear cuentas bancarias para recibir transferencias."""
    
    accounts_data = [
        {
            'bank_name': 'Banco de Chile',
            'account_type': 'checking',
            'account_number': '123456789',
            'account_holder': 'Dulce Bias SpA',
            'rut': '76.123.456-7',
            'email_notification': 'pagos@dulcebias.cl',
            'is_active': True
        },
        {
            'bank_name': 'Banco Estado',
            'account_type': 'vista',
            'account_number': '987654321',
            'account_holder': 'Dulce Bias SpA',
            'rut': '76.123.456-7',
            'email_notification': 'pagos@dulcebias.cl',
            'is_active': True
        },
        {
            'bank_name': 'Banco Santander',
            'account_type': 'savings',
            'account_number': '555777999',
            'account_holder': 'Dulce Bias SpA',
            'rut': '76.123.456-7',
            'email_notification': 'pagos@dulcebias.cl',
            'is_active': True
        }
    ]

    print("🏦 Configurando cuentas bancarias...")
    print("=" * 50)
    
    for data in accounts_data:
        account, created = BankAccount.objects.get_or_create(
            bank_name=data['bank_name'],
            account_number=data['account_number'],
            defaults=data
        )
        
        if created:
            print(f"✅ Cuenta creada: {account.bank_name} - {account.account_number}")
        else:
            # Actualizar cuenta existente
            for key, value in data.items():
                setattr(account, key, value)
            account.save()
            print(f"🔄 Cuenta actualizada: {account.bank_name} - {account.account_number}")
        
        print(f"   🏛️  Banco: {account.bank_name}")
        print(f"   📄 Tipo: {account.get_account_type_display()}")
        print(f"   🔢 Número: {account.account_number}")
        print(f"   👤 Titular: {account.account_holder}")
        print(f"   🆔 RUT: {account.rut}")
        print(f"   ✅ Activa: {'Sí' if account.is_active else 'No'}")
        print()

    print("=" * 50)
    print(f"📊 Total de cuentas bancarias: {BankAccount.objects.count()}")
    print(f"🟢 Cuentas activas: {BankAccount.objects.filter(is_active=True).count()}")
    
    print("\n✅ ¡Cuentas bancarias configuradas exitosamente!")
    print("\n📋 Para gestionar las cuentas:")
    print("   1. Ve al admin de Django: http://127.0.0.1:8000/admin/")
    print("   2. Navega a Orders > Bank accounts")
    print("   3. Edita o agrega nuevas cuentas según necesites")

if __name__ == '__main__':
    setup_bank_accounts()
