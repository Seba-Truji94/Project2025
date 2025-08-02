#!/usr/bin/env python
"""
Script de auditoría de seguridad para Galletas Kati
Ejecuta verificaciones de seguridad y genera reportes
"""
import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dulce_bias_project.settings')
django.setup()

from security.utils import SecurityAudit
from django.contrib.auth.models import User
from datetime import datetime
import json


def run_security_audit():
    """Ejecutar auditoría completa de seguridad"""
    print("🔒 Iniciando auditoría de seguridad de Galletas Kati...")
    print("=" * 60)
    
    # Generar reporte
    report = SecurityAudit.generate_security_report()
    
    # Mostrar resultados
    print(f"📅 Auditoría ejecutada el: {report['timestamp']}")
    print()
    
    # Contraseñas débiles
    weak_passwords = report['weak_passwords']
    print(f"🔑 Contraseñas débiles encontradas: {len(weak_passwords)}")
    if weak_passwords:
        for user in weak_passwords:
            print(f"   ⚠️  {user.username} ({user.email})")
    else:
        print("   ✅ No se encontraron contraseñas débiles")
    print()
    
    # Superusuarios inactivos
    inactive_superusers = report['inactive_superusers']
    print(f"👑 Superusuarios inactivos: {len(inactive_superusers)}")
    if inactive_superusers:
        for user in inactive_superusers:
            print(f"   ⚠️  {user.username} - Último login: {user.last_login}")
    else:
        print("   ✅ Todos los superusuarios están activos")
    print()
    
    # Emails duplicados
    duplicate_emails = report['duplicate_emails']
    print(f"📧 Emails duplicados: {len(duplicate_emails)}")
    if duplicate_emails:
        for email_data in duplicate_emails:
            print(f"   ⚠️  {email_data['email']} ({email_data['count']} usuarios)")
    else:
        print("   ✅ No hay emails duplicados")
    print()
    
    # Estadísticas generales
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    superusers = User.objects.filter(is_superuser=True).count()
    
    print("📊 Estadísticas generales:")
    print(f"   👥 Total de usuarios: {total_users}")
    print(f"   ✅ Usuarios activos: {active_users}")
    print(f"   👑 Superusuarios: {superusers}")
    print()
    
    # Guardar reporte en archivo
    report_filename = f"security_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_path = os.path.join('logs', report_filename)
    
    # Convertir objetos Django a diccionarios para JSON
    json_report = {
        'timestamp': report['timestamp'].isoformat(),
        'weak_passwords': [
            {'username': u.username, 'email': u.email} 
            for u in weak_passwords
        ],
        'inactive_superusers': [
            {
                'username': u.username, 
                'last_login': u.last_login.isoformat() if u.last_login else None
            } 
            for u in inactive_superusers
        ],
        'duplicate_emails': list(duplicate_emails),
        'statistics': {
            'total_users': total_users,
            'active_users': active_users,
            'superusers': superusers
        }
    }
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(json_report, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Reporte guardado en: {report_path}")
    print()
    
    # Recomendaciones
    print("🛡️  RECOMENDACIONES DE SEGURIDAD:")
    print("-" * 40)
    
    if weak_passwords:
        print("1. ⚠️  Solicitar cambio de contraseña a usuarios con contraseñas débiles")
    
    if inactive_superusers:
        print("2. ⚠️  Revisar y desactivar superusuarios inactivos")
    
    if duplicate_emails:
        print("3. ⚠️  Resolver duplicación de emails")
    
    print("4. ✅ Revisar logs de seguridad regularmente")
    print("5. ✅ Mantener Django y dependencias actualizadas")
    print("6. ✅ Configurar HTTPS en producción")
    print("7. ✅ Implementar backups automáticos")
    
    print()
    print("🔒 Auditoría completada")


if __name__ == "__main__":
    run_security_audit()
