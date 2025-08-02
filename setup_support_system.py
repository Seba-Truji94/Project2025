#!/usr/bin/env python
"""
Script para configurar categorías de soporte y FAQs iniciales
"""

import os
import sys
import django

# Configurar Django
if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dulce_bias_project.settings')
    django.setup()

    from support.models import SupportCategory, SupportFAQ

    # Crear categorías de soporte
    categories_data = [
        {
            'name': 'Problemas de Pedidos',
            'description': 'Consultas sobre el estado, modificación o cancelación de pedidos',
            'icon': 'fas fa-shopping-cart',
            'order': 1
        },
        {
            'name': 'Problemas de Pago',
            'description': 'Inconvenientes con transferencias, pagos y facturación',
            'icon': 'fas fa-credit-card',
            'order': 2
        },
        {
            'name': 'Problemas de Envío',
            'description': 'Consultas sobre delivery, tiempos de entrega y seguimiento',
            'icon': 'fas fa-truck',
            'order': 3
        },
        {
            'name': 'Problemas Técnicos',
            'description': 'Errores en la página web, aplicación o plataforma',
            'icon': 'fas fa-bug',
            'order': 4
        },
        {
            'name': 'Consultas Generales',
            'description': 'Preguntas sobre productos, ingredientes y información general',
            'icon': 'fas fa-question-circle',
            'order': 5
        },
        {
            'name': 'Devoluciones y Reembolsos',
            'description': 'Solicitudes de devolución, cambios y reembolsos',
            'icon': 'fas fa-undo',
            'order': 6
        }
    ]

    print("🍪 Configurando categorías de soporte...")
    
    for cat_data in categories_data:
        category, created = SupportCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults=cat_data
        )
        if created:
            print(f"✅ Categoría creada: {category.name}")
        else:
            print(f"📋 Categoría ya existe: {category.name}")

    # Crear FAQs iniciales
    faqs_data = [
        {
            'question': '¿Cuánto tiempo tarda en llegar mi pedido?',
            'answer': 'Los pedidos dentro de Santiago se entregan entre 24-48 horas hábiles. Para regiones, el tiempo de entrega es de 3-5 días hábiles. Recibirás un correo con el código de seguimiento una vez que tu pedido sea despachado.',
            'category_name': 'Problemas de Envío',
            'keywords': 'tiempo entrega, delivery, envío, Santiago, regiones, días hábiles'
        },
        {
            'question': '¿Qué métodos de pago aceptan?',
            'answer': 'Aceptamos transferencia bancaria, tarjetas de crédito y débito (Visa, Mastercard), y pago contra entrega en Santiago. Para transferencias, los datos bancarios se proporcionan al finalizar la compra.',
            'category_name': 'Problemas de Pago',
            'keywords': 'pago, transferencia, tarjeta, crédito, débito, contra entrega'
        },
        {
            'question': '¿Puedo cancelar o modificar mi pedido?',
            'answer': 'Puedes cancelar o modificar tu pedido hasta 2 horas después de realizado, siempre que no haya sido preparado. Para cambios, contacta nuestro soporte inmediatamente con tu número de pedido.',
            'category_name': 'Problemas de Pedidos',
            'keywords': 'cancelar, modificar, cambiar pedido, 2 horas, número pedido'
        },
        {
            'question': '¿Las galletas contienen alérgenos?',
            'answer': 'Nuestras galletas pueden contener gluten, frutos secos, lácteos y huevos. Cada producto indica claramente sus ingredientes. Si tienes alergias específicas, revisa la descripción del producto o contáctanos.',
            'category_name': 'Consultas Generales',
            'keywords': 'alérgenos, gluten, frutos secos, lácteos, huevos, ingredientes, alergias'
        },
        {
            'question': '¿Cómo solicito una devolución?',
            'answer': 'Para devoluciones, contacta nuestro soporte dentro de 24 horas de recibido el pedido. Las galletas deben estar en perfecto estado y empaque original. Procesamos reembolsos en 3-5 días hábiles.',
            'category_name': 'Devoluciones y Reembolsos',
            'keywords': 'devolución, reembolso, 24 horas, perfecto estado, empaque original'
        },
        {
            'question': '¿Por qué no puedo agregar productos al carrito?',
            'answer': 'Este problema puede deberse a cookies deshabilitadas o conexión intermitente. Intenta refrescar la página, limpiar cache del navegador, o usar modo incógnito. Si persiste, contacta soporte técnico.',
            'category_name': 'Problemas Técnicos',
            'keywords': 'carrito, agregar productos, cookies, cache, navegador, incógnito, soporte técnico'
        },
        {
            'question': '¿Ofrecen envío gratis?',
            'answer': 'Sí! Ofrecemos envío gratis en compras superiores a $15.000 dentro de Santiago y V Región. Para otros destinos, consulta nuestras tarifas de envío al momento de finalizar la compra.',
            'category_name': 'Problemas de Envío',
            'keywords': 'envío gratis, $15.000, Santiago, V Región, tarifas envío'
        },
        {
            'question': '¿Cómo verifico el estado de mi transferencia?',
            'answer': 'Una vez realizada la transferencia, sube el comprobante en "Mis Pedidos". Nuestro equipo verificará el pago en 2-4 horas hábiles y recibirás confirmación por correo.',
            'category_name': 'Problemas de Pago',
            'keywords': 'verificar transferencia, comprobante, mis pedidos, 2-4 horas, confirmación correo'
        }
    ]

    print("\n🍪 Configurando FAQs iniciales...")
    
    for faq_data in faqs_data:
        try:
            category = SupportCategory.objects.get(name=faq_data['category_name'])
            faq, created = SupportFAQ.objects.get_or_create(
                question=faq_data['question'],
                defaults={
                    'answer': faq_data['answer'],
                    'category': category,
                    'keywords': faq_data['keywords'],
                    'is_featured': True,
                }
            )
            if created:
                print(f"✅ FAQ creada: {faq.question[:60]}...")
            else:
                print(f"📋 FAQ ya existe: {faq.question[:60]}...")
        except SupportCategory.DoesNotExist:
            print(f"❌ Error: Categoría no encontrada para FAQ: {faq_data['question'][:60]}...")

    print(f"\n🎉 ¡Configuración del sistema de soporte completada!")
    print(f"📊 Categorías totales: {SupportCategory.objects.count()}")
    print(f"❓ FAQs totales: {SupportFAQ.objects.count()}")
    print(f"\n🌐 Accede al centro de soporte en: http://localhost:8000/support/")
