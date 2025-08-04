#!/usr/bin/env python
"""
Prueba la funcionalidad de editar stock desde alertas
Verifica que la URL con parámetro product funcione correctamente
"""
import os
import sys
import django
from django.test import Client

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dulce_bias_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from shop.models import Product

User = get_user_model()

def test_edit_stock_link():
    """Prueba la funcionalidad de editar stock"""
    print("🔗 PRUEBA DE ENLACE EDITAR STOCK")
    print("=" * 50)
    
    # Crear cliente de prueba
    client = Client()
    
    # Obtener superusuario
    superuser = User.objects.filter(is_superuser=True).first()
    if not superuser:
        print("❌ No hay superusuario disponible")
        return
    
    client.force_login(superuser)
    print(f"✅ Autenticado como: {superuser.username}")
    
    # Obtener un producto para probar
    product = Product.objects.first()
    if not product:
        print("❌ No hay productos disponibles")
        return
    
    print(f"🎯 Probando con producto: {product.name} (ID: {product.id})")
    
    # Probar la URL de edición de stock con parámetro
    url = f'/management/stock/movimiento/?product={product.id}'
    print(f"📡 Probando URL: {url}")
    
    response = client.get(url)
    print(f"📊 Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ URL responde correctamente")
        
        # Verificar que el contexto contiene el producto preseleccionado
        if hasattr(response, 'context') and response.context:
            context = response.context
            if 'preselected_product' in context:
                preselected = context['preselected_product']
                print(f"✅ Producto preseleccionado: {preselected.name}")
                
                if preselected.id == product.id:
                    print("🎉 ¡ÉXITO! El producto se preselecciona correctamente")
                else:
                    print("⚠️ El producto preseleccionado no coincide")
            else:
                print("⚠️ No se encontró producto preseleccionado en el contexto")
        else:
            print("⚠️ No se pudo acceder al contexto de la respuesta")
            
        # Verificar que el formulario está presente
        content = response.content.decode('utf-8')
        if 'id_product' in content:
            print("✅ Formulario de producto encontrado")
        else:
            print("❌ Formulario de producto no encontrado")
            
    elif response.status_code == 302:
        print(f"📄 Redirección a: {response.url}")
    else:
        print(f"❌ Error HTTP {response.status_code}")
    
    # Probar también sin parámetro
    print("\n" + "-" * 30)
    print("🔗 Probando URL sin parámetro")
    url_sin_parametro = '/management/stock/movimiento/'
    response2 = client.get(url_sin_parametro)
    print(f"📡 URL: {url_sin_parametro}")
    print(f"📊 Status Code: {response2.status_code}")
    
    if response2.status_code == 200:
        print("✅ URL sin parámetro también funciona")
    else:
        print(f"❌ URL sin parámetro falla: {response2.status_code}")
    
    print("\n" + "=" * 50)
    print("🎯 FIN DE LA PRUEBA")

if __name__ == '__main__':
    test_edit_stock_link()
