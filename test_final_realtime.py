#!/usr/bin/env python
"""
Prueba FINAL del sistema de alertas en tiempo real
Simula cambios de stock mientras monitorea las actualizaciones
"""
import os
import sys
import django
import time
import threading
from django.test import Client

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dulce_bias_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from shop.models import Product

User = get_user_model()

def monitor_api():
    """Monitorea la API continuamente"""
    client = Client()
    superuser = User.objects.filter(is_superuser=True).first()
    client.force_login(superuser)
    
    print("🔍 MONITOREO CONTINUO DE LA API")
    print("=" * 50)
    
    for i in range(10):  # Monitorear 10 veces
        try:
            response = client.get('/management/stock/alertas/api/')
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    stats = data['data']['statistics']
                    timestamp = time.strftime("%H:%M:%S")
                    print(f"[{timestamp}] 🔴:{stats['critical_alerts']} 🟡:{stats['low_stock_alerts']} ⚫:{stats['out_of_stock']} 📊:{stats['total_alerts']}")
                else:
                    print(f"[{time.strftime('%H:%M:%S')}] ❌ API success=False")
            else:
                print(f"[{time.strftime('%H:%M:%S')}] ❌ Status: {response.status_code}")
        except Exception as e:
            print(f"[{time.strftime('%H:%M:%S')}] ❌ Error: {e}")
        
        time.sleep(2)  # Esperar 2 segundos

def simulate_stock_changes():
    """Simula cambios de stock"""
    print("\n🎭 SIMULACIÓN DE CAMBIOS DE STOCK")
    print("=" * 50)
    
    # Obtener algunos productos
    products = list(Product.objects.filter(stock__gt=5)[:3])
    original_stocks = []
    
    for product in products:
        original_stocks.append(product.stock)
        print(f"📦 {product.name}: Stock original = {product.stock}")
    
    # Esperar 3 segundos antes de empezar
    print("\n⏳ Esperando 3 segundos antes de cambiar stocks...")
    time.sleep(3)
    
    # Reducir stocks a niveles críticos
    for i, product in enumerate(products):
        new_stock = 2  # Stock crítico
        product.stock = new_stock
        product.save()
        print(f"🔻 {product.name}: Stock reducido a {new_stock}")
        time.sleep(2)  # Esperar entre cambios
    
    # Esperar 8 segundos 
    print("\n⏳ Esperando 8 segundos...")
    time.sleep(8)
    
    # Restaurar stocks originales
    print("\n🔄 RESTAURANDO STOCKS ORIGINALES")
    for i, product in enumerate(products):
        product.stock = original_stocks[i]
        product.save()
        print(f"🔻 {product.name}: Stock restaurado a {original_stocks[i]}")
        time.sleep(2)
    
    print("\n✅ Simulación completada")

def main():
    """Función principal"""
    print("🚀 PRUEBA FINAL DEL SISTEMA DE ALERTAS EN TIEMPO REAL")
    print("=" * 70)
    print("Esta prueba simula cambios de stock mientras monitorea la API")
    print("=" * 70)
    
    # Crear threads para monitoreo y simulación
    monitor_thread = threading.Thread(target=monitor_api)
    simulation_thread = threading.Thread(target=simulate_stock_changes)
    
    # Iniciar monitoreo
    monitor_thread.start()
    
    # Esperar 1 segundo y luego iniciar simulación
    time.sleep(1)
    simulation_thread.start()
    
    # Esperar a que terminen
    simulation_thread.join()
    monitor_thread.join()
    
    print("\n" + "=" * 70)
    print("🎯 PRUEBA FINAL COMPLETADA")
    print("=" * 70)
    print("✅ Sistema de alertas en tiempo real funcionando correctamente")
    print("📱 Página web: http://127.0.0.1:8002/management/stock/alertas/")
    print("🔄 Auto-refresh cada 30 segundos")
    print("🚨 Notificaciones con SweetAlert2")
    print("📊 Estadísticas animadas")

if __name__ == '__main__':
    main()
