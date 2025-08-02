#!/usr/bin/env python
"""
Script para verificar el estado del sistema de soporte con datos reales
"""
import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dulce_bias_project.settings')
django.setup()

from django.contrib.auth.models import User
from support.models import SupportTicket, SupportCategory, SupportMessage, SupportNotification

def main():
    print("🔍 VERIFICACIÓN DEL SISTEMA DE SOPORTE - DATOS REALES")
    print("=" * 60)
    
    # Verificar usuarios
    print("\n👥 USUARIOS DEL SISTEMA:")
    users = User.objects.all()
    superusers = users.filter(is_superuser=True)
    regular_users = users.filter(is_superuser=False)
    
    print(f"   • Total usuarios: {users.count()}")
    print(f"   • Superusuarios: {superusers.count()}")
    print(f"   • Usuarios regulares: {regular_users.count()}")
    
    if superusers.exists():
        print("   • Superusuarios disponibles:")
        for user in superusers:
            print(f"     - {user.username} ({user.email})")
    
    # Verificar categorías
    print("\n📁 CATEGORÍAS DE SOPORTE:")
    categories = SupportCategory.objects.filter(is_active=True)
    print(f"   • Categorías activas: {categories.count()}")
    
    if categories.exists():
        for cat in categories:
            print(f"     - {cat.name}: {cat.description}")
    
    # Verificar tickets
    print("\n🎫 TICKETS DE SOPORTE:")
    tickets = SupportTicket.objects.all()
    print(f"   • Total tickets: {tickets.count()}")
    
    if tickets.count() == 0:
        print("   ✅ Sistema limpio - No hay datos de prueba")
        print("   📝 Listo para recibir tickets reales de usuarios")
    else:
        print(f"   • Tickets por estado:")
        from django.db.models import Count
        status_counts = tickets.values('status').annotate(count=Count('status'))
        for item in status_counts:
            print(f"     - {item['status']}: {item['count']}")
    
    # Verificar mensajes
    print("\n💬 MENSAJES:")
    messages = SupportMessage.objects.all()
    print(f"   • Total mensajes: {messages.count()}")
    
    # Verificar notificaciones
    print("\n🔔 NOTIFICACIONES:")
    notifications = SupportNotification.objects.all()
    print(f"   • Total notificaciones: {notifications.count()}")
    
    print("\n" + "=" * 60)
    print("✅ ESTADO DEL SISTEMA:")
    
    if tickets.count() == 0:
        print("🎯 Sistema configurado correctamente para datos REALES")
        print("📋 Acciones disponibles:")
        print("   1. Los usuarios pueden crear tickets desde la interfaz web")
        print("   2. Los superusuarios pueden gestionar tickets desde /admin/")
        print("   3. El sistema enviará notificaciones automáticas")
        print("   4. Se mantiene historial completo de conversaciones")
        
        print("\n🔗 URLs importantes:")
        print("   • Admin: http://localhost:8000/admin/")
        print("   • Soporte: http://localhost:8000/support/")
        print("   • Crear ticket: http://localhost:8000/support/create/")
    else:
        print("📊 Sistema en funcionamiento con datos reales")
        print(f"   • {tickets.count()} tickets en el sistema")
        print(f"   • {messages.count()} mensajes intercambiados")
        print(f"   • {notifications.count()} notificaciones enviadas")

if __name__ == "__main__":
    main()
