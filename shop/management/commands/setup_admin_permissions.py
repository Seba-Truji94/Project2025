"""
Comando de administración para configurar permisos de usuarios
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from shop.models import (
    TaxConfiguration, DiscountCoupon, CouponUsage, ProductStock, 
    Supplier, ProductSupplier, Product, Category
)


class Command(BaseCommand):
    help = 'Configura permisos de administración para los nuevos módulos'

    def handle(self, *args, **options):
        self.stdout.write("🔧 CONFIGURANDO PERMISOS DE ADMINISTRACIÓN")
        self.stdout.write("=" * 60)
        
        # 1. Crear grupos de usuarios
        self.stdout.write("\n👥 Creando grupos de usuarios...")
        
        # Grupo de Superusuarios (acceso total)
        superadmin_group, created = Group.objects.get_or_create(
            name='Superadministradores'
        )
        if created:
            self.stdout.write("  ✅ Grupo 'Superadministradores' creado")
        
        # Grupo de Administradores de Tienda (acceso limitado)
        shop_admin_group, created = Group.objects.get_or_create(
            name='Administradores de Tienda'
        )
        if created:
            self.stdout.write("  ✅ Grupo 'Administradores de Tienda' creado")
        
        # Grupo de Operadores de Stock (solo stock y productos)
        stock_operator_group, created = Group.objects.get_or_create(
            name='Operadores de Stock'
        )
        if created:
            self.stdout.write("  ✅ Grupo 'Operadores de Stock' creado")
        
        # 2. Configurar permisos por modelo
        self.stdout.write("\n🔐 Configurando permisos por modelo...")
        
        # Permisos para TaxConfiguration (solo superusuarios)
        tax_content_type = ContentType.objects.get_for_model(TaxConfiguration)
        tax_permissions = Permission.objects.filter(content_type=tax_content_type)
        superadmin_group.permissions.add(*tax_permissions)
        self.stdout.write("  🏷️ Configuraciones de Impuesto → Solo Superusuarios")
        
        # Permisos para DiscountCoupon (solo superusuarios)
        coupon_content_type = ContentType.objects.get_for_model(DiscountCoupon)
        coupon_permissions = Permission.objects.filter(content_type=coupon_content_type)
        superadmin_group.permissions.add(*coupon_permissions)
        self.stdout.write("  🎫 Cupones de Descuento → Solo Superusuarios")
        
        # Permisos para Supplier (solo superusuarios)
        supplier_content_type = ContentType.objects.get_for_model(Supplier)
        supplier_permissions = Permission.objects.filter(content_type=supplier_content_type)
        superadmin_group.permissions.add(*supplier_permissions)
        self.stdout.write("  🏭 Proveedores → Solo Superusuarios")
        
        # Permisos para ProductSupplier (superusuarios y admin tienda)
        product_supplier_content_type = ContentType.objects.get_for_model(ProductSupplier)
        product_supplier_permissions = Permission.objects.filter(content_type=product_supplier_content_type)
        superadmin_group.permissions.add(*product_supplier_permissions)
        shop_admin_group.permissions.add(*product_supplier_permissions)
        self.stdout.write("  🔗 Relaciones Producto-Proveedor → Superusuarios y Admin Tienda")
        
        # Permisos para ProductStock (todos los grupos)
        stock_content_type = ContentType.objects.get_for_model(ProductStock)
        stock_permissions = Permission.objects.filter(content_type=stock_content_type)
        superadmin_group.permissions.add(*stock_permissions)
        shop_admin_group.permissions.add(*stock_permissions)
        stock_operator_group.permissions.add(*stock_permissions)
        self.stdout.write("  📦 Movimientos de Stock → Todos los grupos")
        
        # Permisos para CouponUsage (superusuarios y admin tienda)
        coupon_usage_content_type = ContentType.objects.get_for_model(CouponUsage)
        coupon_usage_permissions = Permission.objects.filter(content_type=coupon_usage_content_type)
        superadmin_group.permissions.add(*coupon_usage_permissions)
        shop_admin_group.permissions.add(*coupon_usage_permissions)
        self.stdout.write("  👥 Uso de Cupones → Superusuarios y Admin Tienda")
        
        # Permisos para Product (todos los grupos)
        product_content_type = ContentType.objects.get_for_model(Product)
        product_permissions = Permission.objects.filter(content_type=product_content_type)
        superadmin_group.permissions.add(*product_permissions)
        shop_admin_group.permissions.add(*product_permissions)
        # Solo permisos de lectura y cambio para operadores de stock
        stock_operator_group.permissions.add(
            *product_permissions.filter(codename__in=['view_product', 'change_product'])
        )
        self.stdout.write("  🛍️ Productos → Superusuarios (total), Admin Tienda (total), Operadores (lectura/edición)")
        
        # Permisos para Category (superusuarios y admin tienda)
        category_content_type = ContentType.objects.get_for_model(Category)
        category_permissions = Permission.objects.filter(content_type=category_content_type)
        superadmin_group.permissions.add(*category_permissions)
        shop_admin_group.permissions.add(*category_permissions)
        self.stdout.write("  📂 Categorías → Superusuarios y Admin Tienda")
        
        self.stdout.write("  ✅ Permisos configurados correctamente")
        
        # 3. Crear usuarios de ejemplo
        self.stdout.write("\n👤 Configurando usuarios...")
        
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
            self.stdout.write("  ✅ Superusuario 'admin' creado")
            self.stdout.write("     📧 Email: admin@dulcebias.cl")
            self.stdout.write("     🔑 Password: Admin123!@#")
        else:
            # Asegurar que el admin existente sea superusuario
            admin_user.is_superuser = True
            admin_user.is_staff = True
            admin_user.save()
            self.stdout.write("  ✅ Superusuario 'admin' verificado")
        
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
            self.stdout.write("  ✅ Admin de Tienda 'tienda_admin' creado")
            self.stdout.write("     📧 Email: tienda@dulcebias.cl")
            self.stdout.write("     🔑 Password: Tienda123!@#")
        
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
            self.stdout.write("  ✅ Operador de Stock 'stock_operator' creado")
            self.stdout.write("     📧 Email: stock@dulcebias.cl")
            self.stdout.write("     🔑 Password: Stock123!@#")
        
        stock_user.groups.add(stock_operator_group)
        
        # 4. Mostrar resumen de accesos
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("🎯 RESUMEN DE ACCESOS POR USUARIO")
        self.stdout.write("=" * 60)
        
        self.stdout.write("\n🔴 SUPERUSUARIO (admin):")
        self.stdout.write("  ✅ Acceso total a TODOS los módulos")
        self.stdout.write("  ✅ Configuraciones de Impuesto")
        self.stdout.write("  ✅ Cupones de Descuento")
        self.stdout.write("  ✅ Proveedores")
        self.stdout.write("  ✅ Relaciones Producto-Proveedor")
        self.stdout.write("  ✅ Movimientos de Stock")
        self.stdout.write("  ✅ Uso de Cupones")
        self.stdout.write("  ✅ Productos y Categorías")
        
        self.stdout.write("\n🟡 ADMINISTRADOR DE TIENDA (tienda_admin):")
        self.stdout.write("  ❌ Configuraciones de Impuesto")
        self.stdout.write("  ❌ Cupones de Descuento")
        self.stdout.write("  ❌ Proveedores")
        self.stdout.write("  ✅ Relaciones Producto-Proveedor")
        self.stdout.write("  ✅ Movimientos de Stock")
        self.stdout.write("  ✅ Uso de Cupones")
        self.stdout.write("  ✅ Productos y Categorías")
        
        self.stdout.write("\n🟢 OPERADOR DE STOCK (stock_operator):")
        self.stdout.write("  ❌ Configuraciones de Impuesto")
        self.stdout.write("  ❌ Cupones de Descuento")
        self.stdout.write("  ❌ Proveedores")
        self.stdout.write("  ❌ Relaciones Producto-Proveedor")
        self.stdout.write("  ✅ Movimientos de Stock")
        self.stdout.write("  ❌ Uso de Cupones")
        self.stdout.write("  🔍 Productos (solo lectura/edición)")
        self.stdout.write("  ❌ Categorías")
        
        self.stdout.write("\n🌐 URLs DE ACCESO:")
        self.stdout.write("  📍 Panel Principal: http://127.0.0.1:8000/admin/")
        self.stdout.write("  🔐 Login: http://127.0.0.1:8000/admin/login/")
        
        self.stdout.write(self.style.SUCCESS("\n🎉 ¡Configuración de permisos completada!"))
        self.stdout.write("   Los usuarios pueden acceder con sus credenciales respectivas.")
