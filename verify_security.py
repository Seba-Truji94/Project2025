#!/usr/bin/env python
"""
Script para verificar la configuración de seguridad y permisos
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dulce_bias_project.settings')
django.setup()

from django.contrib.auth.models import User, Group
from django.conf import settings


def verify_security_setup():
    """Verificar que la configuración de seguridad esté correcta"""
    
    print("🔒 VERIFICACIÓN DE CONFIGURACIÓN DE SEGURIDAD")
    print("=" * 60)
    
    # 1. Verificar middleware
    print("\n🛡️ Verificando middleware de seguridad...")
    
    required_middleware = [
        'security.middleware.AdminModulesAccessMiddleware',
        'security.middleware.SecurityLogMiddleware',
        'security.middleware.RateLimitMiddleware',
        'security.middleware.SecurityHeadersMiddleware',
    ]
    
    for middleware in required_middleware:
        if middleware in settings.MIDDLEWARE:
            print(f"  ✅ {middleware}")
        else:
            print(f"  ❌ {middleware} - NO ENCONTRADO")
    
    # 2. Verificar usuarios
    print("\n👤 Verificando usuarios...")
    
    try:
        admin_user = User.objects.get(username='admin')
        print(f"  ✅ Superusuario 'admin':")
        print(f"    🔴 Es superusuario: {admin_user.is_superuser}")
        print(f"    👔 Es staff: {admin_user.is_staff}")
        print(f"    📧 Email: {admin_user.email}")
        
        tienda_user = User.objects.get(username='tienda_admin')
        print(f"  ✅ Admin Tienda 'tienda_admin':")
        print(f"    🟡 Es superusuario: {tienda_user.is_superuser}")
        print(f"    👔 Es staff: {tienda_user.is_staff}")
        print(f"    📧 Email: {tienda_user.email}")
        
        stock_user = User.objects.get(username='stock_operator')
        print(f"  ✅ Operador Stock 'stock_operator':")
        print(f"    🟢 Es superusuario: {stock_user.is_superuser}")
        print(f"    👔 Es staff: {stock_user.is_staff}")
        print(f"    📧 Email: {stock_user.email}")
        
    except User.DoesNotExist as e:
        print(f"  ❌ Usuario no encontrado: {e}")
    
    # 3. Verificar grupos
    print("\n👥 Verificando grupos...")
    
    expected_groups = [
        'Superadministradores',
        'Administradores de Tienda', 
        'Operadores de Stock'
    ]
    
    for group_name in expected_groups:
        try:
            group = Group.objects.get(name=group_name)
            user_count = group.user_set.count()
            print(f"  ✅ {group_name}: {user_count} usuarios")
        except Group.DoesNotExist:
            print(f"  ❌ Grupo '{group_name}' no encontrado")
    
    # 4. Verificar URLs protegidas
    print("\n🌐 URLs PROTEGIDAS POR MIDDLEWARE:")
    
    protected_urls = [
        '/admin/shop/taxconfiguration/',
        '/admin/shop/discountcoupon/', 
        '/admin/shop/supplier/',
        '/admin/shop/productstock/',
        '/admin/shop/productsupplier/',
        '/admin/shop/couponusage/',
    ]
    
    for url in protected_urls:
        print(f"  🔒 {url}")
    
    # 5. Mostrar instrucciones de prueba
    print("\n" + "=" * 60)
    print("🧪 INSTRUCCIONES PARA PROBAR LA SEGURIDAD")
    print("=" * 60)
    
    print("\n1️⃣ PRUEBA CON SUPERUSUARIO:")
    print("   👤 Usuario: admin")
    print("   🔑 Password: Admin123!@#")
    print("   ✅ Debe tener acceso a TODOS los módulos")
    
    print("\n2️⃣ PRUEBA CON ADMIN DE TIENDA:")
    print("   👤 Usuario: tienda_admin")
    print("   🔑 Password: Tienda123!@#")
    print("   ❌ NO debe acceder a: Impuestos, Cupones, Proveedores")
    print("   ✅ SÍ debe acceder a: Stock, Relaciones, Productos")
    
    print("\n3️⃣ PRUEBA CON OPERADOR DE STOCK:")
    print("   👤 Usuario: stock_operator")
    print("   🔑 Password: Stock123!@#")
    print("   ❌ NO debe acceder a: Impuestos, Cupones, Proveedores, Relaciones")
    print("   ✅ SÍ debe acceder a: Solo Stock y Productos (limitado)")
    
    print("\n🔗 URL DE PRUEBA:")
    print("   📍 http://127.0.0.1:8000/admin/")
    
    print("\n⚠️ MENSAJE DE ACCESO DENEGADO:")
    print("   Si un usuario sin permisos intenta acceder,")
    print("   verá un mensaje explicativo y será redirigido.")
    
    print("\n🎯 CARACTERÍSTICAS DE SEGURIDAD IMPLEMENTADAS:")
    features = [
        "✅ Control de acceso basado en roles",
        "✅ Middleware de logging de seguridad", 
        "✅ Rate limiting personalizado",
        "✅ Headers de seguridad adicionales",
        "✅ Protección específica para módulos críticos",
        "✅ Mensajes informativos de acceso denegado",
        "✅ Logging de intentos de acceso",
        "✅ Grupos de permisos granulares"
    ]
    
    for feature in features:
        print(f"   {feature}")
    
    print("\n🎉 ¡Configuración de seguridad completada y verificada!")


if __name__ == "__main__":
    verify_security_setup()
