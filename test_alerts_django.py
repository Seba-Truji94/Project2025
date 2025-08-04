#!/usr/bin/env python
"""
Script de prueba simple para la vista de alertas usando Django directamente
"""
import os
import sys
import django
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dulce_bias_project.settings')
django.setup()

# Importar después de configurar Django
from django.test import Client
from django.contrib.auth.models import User
from shop.models import Product, Category

def test_alerts_view():
    """Probar la vista de alertas directamente"""
    print("🧪 Probando vista de alertas directamente con Django...")
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    
    try:
        # Crear un cliente de prueba
        client = Client()
        
        # Intentar crear un superusuario de prueba
        try:
            superuser = User.objects.create_superuser(
                username='test_admin',
                email='test@example.com',
                password='test123'
            )
            print("✅ Superusuario de prueba creado")
        except:
            # Si ya existe, obtenerlo
            superuser = User.objects.filter(is_superuser=True).first()
            if not superuser:
                print("❌ No se pudo crear ni encontrar un superusuario")
                return
            print("✅ Usando superusuario existente")
        
        # Login
        client.force_login(superuser)
        print("✅ Autenticado como superusuario")
        
        # Verificar que tenemos algunos productos
        products_count = Product.objects.count()
        print(f"📦 Productos en la base de datos: {products_count}")
        
        # Hacer petición a la API
        response = client.get('/management/stock/alertas/api/')
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                import json
                data = json.loads(response.content.decode('utf-8'))
                print(f"✅ Respuesta JSON válida")
                print(f"🔍 Success: {data.get('success', False)}")
                
                if 'data' in data:
                    stats = data['data'].get('statistics', {})
                    alerts = data['data'].get('alerts', [])
                    
                    print(f"\n📈 ESTADÍSTICAS:")
                    print(f"  🔴 Críticas: {stats.get('critical_alerts', 0)}")
                    print(f"  🟡 Stock Bajo: {stats.get('low_stock_alerts', 0)}")
                    print(f"  ⚫ Sin Stock: {stats.get('out_of_stock', 0)}")
                    print(f"  📊 Total: {stats.get('total_alerts', 0)}")
                    
                    print(f"\n🚨 Alertas encontradas: {len(alerts)}")
                    if alerts:
                        for i, alert in enumerate(alerts[:3], 1):
                            print(f"  {i}. {alert['name']} - Stock: {alert['current_stock']} - Tipo: {alert['type']}")
                    
                else:
                    print(f"❌ No se encontraron datos en la respuesta")
                    
            except json.JSONDecodeError as e:
                print(f"❌ Error al decodificar JSON: {e}")
                print(f"📝 Contenido de respuesta (primeros 200 chars): {response.content[:200]}")
                
        else:
            print(f"❌ Error HTTP {response.status_code}")
            print(f"📝 Contenido: {response.content[:200]}")
            
        # Limpiar usuario de prueba
        try:
            if superuser.username == 'test_admin':
                superuser.delete()
                print("🧹 Usuario de prueba eliminado")
        except:
            pass
            
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        
    print("-" * 60)

if __name__ == "__main__":
    print("🚀 PRUEBA DIRECTA DE VISTA DE ALERTAS")
    print("=" * 60)
    test_alerts_view()
    print("\n🎯 FIN DE LA PRUEBA")
