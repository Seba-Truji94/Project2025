from django import forms
from django.utils import timezone
from datetime import datetime, timedelta
from shop.models import DiscountCoupon, Category, Product


class CouponForm(forms.ModelForm):
    """Formulario para crear y editar cupones de descuento"""
    
    class Meta:
        model = DiscountCoupon
        fields = [
            'code', 'name', 'description', 'discount_type', 'discount_value',
            'minimum_order_amount', 'maximum_discount_amount', 'usage_type',
            'max_uses', 'valid_from', 'valid_until', 'is_active',
            'categories', 'products', 'excluded_products'
        ]
        
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: DESCUENTO20',
                'maxlength': 50
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre descriptivo del cupón'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción que verán los clientes (opcional)'
            }),
            'discount_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'discount_value': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'placeholder': '10'
            }),
            'minimum_order_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'placeholder': '0'
            }),
            'maximum_discount_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'placeholder': 'Opcional'
            }),
            'usage_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'max_uses': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Dejar vacío para ilimitado'
            }),
            'valid_from': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'valid_until': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'custom-control-input'
            }),
            'categories': forms.SelectMultiple(attrs={
                'class': 'form-control',
                'size': '5'
            }),
            'products': forms.SelectMultiple(attrs={
                'class': 'form-control',
                'size': '5'
            }),
            'excluded_products': forms.SelectMultiple(attrs={
                'class': 'form-control',
                'size': '5'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Establecer valores por defecto
        if not self.instance.pk:  # Solo para nuevos cupones
            # Fecha de inicio por defecto: ahora
            self.fields['valid_from'].initial = timezone.now().strftime('%Y-%m-%dT%H:%M')
            
            # Fecha de fin por defecto: 30 días desde ahora
            default_end = timezone.now() + timedelta(days=30)
            self.fields['valid_until'].initial = default_end.strftime('%Y-%m-%dT%H:%M')
            
            # Valor por defecto para minimum_order_amount
            self.fields['minimum_order_amount'].initial = 0
        
        # Hacer que todos los campos requeridos estén marcados
        required_fields = ['code', 'name', 'discount_type', 'discount_value', 'valid_from', 'valid_until', 'usage_type']
        for field_name in required_fields:
            if field_name in self.fields:
                self.fields[field_name].required = True

    def clean_code(self):
        """Validar que el código sea único"""
        code = self.cleaned_data.get('code')
        if code:
            code = code.upper().strip()
            
            # Verificar unicidad
            qs = DiscountCoupon.objects.filter(code=code)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            
            if qs.exists():
                raise forms.ValidationError("Ya existe un cupón con este código.")
            
            return code
        return code

    def clean_discount_value(self):
        """Validar el valor del descuento"""
        discount_value = self.cleaned_data.get('discount_value')
        discount_type = self.cleaned_data.get('discount_type')
        
        if discount_value is not None:
            if discount_value <= 0:
                raise forms.ValidationError("El valor del descuento debe ser mayor a 0.")
            
            if discount_type == 'percentage' and discount_value > 100:
                raise forms.ValidationError("El descuento de porcentaje no puede ser mayor a 100%.")
        
        return discount_value

    def clean_valid_until(self):
        """Validar que la fecha de fin sea después de la fecha de inicio"""
        valid_until = self.cleaned_data.get('valid_until')
        valid_from = self.cleaned_data.get('valid_from')
        
        if valid_until and valid_from:
            if valid_until <= valid_from:
                raise forms.ValidationError("La fecha de fin debe ser posterior a la fecha de inicio.")
        
        return valid_until

    def clean(self):
        """Validaciones adicionales"""
        cleaned_data = super().clean()
        
        discount_type = cleaned_data.get('discount_type')
        maximum_discount_amount = cleaned_data.get('maximum_discount_amount')
        
        # Si es descuento de porcentaje y no hay máximo, sugerir uno
        if discount_type == 'percentage' and not maximum_discount_amount:
            # No es un error, pero podríamos agregar una advertencia
            pass
            
        return cleaned_data

    def save(self, commit=True):
        """Guardar el cupón con validaciones adicionales"""
        instance = super().save(commit=False)
        
        # Convertir código a mayúsculas
        if instance.code:
            instance.code = instance.code.upper().strip()
        
        if commit:
            instance.save()
            # Guardar relaciones many-to-many
            self.save_m2m()
        
        return instance
