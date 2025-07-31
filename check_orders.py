#!/usr/bin/env python3
"""
Script para verificar órdenes existentes
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dulce_bias_project.settings')
django.setup()

from orders.models import Order
from django.contrib.auth.models import User

def check_orders():
    print("🔍 VERIFICANDO ÓRDENES EN LA BASE DE DATOS")
    print("=" * 60)
    
    # Verificar total de órdenes
    total_orders = Order.objects.count()
    print(f"📊 Total de órdenes: {total_orders}")
    
    if total_orders == 0:
        print("❌ No hay órdenes en la base de datos")
        return
    
    # Mostrar las últimas 10 órdenes
    print(f"\n📋 Últimas {min(10, total_orders)} órdenes:")
    print("-" * 60)
    
    for order in Order.objects.all().order_by('-created_at')[:10]:
        print(f"🧾 {order.order_number}")
        print(f"   👤 Usuario: {order.user.username}")
        print(f"   📅 Creada: {order.created_at}")
        print(f"   📊 Estado: {order.status}")
        print(f"   💰 Total: ${order.total}")
        print()
    
    # Buscar específicamente la orden problemática
    problem_order = "DB-20250731-0006"
    print(f"🔍 Buscando orden específica: {problem_order}")
    
    try:
        order = Order.objects.get(order_number=problem_order)
        print(f"✅ Orden encontrada:")
        print(f"   👤 Usuario: {order.user.username}")
        print(f"   📊 Estado: {order.status}")
        print(f"   💰 Total: ${order.total}")
    except Order.DoesNotExist:
        print(f"❌ Orden {problem_order} NO EXISTE en la base de datos")
        
        # Verificar órdenes con números similares
        similar_orders = Order.objects.filter(order_number__contains="20250731")
        if similar_orders.exists():
            print(f"\n🔍 Órdenes similares encontradas:")
            for order in similar_orders:
                print(f"   - {order.order_number}")
        else:
            print(f"❌ No hay órdenes con fecha 20250731")

if __name__ == "__main__":
    check_orders()
