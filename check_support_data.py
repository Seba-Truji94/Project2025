#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dulce_bias_project.settings')
django.setup()

from django.contrib.auth.models import User
from support.models import SupportTicket, SupportMessage, SupportNotification, SupportCategory

print("=== ESTADO ACTUAL DEL SISTEMA DE SOPORTE ===\n")

print("👥 USUARIOS EN EL SISTEMA:")
users = User.objects.all()
if users:
    for user in users:
        role = "Superusuario" if user.is_superuser else "Staff" if user.is_staff else "Cliente"
        print(f"- {user.username} ({user.email or 'Sin email'}) - {role}")
else:
    print("- No hay usuarios registrados")

print(f"\n📊 ESTADÍSTICAS DEL SOPORTE:")
print(f"- Tickets totales: {SupportTicket.objects.count()}")
print(f"- Mensajes totales: {SupportMessage.objects.count()}")
print(f"- Notificaciones: {SupportNotification.objects.count()}")
print(f"- Categorías: {SupportCategory.objects.count()}")

print(f"\n🎫 TICKETS POR ESTADO:")
for status, label in SupportTicket.STATUS_CHOICES:
    count = SupportTicket.objects.filter(status=status).count()
    print(f"- {label}: {count}")

print(f"\n🔥 TICKETS POR PRIORIDAD:")
for priority, label in SupportTicket.PRIORITY_CHOICES:
    count = SupportTicket.objects.filter(priority=priority).count()
    print(f"- {label}: {count}")

print(f"\n📂 TICKETS POR CATEGORÍA:")
categories = SupportCategory.objects.annotate(
    ticket_count=django.db.models.Count('supportticket')
)
for category in categories:
    print(f"- {category.name}: {category.ticket_count}")

print(f"\n🆕 ÚLTIMOS 5 TICKETS:")
recent_tickets = SupportTicket.objects.order_by('-created_at')[:5]
for ticket in recent_tickets:
    print(f"- #{ticket.ticket_number} - {ticket.subject[:50]}... ({ticket.get_status_display()})")

if SupportTicket.objects.count() == 0:
    print("\n⚠️  NO HAY TICKETS REALES EN EL SISTEMA")
    print("💡 Para empezar con datos reales:")
    print("1. Crea un superusuario: python manage.py createsuperuser")
    print("2. Accede al admin: /admin/")
    print("3. Crea categorías y tickets reales")
    print("4. O usa el sistema de soporte desde /support/")
