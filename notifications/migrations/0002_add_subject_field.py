# Generated manually to fix subject field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0001_initial'),
    ]

    operations = [
        # Añadir el campo subject que falta en NotificationTemplate
        migrations.AddField(
            model_name='notificationtemplate',
            name='subject',
            field=models.CharField(max_length=200, verbose_name="Asunto", blank=True, default=''),
        ),
        
        # Renombrar subject_template a content para consistencia
        migrations.RenameField(
            model_name='notificationtemplate',
            old_name='body_template',
            new_name='content',
        ),
        
        # Añadir campos faltantes en Notification
        migrations.AddField(
            model_name='notification',
            name='subject',
            field=models.CharField(max_length=200, verbose_name="Asunto", default=''),
        ),
    ]
