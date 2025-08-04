"""
Formularios administrativos para el sistema de notificaciones
Solo para superusuarios
"""

from django import forms
from django.contrib.auth.models import User
from .models import UserNotificationPreference, NotificationTemplate, Notification
import json


class AdminBulkNotificationForm(forms.Form):
    """Formulario para envío masivo de notificaciones (solo admin)"""
    
    USER_FILTER_CHOICES = [
        ('all', 'Todos los usuarios'),
        ('active', 'Solo usuarios activos'),
        ('staff', 'Solo staff'),
        ('has_orders', 'Usuarios con pedidos'),
        ('new_users', 'Usuarios nuevos (últimos 30 días)'),
        ('inactive', 'Usuarios inactivos'),
        ('subscribers', 'Solo suscriptores a notificaciones'),
    ]
    
    NOTIFICATION_TYPE_CHOICES = [
        ('general', 'General'),
        ('promotion', 'Promoción'),
        ('system', 'Sistema'),
        ('reminder', 'Recordatorio'),
        ('security', 'Seguridad'),
        ('maintenance', 'Mantenimiento'),
    ]
    
    CHANNEL_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('whatsapp', 'WhatsApp'),
        ('push', 'Notificación Push'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
        ('urgent', 'Urgente'),
    ]
    
    user_filter = forms.ChoiceField(
        choices=USER_FILTER_CHOICES,
        label='Enviar a',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    specific_users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        label='Usuarios específicos',
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control',
            'size': '8'
        }),
        help_text='Mantén Ctrl presionado para seleccionar múltiples usuarios'
    )
    
    notification_type = forms.ChoiceField(
        choices=NOTIFICATION_TYPE_CHOICES,
        label='Tipo de notificación',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    priority = forms.ChoiceField(
        choices=PRIORITY_CHOICES,
        label='Prioridad',
        initial='medium',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    channels = forms.MultipleChoiceField(
        choices=CHANNEL_CHOICES,
        label='Canales',
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )
    
    subject = forms.CharField(
        max_length=200,
        label='Asunto',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Asunto de la notificación'
        })
    )
    
    message = forms.CharField(
        label='Mensaje',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 6,
            'placeholder': 'Contenido del mensaje...\n\nPuedes usar variables como:\n{user.first_name} - Nombre del usuario\n{user.email} - Email del usuario\n{company} - Nombre de la empresa'
        })
    )
    
    scheduled_at = forms.DateTimeField(
        required=False,
        label='Programar para',
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        }),
        help_text='Dejar vacío para enviar inmediatamente'
    )
    
    extra_data = forms.CharField(
        required=False,
        label='Datos adicionales (JSON)',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': '{\n  "discount_code": "PROMO20",\n  "expiry_date": "2025-12-31",\n  "link": "https://galletaskati.com/promo"\n}'
        }),
        help_text='Datos adicionales en formato JSON (opcional)'
    )
    
    test_mode = forms.BooleanField(
        required=False,
        label='Modo de prueba',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text='Marcado: solo envía al administrador para prueba'
    )
    
    def clean_extra_data(self):
        extra_data = self.cleaned_data.get('extra_data')
        if extra_data:
            try:
                json.loads(extra_data)
            except json.JSONDecodeError:
                raise forms.ValidationError('Formato JSON inválido')
        return extra_data


class AdminTestNotificationForm(forms.Form):
    """Formulario para pruebas de notificación avanzadas"""
    
    CHANNEL_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('whatsapp', 'WhatsApp'),
        ('all', 'Todos los canales'),
    ]
    
    channel = forms.ChoiceField(
        choices=CHANNEL_CHOICES,
        label='Canal de prueba',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    recipient = forms.CharField(
        label='Destinatario',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'email@example.com o +56912345678'
        }),
        help_text='Email para email, número para SMS/WhatsApp'
    )
    
    message = forms.CharField(
        label='Mensaje de prueba',
        initial='🧪 PRUEBA: Este es un mensaje de prueba del sistema de notificaciones de Galletas Kati.\n\nSistema funcionando correctamente ✅',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4
        })
    )
    
    include_system_info = forms.BooleanField(
        required=False,
        initial=True,
        label='Incluir información del sistema',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text='Incluye fecha, hora, y detalles técnicos'
    )


class AdminNotificationTemplateForm(forms.ModelForm):
    """Formulario para gestión de plantillas administrativas"""
    
    class Meta:
        model = NotificationTemplate
        fields = ['name', 'notification_type', 'channel', 'subject', 'template_body', 'variables', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre descriptivo de la plantilla'
            }),
            'notification_type': forms.Select(attrs={'class': 'form-control'}),
            'channel': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Asunto de la notificación (solo para email)'
            }),
            'template_body': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 12,
                'placeholder': 'Contenido de la plantilla...\n\nVariables disponibles:\n{user.first_name} - Nombre\n{user.email} - Email\n{company} - Empresa\n{date} - Fecha actual'
            }),
            'variables': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': '{\n  "variable1": "descripción",\n  "variable2": "descripción"\n}'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

    def clean_variables(self):
        variables = self.cleaned_data.get('variables')
        if variables:
            try:
                json.loads(variables)
            except json.JSONDecodeError:
                raise forms.ValidationError('Formato JSON inválido para variables')
        return variables


