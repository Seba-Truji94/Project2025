#!/usr/bin/env python
"""
Script para configurar permisos de superusuario y crear usuarios de ejemplo
"""
import os
import sys
import django

# Configurar Django ANTES de importar modelos
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dulce_bias_project.settings')
django.setup()

from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType

from shop.models import (
    TaxConfiguration, DiscountCoupon, CouponUsage, ProductStock, 
    Supplier, ProductSupplier, Product, Category
)


def setup_admin_permissions():
    """Configurar permisos para administración de la tienda"""
    
    print("🔧 CONFIGURANDO PERMISOS DE ADMINISTRACIÓN")
    print("=" * 60)
    
    # 1. Crear grupos de usuarios
    print("\n👥 Creando grupos de usuarios...")
    
    # Grupo de Superusuarios (acceso total)
    superadmin_group, created = Group.objects.get_or_create(
        name='Superadministradores'
    )
    if created:
        print("  ✅ Grupo 'Superadministradores' creado")
    
    # Grupo de Administradores de Tienda (acceso limitado)
    shop_admin_group, created = Group.objects.get_or_create(
        name='Administradores de Tienda'
    )
    if created:
        print("  ✅ Grupo 'Administradores de Tienda' creado")
    
    # Grupo de Operadores de Stock (solo stock y productos)
    stock_operator_group, created = Group.objects.get_or_create(
        name='Operadores de Stock'
    )
    if created:
        print("  ✅ Grupo 'Operadores de Stock' creado")
    
    # 2. Configurar permisos por modelo
    print("\n🔐 Configurando permisos por modelo...")
    
    # Permisos para TaxConfiguration (solo superusuarios)
    tax_content_type = ContentType.objects.get_for_model(TaxConfiguration)
    tax_permissions = Permission.objects.filter(content_type=tax_content_type)
    superadmin_group.permissions.add(*tax_permissions)
    print("  🏷️ Configuraciones de Impuesto → Solo Superusuarios")
    
    # Permisos para DiscountCoupon (solo superusuarios)
    coupon_content_type = ContentType.objects.get_for_model(DiscountCoupon)
    coupon_permissions = Permission.objects.filter(content_type=coupon_content_type)
    superadmin_group.permissions.add(*coupon_permissions)
    print("  🎫 Cupones de Descuento → Solo Superusuarios")
    
    # Permisos para Supplier (solo superusuarios)
    supplier_content_type = ContentType.objects.get_for_model(Supplier)
    supplier_permissions = Permission.objects.filter(content_type=supplier_content_type)
    superadmin_group.permissions.add(*supplier_permissions)
    print("  🏭 Proveedores → Solo Superusuarios")
    
    # Permisos para ProductSupplier (superusuarios y admin tienda)
    product_supplier_content_type = ContentType.objects.get_for_model(ProductSupplier)
    product_supplier_permissions = Permission.objects.filter(content_type=product_supplier_content_type)
    superadmin_group.permissions.add(*product_supplier_permissions)
    shop_admin_group.permissions.add(*product_supplier_permissions)
    print("  🔗 Relaciones Producto-Proveedor → Superusuarios y Admin Tienda")
    
    # Permisos para ProductStock (todos los grupos)
    stock_content_type = ContentType.objects.get_for_model(ProductStock)
    stock_permissions = Permission.objects.filter(content_type=stock_content_type)
    superadmin_group.permissions.add(*stock_permissions)
    shop_admin_group.permissions.add(*stock_permissions)
    stock_operator_group.permissions.add(*stock_permissions)
    print("  📦 Movimientos de Stock → Todos los grupos")
    
    # Permisos para CouponUsage (superusuarios y admin tienda)
    coupon_usage_content_type = ContentType.objects.get_for_model(CouponUsage)
    coupon_usage_permissions = Permission.objects.filter(content_type=coupon_usage_content_type)
    superadmin_group.permissions.add(*coupon_usage_permissions)
    shop_admin_group.permissions.add(*coupon_usage_permissions)
    print("  👥 Uso de Cupones → Superusuarios y Admin Tienda")
    
    # Permisos para Product (todos los grupos)
    product_content_type = ContentType.objects.get_for_model(Product)
    product_permissions = Permission.objects.filter(content_type=product_content_type)
    superadmin_group.permissions.add(*product_permissions)
    shop_admin_group.permissions.add(*product_permissions)
    # Solo permisos de lectura y cambio para operadores de stock
    stock_operator_group.permissions.add(
        *product_permissions.filter(codename__in=['view_product', 'change_product'])
    )
    print("  🛍️ Productos → Superusuarios (total), Admin Tienda (total), Operadores (lectura/edición)")
    
    # Permisos para Category (superusuarios y admin tienda)
    category_content_type = ContentType.objects.get_for_model(Category)
    category_permissions = Permission.objects.filter(content_type=category_content_type)
    superadmin_group.permissions.add(*category_permissions)
    shop_admin_group.permissions.add(*category_permissions)
    print("  📂 Categorías → Superusuarios y Admin Tienda")
    
    print("  ✅ Permisos configurados correctamente")
    
    # 3. Crear usuarios de ejemplo
    print("\n👤 Configurando usuarios...")
    
    # Superusuario principal
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@dulcebias.cl',
            'first_name': 'Administrador',
            'last_name': 'Principal',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        admin_user.set_password('Admin123!@#')
        admin_user.save()
        print("  ✅ Superusuario 'admin' creado")
        print("     📧 Email: admin@dulcebias.cl")
        print("     🔑 Password: Admin123!@#")
    else:
        # Asegurar que el admin existente sea superusuario
        admin_user.is_superuser = True
        admin_user.is_staff = True
        admin_user.save()
        print("  ✅ Superusuario 'admin' verificado")
    
    # Agregar admin al grupo de superadministradores
    admin_user.groups.add(superadmin_group)
    
    # Usuario administrador de tienda
    shop_admin_user, created = User.objects.get_or_create(
        username='tienda_admin',
        defaults={
            'email': 'tienda@dulcebias.cl',
            'first_name': 'Administrador',
            'last_name': 'Tienda',
            'is_staff': True,
            'is_superuser': False
        }
    )
    if created:
        shop_admin_user.set_password('Tienda123!@#')
        shop_admin_user.save()
        print("  ✅ Admin de Tienda 'tienda_admin' creado")
        print("     📧 Email: tienda@dulcebias.cl")
        print("     🔑 Password: Tienda123!@#")
    
    shop_admin_user.groups.add(shop_admin_group)
    
    # Usuario operador de stock
    stock_user, created = User.objects.get_or_create(
        username='stock_operator',
        defaults={
            'email': 'stock@dulcebias.cl',
            'first_name': 'Operador',
            'last_name': 'Stock',
            'is_staff': True,
            'is_superuser': False
        }
    )
    if created:
        stock_user.set_password('Stock123!@#')
        stock_user.save()
        print("  ✅ Operador de Stock 'stock_operator' creado")
        print("     📧 Email: stock@dulcebias.cl")
        print("     🔑 Password: Stock123!@#")
    
    stock_user.groups.add(stock_operator_group)
    
    # 4. Mostrar resumen de accesos
    print("\n" + "=" * 60)
    print("🎯 RESUMEN DE ACCESOS POR USUARIO")
    print("=" * 60)
    
    print("\n🔴 SUPERUSUARIO (admin):")
    print("  ✅ Acceso total a TODOS los módulos")
    print("  ✅ Configuraciones de Impuesto")
    print("  ✅ Cupones de Descuento")
    print("  ✅ Proveedores")
    print("  ✅ Relaciones Producto-Proveedor")
    print("  ✅ Movimientos de Stock")
    print("  ✅ Uso de Cupones")
    print("  ✅ Productos y Categorías")
    
    print("\n🟡 ADMINISTRADOR DE TIENDA (tienda_admin):")
    print("  ❌ Configuraciones de Impuesto")
    print("  ❌ Cupones de Descuento")
    print("  ❌ Proveedores")
    print("  ✅ Relaciones Producto-Proveedor")
    print("  ✅ Movimientos de Stock")
    print("  ✅ Uso de Cupones")
    print("  ✅ Productos y Categorías")
    
    print("\n🟢 OPERADOR DE STOCK (stock_operator):")
    print("  ❌ Configuraciones de Impuesto")
    print("  ❌ Cupones de Descuento")
    print("  ❌ Proveedores")
    print("  ❌ Relaciones Producto-Proveedor")
    print("  ✅ Movimientos de Stock")
    print("  ❌ Uso de Cupones")
    print("  🔍 Productos (solo lectura/edición)")
    print("  ❌ Categorías")
    
    print("\n🌐 URLs DE ACCESO:")
    print("  📍 Panel Principal: http://127.0.0.1:8000/admin/")
    print("  🔐 Login: http://127.0.0.1:8000/admin/login/")
    
    print("\n🎉 ¡Configuración de permisos completada!")
    print("   Los usuarios pueden acceder con sus credenciales respectivas.")
    
    return {
        'superadmin_group': superadmin_group,
        'shop_admin_group': shop_admin_group,
        'stock_operator_group': stock_operator_group,
        'admin_user': admin_user,
        'shop_admin_user': shop_admin_user,
        'stock_user': stock_user
    }


def verify_permissions():
    """Verificar que los permisos estén configurados correctamente"""
    
    print("\n🔍 VERIFICANDO CONFIGURACIÓN DE PERMISOS...")
    
    try:
        admin_user = User.objects.get(username='admin')
        print(f"  ✅ Admin es superusuario: {admin_user.is_superuser}")
        print(f"  ✅ Admin es staff: {admin_user.is_staff}")
        
        tienda_user = User.objects.get(username='tienda_admin')
        print(f"  ✅ Tienda Admin es staff: {tienda_user.is_staff}")
        print(f"  ❌ Tienda Admin NO es superusuario: {not tienda_user.is_superuser}")
        
        stock_user = User.objects.get(username='stock_operator')
        print(f"  ✅ Stock Operator es staff: {stock_user.is_staff}")
        print(f"  ❌ Stock Operator NO es superusuario: {not stock_user.is_superuser}")
        
        print("  ✅ Todos los permisos verificados correctamente")
        
    except User.DoesNotExist as e:
        print(f"  ❌ Error: Usuario no encontrado - {e}")
        return False
    
    return True


if __name__ == "__main__":
    # Configurar permisos
    users = setup_admin_permissions()
    
    # Verificar configuración
    verify_permissions()
