#!/usr/bin/env python
"""
Prueba las actualizaciones en tiempo real de las alertas de stock
Modifica el stock de un producto y verifica que las alertas se actualicen
"""
import os
import sys
import django
import time
from django.test import Client

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dulce_bias_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from shop.models import Product

User = get_user_model()

def test_realtime_updates():
    """Prueba las actualizaciones en tiempo real"""
    print("🔄 PRUEBA DE ACTUALIZACIONES EN TIEMPO REAL")
    print("=" * 60)
    
    # Crear cliente de prueba
    client = Client()
    
    # Obtener o crear superusuario
    try:
        superuser = User.objects.filter(is_superuser=True).first()
        if not superuser:
            superuser = User.objects.create_superuser(
                username='testadmin',
                email='test@test.com',
                password='testpass123'
            )
        print(f"✅ Usando superusuario: {superuser.username}")
    except Exception as e:
        print(f"❌ Error con superusuario: {e}")
        return
    
    # Autenticarse
    client.force_login(superuser)
    print("✅ Autenticado como superusuario")
    
    # Obtener estado inicial
    response = client.get('/management/stock/alertas/api/')
    if response.status_code == 200:
        initial_data = response.json()
        if initial_data.get('success'):
            data = initial_data['data']
            stats = data['statistics']
            print(f"📊 ESTADO INICIAL:")
            print(f"  🔴 Críticas: {stats['critical_alerts']}")
            print(f"  🟡 Stock Bajo: {stats['low_stock_alerts']}")
            print(f"  ⚫ Sin Stock: {stats['out_of_stock']}")
            print(f"  📊 Total: {stats['total_alerts']}")
        else:
            print("❌ API devolvió success=False")
            return
    else:
        print(f"❌ Error obteniendo estado inicial: {response.status_code}")
        return
    
    # Encontrar un producto para modificar
    product = Product.objects.filter(stock__gt=10).first()
    if not product:
        print("❌ No hay productos con stock > 10 para probar")
        return
    
    original_stock = product.stock
    print(f"\n🎯 MODIFICANDO PRODUCTO: {product.name}")
    print(f"   Stock original: {original_stock}")
    
    # Reducir stock a nivel crítico
    product.stock = 3
    product.save()
    print(f"   ✅ Stock reducido a: {product.stock}")
    
    # Esperar un momento
    time.sleep(1)
    
    # Verificar actualización
    response = client.get('/management/stock/alertas/api/')
    if response.status_code == 200:
        updated_data = response.json()
        if updated_data.get('success'):
            data = updated_data['data']
            stats = data['statistics']
            print(f"\n📊 ESTADO DESPUÉS DE MODIFICAR:")
            print(f"  🔴 Críticas: {stats['critical_alerts']}")
            print(f"  🟡 Stock Bajo: {stats['low_stock_alerts']}")
            print(f"  ⚫ Sin Stock: {stats['out_of_stock']}")
            print(f"  📊 Total: {stats['total_alerts']}")
            
            # Verificar si la alerta aparece
            product_found = False
            alerts = data.get('alerts', [])
            for alert in alerts:
                if alert['id'] == product.id:
                    product_found = True
                    print(f"  ✅ Producto encontrado en alertas: {alert['type']}")
                    break
            
            if not product_found:
                print(f"  ⚠️ Producto no encontrado en alertas")
            
            # Comparar estadísticas
            initial_stats = initial_data['data']['statistics']
            if stats['critical_alerts'] > initial_stats['critical_alerts']:
                print("  🎉 ÉXITO: Alertas críticas aumentaron correctamente")
            else:
                print("  ⚠️ Alertas críticas no cambiaron como se esperaba")
        else:
            print("❌ API devolvió success=False en actualización")
            
    else:
        print(f"❌ Error obteniendo estado actualizado: {response.status_code}")
    
    # Restaurar stock original
    product.stock = original_stock
    product.save()
    print(f"\n🔄 Stock restaurado a: {product.stock}")
    
    # Verificar restauración
    response = client.get('/management/stock/alertas/api/')
    if response.status_code == 200:
        final_data = response.json()
        if final_data.get('success'):
            data = final_data['data']
            stats = data['statistics']
            print(f"\n📊 ESTADO FINAL (RESTAURADO):")
            print(f"  🔴 Críticas: {stats['critical_alerts']}")
            print(f"  🟡 Stock Bajo: {stats['low_stock_alerts']}")
            print(f"  ⚫ Sin Stock: {stats['out_of_stock']}")
            print(f"  📊 Total: {stats['total_alerts']}")
            
            initial_stats = initial_data['data']['statistics']
            if stats['critical_alerts'] == initial_stats['critical_alerts']:
                print("  🎉 ÉXITO: Estadísticas restauradas correctamente")
            else:
                print("  ⚠️ Estadísticas no se restauraron completamente")
        else:
            print("❌ API devolvió success=False en verificación final")
    
    print("\n" + "-" * 60)
    print("🎯 FIN DE LA PRUEBA DE TIEMPO REAL")

if __name__ == '__main__':
    test_realtime_updates()
