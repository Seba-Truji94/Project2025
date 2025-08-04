#!/usr/bin/env python
"""
Verificación de URLs corregidas en el perfil de usuario
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dulce_bias_project.settings')
django.setup()

from django.urls import reverse, NoReverseMatch

def verificar_urls():
    print("🔍 VERIFICANDO URLS CORREGIDAS")
    print("=" * 50)
    
    # URLs que deben funcionar
    urls_test = [
        ('orders:admin_dashboard', 'Admin Dashboard de Pedidos'),
        ('support:admin_management', 'Admin Management de Soporte'),
        ('management:dashboard', 'Management Dashboard'),
        ('accounts:profile', 'Perfil de Usuario'),
    ]
    
    print("✅ PROBANDO URLs:")
    for url_name, description in urls_test:
        try:
            url = reverse(url_name)
            print(f"   ✅ {description}: {url}")
        except NoReverseMatch as e:
            print(f"   ❌ {description}: Error - {str(e)}")
    
    # Verificar que la URL problemática ya no existe
    print("\n🚫 VERIFICANDO URLs PROBLEMÁTICAS:")
    problematic_urls = [
        ('support:admin_dashboard', 'URL problemática de support'),
    ]
    
    for url_name, description in problematic_urls:
        try:
            url = reverse(url_name)
            print(f"   ⚠️  {description}: Aún existe - {url}")
        except NoReverseMatch:
            print(f"   ✅ {description}: Correctamente removida")
    
    print("\n📄 ARCHIVO CORREGIDO:")
    print("   • templates/accounts/profile.html")
    print("     - support:admin_dashboard → support:admin_management")
    print("     - orders:admin_dashboard → mantenido (existe)")
    
    print("\n🎯 CAMBIO REALIZADO:")
    print("   Antes: {% url 'support:admin_dashboard' %}")
    print("   Ahora: {% url 'support:admin_management' %}")
    
    print("\n📋 URLS DISPONIBLES EN SUPPORT:")
    support_urls = [
        'support:admin_management',
        'support:admin_ticket_list', 
        'support:admin_statistics',
        'support:admin_category_management'
    ]
    
    for url_name in support_urls:
        try:
            url = reverse(url_name)
            print(f"   ✅ {url_name}: {url}")
        except NoReverseMatch:
            print(f"   ❌ {url_name}: No disponible")
    
    print("\n" + "=" * 50)
    print("✨ VERIFICACIÓN COMPLETADA")
    print("=" * 50)

if __name__ == '__main__':
    verificar_urls()
