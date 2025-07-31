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
