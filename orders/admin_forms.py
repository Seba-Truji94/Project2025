from django import forms
from .models import Order, OrderStatusHistory


class OrderStatusForm(forms.ModelForm):
    """Formulario para actualizar el estado de un pedido"""
    status_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Notas sobre el cambio de estado (opcional)'
        }),
        label='Notas del cambio'
    )
    
    class Meta:
        model = Order
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-select'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Personalizar las opciones de estado con colores
        status_choices_with_colors = []
        for value, display in Order.STATUS_CHOICES:
            status_choices_with_colors.append((value, display))
        
        self.fields['status'].choices = status_choices_with_colors
        self.fields['status'].widget.attrs.update({
            'class': 'form-select status-select'
        })


class OrderNotesForm(forms.ModelForm):
    """Formulario para actualizar las notas de un pedido"""
    
    class Meta:
        model = Order
        fields = ['notes', 'tracking_number']
        widgets = {
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Notas especiales para este pedido...'
            }),
            'tracking_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de seguimiento del envío'
            })
        }
        labels = {
            'notes': 'Notas del Pedido',
            'tracking_number': 'Número de Seguimiento'
        }


class OrderFilterForm(forms.Form):
    """Formulario para filtrar pedidos en la vista de administración"""
    STATUS_CHOICES = [('all', 'Todos los Estados')] + list(Order.STATUS_CHOICES)
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Estado'
    )
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por número de pedido, usuario, email...'
        }),
        label='Buscar'
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Desde'
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Hasta'
    )


class BulkOrderUpdateForm(forms.Form):
    """Formulario para actualización masiva de pedidos"""
    new_status = forms.ChoiceField(
        choices=Order.STATUS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Nuevo Estado'
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Notas para la actualización masiva (opcional)'
        }),
        label='Notas'
    )
