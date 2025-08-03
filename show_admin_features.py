#!/usr/bin/env python
"""
Script para demostrar las nuevas funcionalidades del panel de administración
"""
import os
import django
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dulce_bias_project.settings')
django.setup()

from shop.models import (
    TaxConfiguration, DiscountCoupon, CouponUsage, ProductStock, 
    Supplier, ProductSupplier, Product
)
from django.contrib.auth.models import User
from django.utils import timezone


def show_admin_features():
    """Mostrar las nuevas funcionalidades del panel de administración"""
    
    print("=" * 80)
    print("🎉 MÓDULO DE ADMINISTRACIÓN COMPLETO - GALLETAS KATI")
    print("=" * 80)
    
    # 1. Configuraciones de Impuesto
    print("\n📊 1. CONFIGURACIONES DE IMPUESTO")
    print("-" * 50)
    
    for tax in TaxConfiguration.objects.all():
        status = "✅ Activo" if tax.is_active else "❌ Inactivo"
        shipping = "📦 Aplica a envío" if tax.applies_to_shipping else "🚫 No aplica a envío"
        print(f"  {status} {tax.name}")
        print(f"    📈 Tasa: {tax.rate}%")
        print(f"    {shipping}")
        print(f"    📅 Creado: {tax.created_at.strftime('%d/%m/%Y')}")
        
        # Mostrar productos con esta configuración
        products_count = Product.objects.filter(tax_configuration=tax).count()
        print(f"    🛍️ Productos asociados: {products_count}")
        print()
    
    # 2. Cupones de Descuento
    print("🎫 2. CUPONES DE DESCUENTO")
    print("-" * 50)
    
    for coupon in DiscountCoupon.objects.all():
        status = "✅ Activo" if coupon.is_active else "❌ Inactivo"
        expired = "⏰ EXPIRADO" if coupon.is_expired else "✅ Vigente"
        
        print(f"  {status} Código: {coupon.code}")
        print(f"    📝 {coupon.name}")
        print(f"    💬 {coupon.description}")
        print(f"    🎯 Tipo: {coupon.get_discount_type_display()}")
        
        if coupon.discount_type == 'percentage':
            print(f"    💰 Descuento: {coupon.discount_value}%")
        elif coupon.discount_type == 'fixed_amount':
            print(f"    💰 Descuento: ${int(coupon.discount_value):,}")
        else:
            print(f"    🚚 Envío gratuito")
        
        print(f"    🛒 Monto mínimo: ${int(coupon.minimum_order_amount):,}")
        
        if coupon.max_uses:
            uses = coupon.get_usage_count()
            remaining = coupon.max_uses - uses
            print(f"    📊 Usos: {uses}/{coupon.max_uses} (Quedan: {remaining})")
        else:
            print(f"    ♾️ Usos ilimitados")
        
        print(f"    📅 Válido: {coupon.valid_from.strftime('%d/%m/%Y')} - {coupon.valid_until.strftime('%d/%m/%Y')}")
        print(f"    ⏱️ Estado: {expired}")
        print(f"    👤 Creado por: {coupon.created_by.username}")
        print()
    
    # 3. Proveedores
    print("🏭 3. PROVEEDORES")
    print("-" * 50)
    
    for supplier in Supplier.objects.all():
        status = "✅ Activo" if supplier.is_active else "❌ Inactivo"
        rating_stars = "⭐" * int(supplier.rating) if supplier.rating else "Sin calificación"
        
        print(f"  {status} {supplier.name}")
        print(f"    👤 Contacto: {supplier.contact_person}")
        print(f"    📧 Email: {supplier.email}")
        print(f"    📞 Teléfono: {supplier.phone}")
        print(f"    📍 Dirección: {supplier.address}, {supplier.city}")
        print(f"    🆔 RUT: {supplier.tax_id}")
        print(f"    ⭐ Calificación: {supplier.rating}/5 {rating_stars}")
        
        # Productos que suministra
        products_count = ProductSupplier.objects.filter(supplier=supplier).count()
        print(f"    📦 Productos que suministra: {products_count}")
        
        if supplier.notes:
            print(f"    📝 Notas: {supplier.notes}")
        print()
    
    # 4. Relaciones Producto-Proveedor
    print("🔗 4. RELACIONES PRODUCTO-PROVEEDOR")
    print("-" * 50)
    
    for relation in ProductSupplier.objects.select_related('product', 'supplier'):
        primary = "⭐ PRINCIPAL" if relation.is_primary else "🔗 Secundario"
        
        print(f"  {primary} {relation.product.name}")
        print(f"    🏭 Proveedor: {relation.supplier.name}")
        print(f"    🆔 SKU Proveedor: {relation.supplier_sku}")
        print(f"    💵 Precio de costo: ${int(relation.cost_price):,}")
        print(f"    💰 Precio de venta: ${int(relation.product.price):,}")
        print(f"    📈 Margen: {relation.formatted_profit_margin}")
        print(f"    📦 Cantidad mínima: {relation.minimum_order_quantity}")
        print(f"    ⏱️ Tiempo de entrega: {relation.lead_time_days} días")
        print()
    
    # 5. Estadísticas del Sistema
    print("📊 5. ESTADÍSTICAS DEL SISTEMA")
    print("-" * 50)
    
    total_products = Product.objects.count()
    active_products = Product.objects.filter(available=True).count()
    products_with_tax = Product.objects.exclude(tax_configuration=None).count()
    
    total_coupons = DiscountCoupon.objects.count()
    active_coupons = DiscountCoupon.objects.filter(is_active=True).count()
    expired_coupons = sum(1 for c in DiscountCoupon.objects.all() if c.is_expired)
    
    total_suppliers = Supplier.objects.count()
    active_suppliers = Supplier.objects.filter(is_active=True).count()
    
    total_relations = ProductSupplier.objects.count()
    primary_relations = ProductSupplier.objects.filter(is_primary=True).count()
    
    print(f"🛍️  PRODUCTOS:")
    print(f"    • Total: {total_products}")
    print(f"    • Activos: {active_products}")
    print(f"    • Con IVA configurado: {products_with_tax}")
    print()
    
    print(f"🎫  CUPONES:")
    print(f"    • Total: {total_coupons}")
    print(f"    • Activos: {active_coupons}")
    print(f"    • Expirados: {expired_coupons}")
    print()
    
    print(f"🏭  PROVEEDORES:")
    print(f"    • Total: {total_suppliers}")
    print(f"    • Activos: {active_suppliers}")
    print()
    
    print(f"🔗  RELACIONES:")
    print(f"    • Total: {total_relations}")
    print(f"    • Principales: {primary_relations}")
    print()
    
    # 6. Funcionalidades del Panel de Administración
    print("⚙️ 6. FUNCIONALIDADES DISPONIBLES EN EL ADMIN")
    print("-" * 50)
    
    features = [
        "🏷️ Gestión de Configuraciones de Impuesto (IVA/Sin IVA)",
        "🎫 Creación y gestión de cupones de descuento",
        "👥 Seguimiento de uso de cupones por cliente",
        "📦 Control de movimientos de stock (entradas/salidas)",
        "🏭 Gestión completa de proveedores",
        "🔗 Relaciones producto-proveedor con costos y márgenes",
        "💰 Cálculo automático de precios con/sin impuestos",
        "📊 Filtros avanzados por categoría, estado, stock",
        "🔍 Búsqueda por nombre, descripción, SKU",
        "📈 Estadísticas y métricas en tiempo real",
        "✏️ Edición en línea de precios y stock",
        "📋 Acciones masivas (actualización de precios)",
        "🖼️ Vista previa de imágenes en lista",
        "📱 Interfaz responsiva y fácil de usar"
    ]
    
    for feature in features:
        print(f"  {feature}")
    
    print("\n" + "=" * 80)
    print("🎯 INSTRUCCIONES DE USO")
    print("=" * 80)
    
    instructions = [
        "1. 🌐 Accede al panel de administración en: http://127.0.0.1:8000/admin/",
        "2. 🔐 Inicia sesión con tu usuario administrador",
        "3. 📂 Navega a la sección 'SHOP' para ver todos los módulos",
        "4. ⚙️ Configura primero los impuestos en 'Configuraciones de impuesto'",
        "5. 🏭 Registra tus proveedores en 'Proveedores'",
        "6. 🔗 Asocia productos con proveedores en 'Relaciones producto-proveedor'",
        "7. 🎫 Crea cupones de descuento para promociones",
        "8. 📦 Usa 'Movimientos de stock' para registrar entradas y salidas",
        "9. 💰 Los precios se calculan automáticamente con IVA",
        "10. 📊 Revisa las estadísticas en cada sección del admin"
    ]
    
    for instruction in instructions:
        print(f"  {instruction}")
    
    print("\n🎉 ¡El módulo de administración está listo para usar!")
    print("   Todas las funcionalidades están operativas y con datos de ejemplo.")


if __name__ == "__main__":
    show_admin_features()
