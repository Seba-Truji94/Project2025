from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, Address


class UserRegistrationForm(UserCreationForm):
    """Formulario de registro extendido"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'tu@email.com'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tu nombre'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tu apellido'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nombre de usuario'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña'
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    """Formulario para editar el perfil del usuario"""
    
    class Meta:
        model = UserProfile
        fields = [
            'avatar', 'phone', 'birth_date', 'address', 'city', 
            'region', 'postal_code', 'newsletter_subscription', 'receives_offers'
        ]
        widgets = {
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+56 9 1234 5678'
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Dirección completa'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ciudad'
            }),
            'region': forms.Select(attrs={
                'class': 'form-select'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Código postal'
            }),
            'newsletter_subscription': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'receives_offers': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'avatar': 'Foto de Perfil',
            'phone': 'Teléfono',
            'birth_date': 'Fecha de Nacimiento',
            'address': 'Dirección',
            'city': 'Ciudad',
            'region': 'Región',
            'postal_code': 'Código Postal',
            'newsletter_subscription': 'Suscribirse al newsletter',
            'receives_offers': 'Recibir ofertas por email'
        }

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        
        if avatar:
            # Validar el tamaño del archivo (5MB máximo)
            if avatar.size > 5 * 1024 * 1024:
                raise forms.ValidationError('El archivo es demasiado grande. El tamaño máximo es 5MB.')
            
            # Validar el tipo de archivo
            if not avatar.content_type.startswith('image/'):
                raise forms.ValidationError('El archivo debe ser una imagen.')
        
        return avatar

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        
        if phone:
            # Eliminar espacios y caracteres especiales para validación
            clean_phone = ''.join(char for char in phone if char.isdigit() or char == '+')
            
            # Validar formato chileno básico
            if not (clean_phone.startswith('+56') or clean_phone.startswith('56') or clean_phone.startswith('9')):
                if len(clean_phone) < 8:
                    raise forms.ValidationError('Ingresa un número de teléfono válido.')
        
        return phone


class UserForm(forms.ModelForm):
    """Formulario para editar información básica del usuario"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tu nombre'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tu apellido'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'tu@email.com'
            })
        }


class AddressForm(forms.ModelForm):
    """Formulario para crear/editar direcciones"""
    
    class Meta:
        model = Address
        fields = [
            'name', 'first_name', 'last_name', 'phone', 
            'address', 'city', 'region', 'postal_code', 'is_default'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Casa, Trabajo, etc.'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellido'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+56 9 1234 5678'
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Dirección completa'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ciudad'
            }),
            'region': forms.Select(attrs={
                'class': 'form-select'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Código postal'
            }),
            'is_default': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'name': 'Nombre de la dirección',
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'phone': 'Teléfono',
            'address': 'Dirección',
            'city': 'Ciudad',
            'region': 'Región',
            'postal_code': 'Código postal',
            'is_default': 'Dirección predeterminada'
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        address = super().save(commit=False)
        if self.user:
            address.user = self.user
        if commit:
            address.save()
        return address
