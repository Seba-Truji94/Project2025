# Celery configuration for Galletas Kati Notifications
# Create this file as: galletas_kati/celery.py

import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'galletas_kati.settings')

app = Celery('galletas_kati')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Celery beat schedule for periodic tasks
app.conf.beat_schedule = {
    'process-pending-notifications': {
        'task': 'notifications.tasks.process_pending_notifications',
        'schedule': 60.0,  # Run every minute
    },
    'cleanup-old-logs': {
        'task': 'notifications.tasks.cleanup_old_notification_logs',
        'schedule': 86400.0,  # Run daily
    },
    'send-digest-notifications': {
        'task': 'notifications.tasks.send_digest_notifications',
        'schedule': 3600.0,  # Run hourly
    },
}

app.conf.timezone = 'America/Santiago'

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
