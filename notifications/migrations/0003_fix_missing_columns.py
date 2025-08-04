# Generated manually to fix missing columns

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            "ALTER TABLE notifications_notificationtemplate ADD COLUMN IF NOT EXISTS subject VARCHAR(200) DEFAULT '';",
            reverse_sql="ALTER TABLE notifications_notificationtemplate DROP COLUMN subject;"
        ),
        migrations.RunSQL(
            "ALTER TABLE notifications_notificationtemplate ADD COLUMN IF NOT EXISTS template_body TEXT DEFAULT '';",
            reverse_sql="ALTER TABLE notifications_notificationtemplate DROP COLUMN template_body;"
        ),
    ]
