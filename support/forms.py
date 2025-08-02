from django import forms
from .models import SupportTicket, SupportCategory


class SupportTicketForm(forms.ModelForm):
    class Meta:
        model = SupportTicket
        fields = ['category', 'priority', 'subject', 'description']
        widgets = {
            'category': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Describe brevemente tu problema o consulta',
                'required': True,
                'maxlength': 255
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Describe detalladamente tu problema, incluyendo los pasos que realizaste, mensajes de error (si los hay), y cualquier información adicional que pueda ser útil...',
                'required': True
            })
        }
        labels = {
            'category': 'Categoría del problema',
            'priority': 'Prioridad',
            'subject': 'Asunto',
            'description': 'Descripción detallada'
        }
        help_texts = {
            'category': 'Selecciona la categoría que mejor describe tu problema',
            'priority': 'Indica qué tan urgente es tu consulta',
            'subject': 'Un resumen breve y claro del problema',
            'description': 'Proporciona todos los detalles posibles para una mejor asistencia'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Personalizar opciones de prioridad
        self.fields['priority'].choices = [
            ('', 'Seleccionar prioridad'),
            ('low', '🟢 Baja - Consulta general'),
            ('medium', '🟡 Media - Problema que no es urgente'),
            ('high', '🟠 Alta - Problema que afecta mi experiencia'),
            ('urgent', '🔴 Urgente - Problema crítico que requiere atención inmediata')
        ]
        
        # Asegurar que las categorías estén disponibles
        if SupportCategory.objects.exists():
            self.fields['category'].queryset = SupportCategory.objects.filter(is_active=True)
        else:
            # Crear categorías por defecto si no existen
            default_categories = [
                'Problemas de pedidos',
                'Problemas de pago',
                'Problemas técnicos',
                'Consultas generales',
                'Devoluciones y reembolsos'
            ]
            for cat_name in default_categories:
                SupportCategory.objects.get_or_create(
                    name=cat_name,
                    defaults={'description': f'Categoría para {cat_name.lower()}'}
                )
            self.fields['category'].queryset = SupportCategory.objects.filter(is_active=True)

    def clean_subject(self):
        subject = self.cleaned_data.get('subject')
        if subject:
            subject = subject.strip()
            if len(subject) < 10:
                raise forms.ValidationError(
                    'El asunto debe tener al menos 10 caracteres para ser descriptivo.'
                )
        return subject

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if description:
            description = description.strip()
            if len(description) < 20:
                raise forms.ValidationError(
                    'La descripción debe tener al menos 20 caracteres para proporcionar suficiente contexto.'
                )
        return description
