# Integration Guide for Galletas Kati Notifications System

## 1. Installation Steps

### 1.1 Install Required Packages
```bash
pip install celery redis twilio requests phonenumbers django-phonenumber-field
```

### 1.2 Add to Django Settings
Add these lines to your main `settings.py`:

```python
INSTALLED_APPS = [
    # ... your existing apps
    'phonenumber_field',
    'notifications',
]

# Import notification settings
from notifications.config.settings import *
```

### 1.3 Add URLs
Add to your main `urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    # ... your existing URLs
    path('notifications/', include('notifications.urls')),
]
```

### 1.4 Celery Setup
Copy `notifications/config/celery.py` to your project root as `celery.py`

Add to your project's `__init__.py`:
```python
from .celery import app as celery_app

__all__ = ('celery_app',)
```

## 2. Database Migration
```bash
python manage.py makemigrations notifications
python manage.py migrate
```

## 3. Environment Configuration

Create a `.env` file with your credentials:

```env
# Email Configuration
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Twilio Configuration
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+1234567890
TWILIO_WHATSAPP_NUMBER=whatsapp:+1234567890

# WhatsApp Business API (alternative)
WHATSAPP_ACCESS_TOKEN=your_access_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
```

## 4. Redis Setup (for Celery)

### Windows:
1. Download Redis from: https://github.com/microsoftarchive/redis/releases
2. Install and start Redis service

### Linux/Mac:
```bash
# Install Redis
sudo apt-get install redis-server  # Ubuntu
brew install redis                 # Mac

# Start Redis
redis-server
```

## 5. Running the System

### Start Django Development Server
```bash
python manage.py runserver
```

### Start Celery Worker (new terminal)
```bash
celery -A galletas_kati worker --loglevel=info
```

### Start Celery Beat (new terminal)
```bash
celery -A galletas_kati beat --loglevel=info
```

## 6. Usage Examples

### 6.1 Send Order Confirmation
```python
from notifications.services import NotificationService

# Send order confirmation
NotificationService.send_order_confirmation(
    user=user,
    order_id="ORD-001",
    total=25000,
    status="confirmed"
)
```

### 6.2 Send Promotion
```python
# Send promotion to all users
NotificationService.send_bulk_notification(
    notification_type="promotion",
    message="¡20% descuento en todas las galletas!",
    channels=["email", "sms", "whatsapp"],
    extra_data={
        "discount_code": "PROMO20",
        "discount_percentage": 20,
        "expiry_date": "2025-02-15"
    }
)
```

### 6.3 Send Support Ticket Update
```python
# Send support ticket notification
NotificationService.send_support_notification(
    user=user,
    ticket_id="TKT-123",
    title="Problema con el pago",
    status="resolved",
    response="Hemos solucionado el problema con tu pago."
)
```

## 7. Admin Interface

Access the Django admin at `/admin/` to:
- View notification logs
- Manage notification templates
- Send bulk notifications
- Configure user preferences

## 8. User Interface

Users can access:
- `/notifications/preferences/` - Configure notification preferences
- `/notifications/` - View notification history

## 9. API Endpoints

- `POST /notifications/webhook/delivery/` - Delivery status webhooks
- `GET /notifications/preferences/` - Get user preferences
- `POST /notifications/preferences/` - Update preferences
- `POST /notifications/test/` - Send test notification

## 10. Monitoring

Check logs in:
- `notifications.log` - Application logs
- Celery worker output - Task execution logs
- Django admin notification logs - Delivery status

## 11. Troubleshooting

### Common Issues:

1. **Celery not working**: Ensure Redis is running
2. **SMS not sending**: Check Twilio credentials
3. **Email not sending**: Verify SMTP settings
4. **WhatsApp not working**: Confirm WhatsApp Business API setup

### Debug Commands:
```bash
# Test notification system
python manage.py shell
>>> from notifications.services import NotificationService
>>> NotificationService.test_configuration()

# Check Celery tasks
celery -A galletas_kati inspect active

# Monitor Redis
redis-cli monitor
```

This notification system provides:
✅ Multi-channel support (Email, SMS, WhatsApp)
✅ Async processing with Celery
✅ User preference management
✅ Template system
✅ Rate limiting
✅ Delivery tracking
✅ Admin interface
✅ Webhook support
✅ Bulk notifications
✅ Campaign management
