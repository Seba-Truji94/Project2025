# Generated manually for notifications

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('notification_type', models.CharField(choices=[('general', 'General'), ('order_confirmation', 'Confirmación de Pedido'), ('order_update', 'Actualización de Pedido'), ('promotion', 'Promoción'), ('reminder', 'Recordatorio'), ('support_ticket', 'Ticket de Soporte'), ('welcome', 'Bienvenida'), ('password_reset', 'Recuperación de Contraseña')], max_length=50)),
                ('channel', models.CharField(choices=[('email', 'Email'), ('sms', 'SMS'), ('whatsapp', 'WhatsApp'), ('push', 'Push Notification')], max_length=20)),
                ('recipient_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('recipient_phone', models.CharField(blank=True, max_length=20, null=True)),
                ('title', models.CharField(blank=True, max_length=200, null=True)),
                ('message', models.TextField()),
                ('status', models.CharField(choices=[('pending', 'Pendiente'), ('sent', 'Enviado'), ('delivered', 'Entregado'), ('failed', 'Fallido')], default='pending', max_length=20)),
                ('scheduled_at', models.DateTimeField(blank=True, null=True)),
                ('sent_at', models.DateTimeField(blank=True, null=True)),
                ('read_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('extra_data', models.JSONField(blank=True, default=dict)),
                ('external_id', models.CharField(blank=True, max_length=100, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Notificación',
                'verbose_name_plural': 'Notificaciones',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='NotificationTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('notification_type', models.CharField(choices=[('general', 'General'), ('order_confirmation', 'Confirmación de Pedido'), ('order_update', 'Actualización de Pedido'), ('promotion', 'Promoción'), ('reminder', 'Recordatorio'), ('support_ticket', 'Ticket de Soporte'), ('welcome', 'Bienvenida'), ('password_reset', 'Recuperación de Contraseña')], max_length=50)),
                ('channel', models.CharField(choices=[('email', 'Email'), ('sms', 'SMS'), ('whatsapp', 'WhatsApp'), ('push', 'Push Notification')], max_length=20)),
                ('subject_template', models.CharField(blank=True, max_length=200, null=True)),
                ('body_template', models.TextField()),
                ('html_template', models.TextField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Plantilla de Notificación',
                'verbose_name_plural': 'Plantillas de Notificación',
            },
        ),
        migrations.CreateModel(
            name='UserNotificationPreference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_enabled', models.BooleanField(default=True)),
                ('sms_enabled', models.BooleanField(default=False)),
                ('whatsapp_enabled', models.BooleanField(default=False)),
                ('push_enabled', models.BooleanField(default=True)),
                ('notification_types', models.JSONField(default=dict)),
                ('quiet_hours_start', models.TimeField(blank=True, null=True)),
                ('quiet_hours_end', models.TimeField(blank=True, null=True)),
                ('timezone', models.CharField(default='America/Santiago', max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='notification_preferences', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Preferencia de Notificación',
                'verbose_name_plural': 'Preferencias de Notificación',
            },
        ),
        migrations.CreateModel(
            name='NotificationQueue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('priority', models.IntegerField(default=5)),
                ('retry_count', models.IntegerField(default=0)),
                ('max_retries', models.IntegerField(default=3)),
                ('scheduled_for', models.DateTimeField()),
                ('last_error', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('notification', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='queue_item', to='notifications.notification')),
            ],
            options={
                'verbose_name': 'Cola de Notificación',
                'verbose_name_plural': 'Cola de Notificaciones',
                'ordering': ['priority', 'scheduled_for'],
            },
        ),
        migrations.CreateModel(
            name='NotificationLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('sent', 'Enviado'), ('delivered', 'Entregado'), ('opened', 'Abierto'), ('clicked', 'Clicado'), ('failed', 'Fallido'), ('bounced', 'Rebotado')], max_length=20)),
                ('details', models.JSONField(blank=True, default=dict)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('notification', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='logs', to='notifications.notification')),
            ],
            options={
                'verbose_name': 'Log de Notificación',
                'verbose_name_plural': 'Logs de Notificación',
                'ordering': ['-timestamp'],
            },
        ),
    ]
