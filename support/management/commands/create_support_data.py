from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random
from support.models import (
    SupportCategory, SupportTicket, SupportMessage, SupportFAQ, 
    AIConversationHistory, SupportKnowledgeBase, SupportNotification
)


class Command(BaseCommand):
    help = 'Crear datos de prueba para el sistema de soporte'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tickets',
            type=int,
            default=25,
            help='Número de tickets a crear (default: 25)'
        )
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Limpiar datos existentes antes de crear nuevos'
        )

    def handle(self, *args, **options):
        if options['clean']:
            self.stdout.write('Limpiando datos existentes...')
            SupportTicket.objects.all().delete()
            SupportMessage.objects.all().delete()
            SupportFAQ.objects.all().delete()
            SupportCategory.objects.all().delete()
            SupportKnowledgeBase.objects.all().delete()
            AIConversationHistory.objects.all().delete()
            SupportNotification.objects.all().delete()

        self.stdout.write('Creando datos de prueba...')
        
        # Crear categorías
        categories = self.create_categories()
        
        # Crear FAQs
        self.create_faqs(categories)
        
        # Crear knowledge base
        self.create_knowledge_base(categories)
        
        # Crear usuarios de prueba si no existen
        users = self.create_test_users()
        
        # Crear tickets
        tickets = self.create_tickets(categories, users, options['tickets'])
        
        # Crear mensajes para los tickets
        self.create_messages(tickets, users)
        
        # Crear conversaciones de IA
        self.create_ai_conversations(users)
        
        self.stdout.write(
            self.style.SUCCESS(f'¡Datos de prueba creados exitosamente!')
        )
        self.stdout.write(f'- {len(categories)} categorías')
        self.stdout.write(f'- {options["tickets"]} tickets')
        self.stdout.write(f'- {SupportFAQ.objects.count()} FAQs')
        self.stdout.write(f'- {SupportKnowledgeBase.objects.count()} artículos base de conocimiento')

    def create_categories(self):
        categories_data = [
            ('Problemas Técnicos', 'Errores del sitio web, problemas de login, etc.'),
            ('Pedidos y Envíos', 'Consultas sobre pedidos, estado de envío, etc.'),
            ('Productos', 'Información sobre productos, ingredientes, etc.'),
            ('Facturación', 'Problemas con pagos, facturas, etc.'),
            ('Cuenta de Usuario', 'Problemas con registro, perfil, etc.'),
            ('Sugerencias', 'Ideas para mejorar el servicio'),
            ('Quejas', 'Reclamos sobre productos o servicios'),
            ('Información General', 'Consultas generales sobre la empresa'),
        ]
        
        categories = []
        for name, description in categories_data:
            category, created = SupportCategory.objects.get_or_create(
                name=name,
                defaults={'description': description}
            )
            categories.append(category)
            if created:
                self.stdout.write(f'  Categoría creada: {name}')
        
        return categories

    def create_faqs(self, categories):
        faqs_data = [
            (
                '¿Cómo puedo rastrear mi pedido?',
                'Puedes rastrear tu pedido ingresando a tu cuenta y visitando la sección "Mis Pedidos". También recibirás un email con el número de seguimiento.',
                categories[1]  # Pedidos y Envíos
            ),
            (
                '¿Cuáles son los ingredientes de las galletas?',
                'Todas nuestras galletas contienen harina, azúcar, mantequilla y huevos. Para información específica sobre alérgenos, consulta la página de cada producto.',
                categories[2]  # Productos
            ),
            (
                '¿Puedo cambiar o cancelar mi pedido?',
                'Puedes cancelar tu pedido dentro de las primeras 2 horas después de realizarlo. Para cambios, contacta con nuestro servicio al cliente.',
                categories[1]  # Pedidos y Envíos
            ),
            (
                '¿Aceptan devoluciones?',
                'Aceptamos devoluciones dentro de los 7 días de la entrega si el producto llegó dañado o no es lo que ordenaste.',
                categories[1]  # Pedidos y Envíos
            ),
            (
                '¿Cómo puedo recuperar mi contraseña?',
                'Haz clic en "¿Olvidaste tu contraseña?" en la página de login y sigue las instrucciones que te enviaremos por email.',
                categories[4]  # Cuenta de Usuario
            ),
            (
                '¿Ofrecen productos sin gluten?',
                'Sí, tenemos una línea especial de galletas sin gluten. Puedes encontrarlas en la sección "Productos Especiales".',
                categories[2]  # Productos
            ),
        ]
        
        for question, answer, category in faqs_data:
            faq, created = SupportFAQ.objects.get_or_create(
                question=question,
                defaults={
                    'answer': answer,
                    'category': category,
                    'helpful_votes': random.randint(5, 50),
                    'not_helpful_votes': random.randint(0, 5)
                }
            )
            if created:
                self.stdout.write(f'  FAQ creada: {question[:50]}...')

    def create_knowledge_base(self, categories):
        kb_data = [
            (
                'Proceso de Horneado de Galletas',
                'Nuestro proceso de horneado tradicional garantiza la calidad y frescura de cada galleta...',
                categories[2],  # Productos
                'horneado, proceso, calidad, frescura'
            ),
            (
                'Política de Privacidad',
                'En Galletas Kati respetamos tu privacidad y protegemos tus datos personales...',
                categories[7],  # Información General
                'privacidad, datos, protección, GDPR'
            ),
            (
                'Términos y Condiciones',
                'Al utilizar nuestro sitio web, aceptas los siguientes términos y condiciones...',
                categories[7],  # Información General
                'términos, condiciones, legal, uso'
            ),
        ]
        
        for title, content, category, keywords in kb_data:
            kb, created = SupportKnowledgeBase.objects.get_or_create(
                title=title,
                defaults={
                    'content': content,
                    'category': category,
                    'keywords': keywords,
                    'times_used': random.randint(10, 100)
                }
            )
            if created:
                self.stdout.write(f'  KB creado: {title}')

    def create_test_users(self):
        users = []
        
        # Usuarios clientes
        customer_data = [
            ('maria.garcia', 'maria.garcia@email.com', 'María', 'García'),
            ('carlos.lopez', 'carlos.lopez@email.com', 'Carlos', 'López'),
            ('ana.martinez', 'ana.martinez@email.com', 'Ana', 'Martínez'),
            ('juan.rodriguez', 'juan.rodriguez@email.com', 'Juan', 'Rodríguez'),
            ('sofia.hernandez', 'sofia.hernandez@email.com', 'Sofía', 'Hernández'),
        ]
        
        for username, email, first_name, last_name in customer_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'is_active': True
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                self.stdout.write(f'  Usuario creado: {username}')
            users.append(user)
        
        # Usuarios staff
        staff_data = [
            ('soporte1', 'soporte1@galletaskati.com', 'Luis', 'Soporte'),
            ('soporte2', 'soporte2@galletaskati.com', 'Carmen', 'Atención'),
        ]
        
        for username, email, first_name, last_name in staff_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'is_staff': True,
                    'is_active': True
                }
            )
            if created:
                user.set_password('staff123')
                user.save()
                self.stdout.write(f'  Usuario staff creado: {username}')
            users.append(user)
        
        return users

    def create_tickets(self, categories, users, num_tickets):
        tickets = []
        customer_users = [u for u in users if not u.is_staff]
        staff_users = [u for u in users if u.is_staff]
        
        subjects_by_category = {
            'Problemas Técnicos': [
                'No puedo iniciar sesión en mi cuenta',
                'Error al procesar el pago',
                'La página se carga muy lenta',
                'Error 404 en el catálogo de productos',
                'Problemas con el carrito de compras'
            ],
            'Pedidos y Envíos': [
                'Consulta sobre el estado de mi pedido',
                'No he recibido mi pedido',
                'Quiero cambiar la dirección de envío',
                'Producto llegó dañado',
                'Falta un producto en mi pedido'
            ],
            'Productos': [
                'Información nutricional de galletas',
                'Disponibilidad de productos sin azúcar',
                '¿Tienen galletas veganas?',
                'Fechas de caducidad',
                'Consulta sobre ingredientes'
            ],
            'Facturación': [
                'Problema con el cobro en mi tarjeta',
                'Necesito una factura',
                'Cobro duplicado',
                'Consulta sobre promociones',
                'Código de descuento no funciona'
            ]
        }
        
        for i in range(num_tickets):
            category = random.choice(categories)
            user = random.choice(customer_users)
            
            # Obtener subject según categoría
            subjects = subjects_by_category.get(category.name, ['Consulta general'])
            subject = random.choice(subjects)
            
            # Determinar estado y prioridad
            status_choices = ['open', 'in_progress', 'resolved']
            priority_choices = ['low', 'normal', 'high', 'urgent']
            
            status = random.choice(status_choices)
            priority = random.choice(priority_choices)
            
            # Crear fecha aleatoria en los últimos 30 días
            days_ago = random.randint(0, 30)
            created_at = timezone.now() - timedelta(days=days_ago)
            
            ticket = SupportTicket.objects.create(
                user=user,
                category=category,
                subject=subject,
                description=f'Descripción detallada del problema: {subject.lower()}. Necesito ayuda urgente con este tema.',
                status=status,
                priority=priority,
                assigned_to=random.choice(staff_users) if random.random() > 0.3 else None,
                is_resolved=status == 'resolved',
                created_at=created_at,
                updated_at=created_at + timedelta(hours=random.randint(1, 48))
            )
            
            if status == 'resolved':
                ticket.resolved_at = ticket.updated_at
                ticket.rating = random.randint(3, 5)
                ticket.feedback = 'Gracias por la ayuda, problema resuelto satisfactoriamente.'
                ticket.save()
            
            tickets.append(ticket)
        
        self.stdout.write(f'  {len(tickets)} tickets creados')
        return tickets

    def create_messages(self, tickets, users):
        staff_users = [u for u in users if u.is_staff]
        
        for ticket in tickets:
            # Mensaje inicial del usuario
            SupportMessage.objects.create(
                ticket=ticket,
                sender=ticket.user,
                content=f'Necesito ayuda con: {ticket.subject}. {ticket.description}',
                message_type='user',
                created_at=ticket.created_at
            )
            
            # Algunas respuestas adicionales
            if random.random() > 0.4:  # 60% de probabilidad
                # Respuesta del staff
                staff_user = ticket.assigned_to or random.choice(staff_users)
                SupportMessage.objects.create(
                    ticket=ticket,
                    sender=staff_user,
                    content='Hola, gracias por contactarnos. Estamos revisando tu consulta y te responderemos pronto.',
                    message_type='human',
                    created_at=ticket.created_at + timedelta(hours=random.randint(1, 6))
                )
                
                # Posible mensaje adicional del usuario
                if random.random() > 0.6:  # 40% de probabilidad
                    SupportMessage.objects.create(
                        ticket=ticket,
                        sender=ticket.user,
                        content='Gracias por la respuesta. Espero su pronta solución.',
                        message_type='user',
                        created_at=ticket.created_at + timedelta(hours=random.randint(6, 12))
                    )

    def create_ai_conversations(self, users):
        customer_users = [u for u in users if not u.is_staff]
        
        conversations_data = [
            {
                'messages': [
                    {'user': '¿Cuáles son sus horarios de atención?'},
                    {'ai': 'Nuestros horarios de atención son de lunes a viernes de 9:00 a 18:00 y sábados de 9:00 a 14:00.'}
                ]
            },
            {
                'messages': [
                    {'user': '¿Hacen envíos a toda España?'},
                    {'ai': 'Sí, realizamos envíos a toda España. El tiempo de entrega es de 2-3 días laborables.'}
                ]
            },
            {
                'messages': [
                    {'user': '¿Tienen galletas sin azúcar?'},
                    {'ai': 'Sí, tenemos una línea completa de galletas sin azúcar endulzadas con stevia.'}
                ]
            }
        ]
        
        for _ in range(10):
            user = random.choice(customer_users)
            conv_data = random.choice(conversations_data)
            
            AIConversationHistory.objects.create(
                user=user,
                conversation_data=conv_data,
                total_messages=len(conv_data['messages']),
                total_tokens=random.randint(50, 200),
                was_helpful=random.choice([True, False, None]),
                created_at=timezone.now() - timedelta(days=random.randint(0, 15))
            )
