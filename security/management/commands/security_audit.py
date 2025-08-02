"""
Comando de gestión para auditorías de seguridad
"""
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from security.utils import SecurityAudit
from datetime import datetime
import json


class Command(BaseCommand):
    help = 'Ejecuta auditoría de seguridad del sistema'

    def add_arguments(self, parser):
        parser.add_argument(
            '--export',
            action='store_true',
            help='Exportar reporte a archivo JSON',
        )
        parser.add_argument(
            '--fix-duplicates',
            action='store_true',
            help='Intentar corregir emails duplicados automáticamente',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Mostrar información detallada',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.HTTP_INFO('🔒 Iniciando auditoría de seguridad...')
        )

        # Ejecutar auditoría
        report = SecurityAudit.generate_security_report()

        # Mostrar resultados
        self.show_results(report, options['verbose'])

        # Exportar si se solicita
        if options['export']:
            self.export_report(report)

        # Corregir duplicados si se solicita
        if options['fix_duplicates']:
            self.fix_duplicate_emails(report['duplicate_emails'])

        self.stdout.write(
            self.style.SUCCESS('✅ Auditoría completada')
        )

    def show_results(self, report, verbose=False):
        """Mostrar resultados de la auditoría"""
        
        # Contraseñas débiles
        weak_count = len(report['weak_passwords'])
        if weak_count > 0:
            self.stdout.write(
                self.style.WARNING(f'⚠️  Contraseñas débiles: {weak_count}')
            )
            if verbose:
                for user in report['weak_passwords']:
                    self.stdout.write(f'   - {user.username} ({user.email})')
        else:
            self.stdout.write(
                self.style.SUCCESS('✅ No se encontraron contraseñas débiles')
            )

        # Superusuarios inactivos
        inactive_count = len(report['inactive_superusers'])
        if inactive_count > 0:
            self.stdout.write(
                self.style.WARNING(f'⚠️  Superusuarios inactivos: {inactive_count}')
            )
            if verbose:
                for user in report['inactive_superusers']:
                    last_login = user.last_login.strftime('%Y-%m-%d') if user.last_login else 'Nunca'
                    self.stdout.write(f'   - {user.username} (Último login: {last_login})')
        else:
            self.stdout.write(
                self.style.SUCCESS('✅ Todos los superusuarios están activos')
            )

        # Emails duplicados
        duplicate_count = len(report['duplicate_emails'])
        if duplicate_count > 0:
            self.stdout.write(
                self.style.WARNING(f'⚠️  Emails duplicados: {duplicate_count}')
            )
            if verbose:
                for email_data in report['duplicate_emails']:
                    self.stdout.write(f'   - {email_data["email"]} ({email_data["count"]} usuarios)')
        else:
            self.stdout.write(
                self.style.SUCCESS('✅ No hay emails duplicados')
            )

        # Estadísticas generales
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        superusers = User.objects.filter(is_superuser=True).count()

        self.stdout.write('\n📊 Estadísticas:')
        self.stdout.write(f'   Total usuarios: {total_users}')
        self.stdout.write(f'   Usuarios activos: {active_users}')
        self.stdout.write(f'   Superusuarios: {superusers}')

    def export_report(self, report):
        """Exportar reporte a archivo JSON"""
        filename = f'security_audit_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        filepath = f'logs/{filename}'

        # Convertir para JSON
        json_report = {
            'timestamp': report['timestamp'].isoformat(),
            'weak_passwords': [
                {'username': u.username, 'email': u.email} 
                for u in report['weak_passwords']
            ],
            'inactive_superusers': [
                {
                    'username': u.username, 
                    'last_login': u.last_login.isoformat() if u.last_login else None
                } 
                for u in report['inactive_superusers']
            ],
            'duplicate_emails': list(report['duplicate_emails']),
            'statistics': {
                'total_users': User.objects.count(),
                'active_users': User.objects.filter(is_active=True).count(),
                'superusers': User.objects.filter(is_superuser=True).count()
            }
        }

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(json_report, f, indent=2, ensure_ascii=False)
            
            self.stdout.write(
                self.style.SUCCESS(f'📄 Reporte exportado: {filepath}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error al exportar: {e}')
            )

    def fix_duplicate_emails(self, duplicates):
        """Intentar corregir emails duplicados"""
        if not duplicates:
            return

        self.stdout.write('🔧 Intentando corregir emails duplicados...')
        
        for email_data in duplicates:
            email = email_data['email']
            users_with_email = User.objects.filter(email=email)
            
            if users_with_email.count() > 1:
                # Mantener el usuario más reciente, limpiar los otros
                latest_user = users_with_email.order_by('-date_joined').first()
                older_users = users_with_email.exclude(id=latest_user.id)
                
                for user in older_users:
                    # Limpiar email de usuarios más antiguos
                    user.email = f"{user.username}@duplicate-removed.local"
                    user.save()
                    
                    self.stdout.write(
                        f'   📧 Email duplicado removido de {user.username}'
                    )

        self.stdout.write(
            self.style.SUCCESS('✅ Corrección de emails duplicados completada')
        )
