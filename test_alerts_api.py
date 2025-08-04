#!/usr/bin/env python
"""
Script para probar la API de alertas de stock en tiempo real
"""
import os
import sys
import django
import urllib.request
import urllib.error
import json
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dulce_bias_project.settings')
django.setup()

def test_alerts_api():
    """Probar la nueva API de alertas de stock"""
    print("🧪 Probando API de alertas de stock...")
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    
    base_url = "http://127.0.0.1:8002"
    api_url = f"{base_url}/management/stock/alertas/api/"
    
    try:
        print(f"📡 Haciendo petición a: {api_url}")
        
        # Crear petición HTTP
        req = urllib.request.Request(api_url)
        req.add_header('User-Agent', 'TestScript/1.0')
        
        with urllib.request.urlopen(req, timeout=10) as response:
            status_code = response.getcode()
            print(f"📊 Status Code: {status_code}")
            
            if status_code == 200:
                data = json.loads(response.read().decode('utf-8'))
                print(f"✅ Respuesta exitosa!")
                print(f"🔍 Success: {data.get('success', False)}")
                
                if 'data' in data:
                    stats = data['data'].get('statistics', {})
                    alerts = data['data'].get('alerts', [])
                    last_updated = data['data'].get('last_updated', '')
                    
                    print(f"\n📈 ESTADÍSTICAS:")
                    print(f"  🔴 Críticas: {stats.get('critical_alerts', 0)}")
                    print(f"  🟡 Stock Bajo: {stats.get('low_stock_alerts', 0)}")
                    print(f"  ⚫ Sin Stock: {stats.get('out_of_stock', 0)}")
                    print(f"  📊 Total: {stats.get('total_alerts', 0)}")
                    print(f"  🕐 Actualizado: {last_updated}")
                    
                    if alerts:
                        print(f"\n🚨 ALERTAS DETECTADAS ({len(alerts)}):")
                        for i, alert in enumerate(alerts[:5], 1):  # Mostrar solo las primeras 5
                            priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                            type_emoji = {"critical": "⚠️", "low": "⚡", "out": "❌"}
                            
                            print(f"  {i}. {type_emoji.get(alert['type'], '📦')} {alert['name']}")
                            print(f"     Stock: {alert['current_stock']} | Prioridad: {priority_emoji.get(alert['priority'], '⚪')} {alert['priority']}")
                            print(f"     Categoría: {alert['category']}")
                            
                            if i >= 5 and len(alerts) > 5:
                                print(f"     ... y {len(alerts) - 5} alertas más")
                                break
                    else:
                        print(f"\n✅ ¡Excelente! No hay alertas de stock críticas")
                        
                else:
                    print(f"❌ No se encontraron datos en la respuesta")
            else:
                print(f"❌ Error HTTP {status_code}")
                
    except urllib.error.HTTPError as e:
        if e.code == 403:
            print(f"🔒 Error 403: Acceso denegado")
            print("💡 Necesitas estar autenticado como superusuario")
        elif e.code == 404:
            print(f"🔍 Error 404: Endpoint no encontrado")
            print("💡 Verifica que la URL esté configurada correctamente")
        else:
            print(f"❌ Error HTTP {e.code}: {e.reason}")
            
    except urllib.error.URLError as e:
        print(f"❌ Error de conexión: {e.reason}")
        print(f"💡 Asegúrate de que el servidor Django esté ejecutándose en {base_url}")
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        
    print("-" * 60)

def check_server_status():
    """Verificar si el servidor está ejecutándose"""
    print("🔍 Verificando estado del servidor...")
    
    try:
        req = urllib.request.Request("http://127.0.0.1:8002/")
        req.add_header('User-Agent', 'TestScript/1.0')
        
        with urllib.request.urlopen(req, timeout=5) as response:
            status_code = response.getcode()
            if status_code in [200, 302, 404]:  # Cualquier respuesta válida
                print("✅ Servidor Django está ejecutándose")
                return True
            else:
                print(f"⚠️ Servidor responde con código {status_code}")
                return False
    except:
        print("❌ Servidor Django no está ejecutándose")
        print("💡 Ejecuta: python manage.py runserver 127.0.0.1:8002")
        return False

if __name__ == "__main__":
    print("🚀 PRUEBA DE SISTEMA DE ALERTAS DE STOCK EN TIEMPO REAL")
    print("=" * 60)
    
    # Verificar servidor
    if check_server_status():
        print()
        # Probar API
        test_alerts_api()
        
        print("\n🔄 PRÓXIMOS PASOS:")
        print("1. Visita http://127.0.0.1:8002/management/stock/alertas/")
        print("2. Las alertas se actualizarán automáticamente cada 30 segundos")
        print("3. Haz cambios en el stock de productos para ver las alertas en tiempo real")
        
    print("\n🎯 FIN DE LA PRUEBA")
