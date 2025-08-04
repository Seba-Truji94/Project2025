"""
Formularios para el sistema de notificaciones
"""
from django import forms
from django.contrib.auth.models import User
from .models import UserNotificationPreference, NotificationType, NotificationChannel, NotificationTemplate


class NotificationPreferenceForm(forms.ModelForm):
    """Formulario para preferencias de notificación del usuario"""
    
    class Meta:
        model = UserNotificationPreference
        fields = [
            'email_enabled', 'sms_enabled', 'whatsapp_enabled', 'push_enabled',
            'order_notifications', 'shipping_notifications', 
            'promotional_notifications', 'support_notifications',
            'phone_number', 'whatsapp_number'
        ]
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+56912345678'
            }),
            'whatsapp_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+56912345678'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Personalizar widgets
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            else:
                field.widget.attrs.update({'class': 'form-control'})


class BulkNotificationForm(forms.Form):
    """Formulario para enviar notificaciones masivas"""
    
    recipients = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_active=True),
        widget=forms.CheckboxSelectMultiple,
        label="Destinatarios"
    )
    
    notification_type = forms.ChoiceField(
        choices=NotificationType.choices,
        label="Tipo de Notificación",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    channels = forms.MultipleChoiceField(
        choices=NotificationChannel.choices,
        widget=forms.CheckboxSelectMultiple,
        label="Canales de Envío",
        initial=['email']
    )
    
    subject = forms.CharField(
        max_length=200,
        label="Asunto",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Asunto de la notificación'
        })
    )
    
    message = forms.CharField(
        label="Mensaje",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Contenido del mensaje'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Opciones de destinatarios predefinidas
        self.fields['recipient_filter'] = forms.ChoiceField(
            choices=[
                ('all', 'Todos los usuarios'),
                ('subscribers', 'Solo suscriptores'),
                ('recent', 'Usuarios recientes (últimos 30 días)'),
                ('custom', 'Selección personalizada')
            ],
            label="Filtro de Destinatarios",
            widget=forms.RadioSelect(),
            initial='subscribers'
        )
    
    def clean(self):
        cleaned_data = super().clean()
        recipient_filter = cleaned_data.get('recipient_filter')
        recipients = cleaned_data.get('recipients')
        
        if recipient_filter == 'custom' and not recipients:
            raise forms.ValidationError("Debe seleccionar al menos un destinatario para envío personalizado")
        
        return cleaned_data


class TestNotificationForm(forms.Form):
    """Formulario para enviar notificación de prueba"""
    
    channels = forms.MultipleChoiceField(
        choices=NotificationChannel.choices,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label="Canales de Prueba",
        initial=['email']
    )
    
    custom_message = forms.CharField(
        required=False,
        label="Mensaje Personalizado (opcional)",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Deja en blanco para usar mensaje predeterminado'
        })
    )


class NotificationTemplateForm(forms.ModelForm):
    """Formulario para crear/editar plantillas de notificación"""
    
    class Meta:
        model = NotificationTemplate
        fields = ['name', 'notification_type', 'channel', 'subject', 'template_body', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Confirmación de Pedido - Email'
            }),
            'notification_type': forms.Select(attrs={'class': 'form-control'}),
            'channel': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Variables disponibles: {{user.first_name}}, {{order.id}}, etc.'
            }),
            'template_body': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Usar variables como {{user.first_name}} para personalizar'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
        labels = {
            'name': 'Nombre de la Plantilla',
            'notification_type': 'Tipo de Notificación',
            'channel': 'Canal',
            'subject': 'Asunto (solo para Email)',
            'template_body': 'Cuerpo del Mensaje',
            'is_active': 'Plantilla Activa'
        }
        help_texts = {
            'subject': 'Para SMS y WhatsApp, este campo es opcional',
            'template_body': 'Puedes usar variables como {{user.first_name}}, {{order.id}}, etc.'
        }


class CampaignForm(forms.Form):
    """Formulario para campañas de marketing"""
    
    campaign_name = forms.CharField(
        max_length=100,
        label="Nombre de la Campaña",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: Promoción Galletas de Chocolate'
        })
    )
    
    target_audience = forms.ChoiceField(
        choices=[
            ('all_subscribers', 'Todos los suscriptores'),
            ('recent_customers', 'Clientes recientes'),
            ('inactive_customers', 'Clientes inactivos'),
            ('high_value_customers', 'Clientes de alto valor'),
            ('custom', 'Selección personalizada')
        ],
        label="Audiencia Objetivo",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    channels = forms.MultipleChoiceField(
        choices=NotificationChannel.choices,
        widget=forms.CheckboxSelectMultiple,
        label="Canales de Envío",
        initial=['email']
    )
    
    subject = forms.CharField(
        max_length=200,
        label="Asunto",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '🍪 ¡Oferta especial en galletas!'
        })
    )
    
    message = forms.CharField(
        label="Mensaje de la Campaña",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 6,
            'placeholder': 'Mensaje atractivo para tu campaña'
        })
    )
    
    schedule_send = forms.BooleanField(
        required=False,
        label="Programar Envío",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    send_date = forms.DateTimeField(
        required=False,
        label="Fecha y Hora de Envío",
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        schedule_send = cleaned_data.get('schedule_send')
        send_date = cleaned_data.get('send_date')
        
        if schedule_send and not send_date:
            raise forms.ValidationError("Debe especificar fecha y hora para envío programado")
        
        return cleaned_data
