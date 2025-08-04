# Configuration for Notifications System
# Add this to your main settings.py

# ===== NOTIFICATIONS CONFIGURATION =====

# Add 'notifications' to INSTALLED_APPS
# INSTALLED_APPS = [
#     ...
#     'notifications',
#     ...
# ]

# Email Configuration (if not already configured)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # Change to your SMTP server
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'  # Change to your email
EMAIL_HOST_PASSWORD = 'your-app-password'  # Use app password for Gmail
DEFAULT_FROM_EMAIL = 'Galletas Kati <noreply@galletaskati.cl>'

# Notification Settings
NOTIFICATION_SETTINGS = {
    'DEFAULT_CHANNELS': ['email'],  # Default channels for new users
    'EMAIL_TEMPLATES': {
        'order_confirmation': 'notifications/email/order_confirmation.html',
        'general': 'notifications/email/general.html',
        'support_ticket': 'notifications/email/support_ticket.html',
    },
    'SMS_PROVIDER': 'twilio',  # or 'local_api'
    'WHATSAPP_PROVIDER': 'twilio',  # or 'business_api'
    'MAX_RETRIES': 3,
    'RETRY_DELAY': 60,  # seconds
}

# Twilio Configuration (for SMS and WhatsApp)
TWILIO_ACCOUNT_SID = 'your_twilio_account_sid'
TWILIO_AUTH_TOKEN = 'your_twilio_auth_token'
TWILIO_PHONE_NUMBER = '+1234567890'  # Your Twilio phone number
TWILIO_WHATSAPP_NUMBER = 'whatsapp:+1234567890'  # Your Twilio WhatsApp number

# WhatsApp Business API Configuration (alternative to Twilio)
WHATSAPP_BUSINESS_API = {
    'ACCESS_TOKEN': 'your_whatsapp_business_access_token',
    'PHONE_NUMBER_ID': 'your_phone_number_id',
    'VERIFY_TOKEN': 'your_verify_token',
    'APP_SECRET': 'your_app_secret',
}

# Local SMS API Configuration (alternative to Twilio)
LOCAL_SMS_API = {
    'URL': 'https://your-sms-provider.com/api/send',
    'API_KEY': 'your_api_key',
    'SENDER_ID': 'GALLETASK',
}

# Celery Configuration for Async Tasks
CELERY_BROKER_URL = 'redis://localhost:6379/0'  # or 'amqp://localhost'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'America/Santiago'

# Notification Rate Limiting
NOTIFICATION_RATE_LIMITS = {
    'email': {
        'per_user_per_hour': 10,
        'per_user_per_day': 50,
    },
    'sms': {
        'per_user_per_hour': 5,
        'per_user_per_day': 20,
    },
    'whatsapp': {
        'per_user_per_hour': 5,
        'per_user_per_day': 20,
    },
}

# Logging Configuration for Notifications
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'notifications.log',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'notifications': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
