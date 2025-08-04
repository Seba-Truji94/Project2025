#!/usr/bin/env python
"""
Script de prueba para la funcionalidad de detalles de movimientos de stock
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dulce_bias_project.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from shop.models import ProductStock
import json

def test_stock_movement_detail():
    print("🧪 Probando funcionalidad de detalles de movimientos de stock...")
    
    # Crear cliente de prueba
    client = Client()
    
    # Obtener un superusuario
    try:
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            print("❌ No hay superusuarios en la base de datos")
            return
        
        print(f"✅ Usuario admin encontrado: {admin_user.username}")
        
        # Hacer login
        client.force_login(admin_user)
        print("✅ Login exitoso")
        
        # Obtener un movimiento de stock para probar
        movement = ProductStock.objects.first()
        if not movement:
            print("❌ No hay movimientos de stock en la base de datos")
            return
        
        print(f"✅ Movimiento de prueba: ID {movement.id} - {movement.product.name}")
        
        # Probar la vista de detalle
        response = client.get(f'/management/stock/movimiento/{movement.id}/')
        
        print(f"📊 Código de respuesta: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ Respuesta JSON válida")
                
                if data.get('success'):
                    print("✅ API responde exitosamente")
                    print(f"📦 Producto: {data['data']['product']['name']}")
                    print(f"🔄 Tipo: {data['data']['movement_type']}")
                    print(f"📈 Cantidad: {data['data']['quantity']}")
                    print(f"👤 Usuario: {data['data']['user']}")
                    print("✅ ¡Todos los datos están presentes!")
                else:
                    print(f"❌ API retorna error: {data.get('error')}")
                    
            except json.JSONDecodeError:
                print("❌ Respuesta no es JSON válido")
                print(f"Contenido: {response.content[:500]}")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"Contenido: {response.content[:500]}")
            
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_stock_movement_detail()