class AdminCampaignForm(forms.Form):
    """Formulario para campañas administrativas"""
    
    name = forms.CharField(
        max_length=200,
        label='Nombre de la campaña',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: Promoción Black Friday 2025'
        })
    )
    
    description = forms.CharField(
        required=False,
        label='Descripción',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Descripción interna de la campaña...'
        })
    )
    
    template = forms.ModelChoiceField(
        queryset=NotificationTemplate.objects.filter(is_active=True),
        required=False,
        label='Plantilla',
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label='Crear mensaje personalizado...'
    )
    
    target_users = forms.ChoiceField(
        choices=AdminBulkNotificationForm.USER_FILTER_CHOICES,
        label='Usuarios objetivo',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    channels = forms.MultipleChoiceField(
        choices=AdminBulkNotificationForm.CHANNEL_CHOICES,
        label='Canales',
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )
    
    subject = forms.CharField(
        required=False,
        max_length=200,
        label='Asunto personalizado',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Solo si no usas plantilla'
        })
    )
    
    message = forms.CharField(
        required=False,
        label='Mensaje personalizado',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 6,
            'placeholder': 'Solo si no usas plantilla'
        })
    )
    
    scheduled_at = forms.DateTimeField(
        label='Fecha de envío',
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        })
    )
    
    variables = forms.CharField(
        required=False,
        label='Variables de la campaña (JSON)',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': '{\n  "discount_percentage": 20,\n  "promo_code": "BLACK20",\n  "expiry_date": "2025-12-31"\n}'
        }),
        help_text='Variables que se usarán en la plantilla'
    )
    
    budget = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        label='Presupuesto estimado',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '0.00'
        })
    )
    
    def clean_variables(self):
        variables = self.cleaned_data.get('variables')
        if variables:
            try:
                json.loads(variables)
            except json.JSONDecodeError:
                raise forms.ValidationError('Formato JSON inválido')
        return variables
    
    def clean(self):
        cleaned_data = super().clean()
        template = cleaned_data.get('template')
        subject = cleaned_data.get('subject')
        message = cleaned_data.get('message')
        
        if not template and not (subject and message):
            raise forms.ValidationError('Debe seleccionar una plantilla O proporcionar asunto y mensaje personalizado')
        
        return cleaned_data


class AdminNotificationFilterForm(forms.Form):
    """Formulario para filtrar notificaciones en el admin"""
    
    STATUS_CHOICES = [
        ('', 'Todos los estados'),
        ('pending', 'Pendiente'),
        ('sent', 'Enviado'),
        ('delivered', 'Entregado'),
        ('failed', 'Fallido'),
        ('cancelled', 'Cancelado'),
    ]
    
    CHANNEL_CHOICES = [
        ('', 'Todos los canales'),
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('whatsapp', 'WhatsApp'),
        ('push', 'Push'),
    ]
    
    TYPE_CHOICES = [
        ('', 'Todos los tipos'),
        ('general', 'General'),
        ('promotion', 'Promoción'),
        ('system', 'Sistema'),
        ('reminder', 'Recordatorio'),
        ('security', 'Seguridad'),
    ]
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    channel = forms.ChoiceField(
        choices=CHANNEL_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    notification_type = forms.ChoiceField(
        choices=TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    user_search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por email o nombre de usuario...'
        })
    )
    
    show_test = forms.BooleanField(
        required=False,
        label='Incluir notificaciones de prueba',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


class AdminSystemConfigForm(forms.Form):
    """Formulario para configuración del sistema de notificaciones"""
    
    # Configuración de email
    email_enabled = forms.BooleanField(
        required=False,
        initial=True,
        label='Email habilitado',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    email_rate_limit = forms.IntegerField(
        initial=100,
        min_value=1,
        max_value=1000,
        label='Límite de emails por hora',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    # Configuración de SMS
    sms_enabled = forms.BooleanField(
        required=False,
        initial=False,
        label='SMS habilitado',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    sms_rate_limit = forms.IntegerField(
        initial=50,
        min_value=1,
        max_value=500,
        label='Límite de SMS por hora',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    # Configuración de WhatsApp
    whatsapp_enabled = forms.BooleanField(
        required=False,
        initial=False,
        label='WhatsApp habilitado',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    whatsapp_rate_limit = forms.IntegerField(
        initial=80,
        min_value=1,
        max_value=500,
        label='Límite de WhatsApp por hora',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    # Configuración general
    max_retries = forms.IntegerField(
        initial=3,
        min_value=0,
        max_value=10,
        label='Máximo reintentos por notificación',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    log_retention_days = forms.IntegerField(
        initial=90,
        min_value=1,
        max_value=365,
        label='Días de retención de logs',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    enable_analytics = forms.BooleanField(
        required=False,
        initial=True,
        label='Habilitar análisis y estadísticas',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


class AdminUserPreferenceForm(forms.ModelForm):
    """Formulario para editar preferencias de usuarios específicos"""
    
    class Meta:
        model = UserNotificationPreference
        fields = '__all__'
        widgets = {
            'email_address': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'whatsapp_number': forms.TextInput(attrs={'class': 'form-control'}),
            'notification_types': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
