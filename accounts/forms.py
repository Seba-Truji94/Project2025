from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from .models import UserProfile, Address
from security.utils import sanitize_input, validate_file_upload
import re


class UserRegistrationForm(UserCreationForm):
    """Formulario de registro extendido con validaciones de seguridad"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'tu@email.com',
            'autocomplete': 'email'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tu nombre',
            'autocomplete': 'given-name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tu apellido',
            'autocomplete': 'family-name'
        })
    )
    
    # Campo honey pot para prevenir bots
    website = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
        help_text="No llenar este campo"
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nombre de usuario',
            'autocomplete': 'username',
            'minlength': '3',
            'maxlength': '20'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Contraseña',
            'autocomplete': 'new-password',
            'id': 'password-input'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña',
            'autocomplete': 'new-password'
        })
        
        # Actualizar help texts de contraseña
        self.fields['password1'].help_text = (
            "Su contraseña debe tener al menos 12 caracteres, "
            "incluir mayúsculas, minúsculas, números y símbolos."
        )

    def clean_website(self):
        """Honey pot - si se llena, es un bot"""
        website = self.cleaned_data.get('website')
        if website:
            raise ValidationError("Formulario inválido.")
        return website

    def clean_username(self):
        username = self.cleaned_data.get('username')
        username = sanitize_input(username)
        
        # Validar caracteres permitidos
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise ValidationError("El nombre de usuario solo puede contener letras, números y guiones bajos.")
        
        # Verificar palabras prohibidas
        prohibited_words = ['admin', 'root', 'administrator', 'superuser', 'test']
        if username.lower() in prohibited_words:
            raise ValidationError("Este nombre de usuario no está permitido.")
        
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        email = sanitize_input(email)
        
        # Verificar que el email no esté en uso
        if User.objects.filter(email=email).exists():
            raise ValidationError("Este email ya está registrado.")
        
        # Validar dominio (opcional)
        domain = email.split('@')[1].lower()
        blocked_domains = ['tempmail.com', '10minutemail.com', 'guerrillamail.com']
        if domain in blocked_domains:
            raise ValidationError("Dominios de email temporales no permitidos.")
        
        return email

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        return sanitize_input(first_name)

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        return sanitize_input(last_name)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    """Formulario para editar el perfil del usuario con validaciones de seguridad"""
    
    class Meta:
        model = UserProfile
        fields = [
            'avatar', 'phone', 'birth_date', 'address', 'city', 
            'region', 'postal_code', 'newsletter_subscription', 'receives_offers'
        ]
        widgets = {
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/jpeg,image/jpg,image/png,image/gif,image/webp'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+56 9 1234 5678',
                'pattern': r'[\+]?[0-9\s\-\(\)]+',
                'maxlength': '20'
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': '1900-01-01',
                'max': '2010-12-31'  # Mínimo 13 años
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Dirección completa',
                'maxlength': '200'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ciudad',
                'maxlength': '50'
            }),
            'region': forms.Select(attrs={
                'class': 'form-select'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Código postal',
                'pattern': r'[0-9]{5,7}',
                'maxlength': '7'
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
            try:
                validate_file_upload(avatar)
            except ValueError as e:
                raise ValidationError(str(e))
        
        return avatar

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        
        if phone:
            phone = sanitize_input(phone)
            # Eliminar espacios y caracteres especiales para validación
            clean_phone = ''.join(char for char in phone if char.isdigit() or char == '+')
            
            # Validar formato chileno básico
            if not (clean_phone.startswith('+56') or clean_phone.startswith('56') or clean_phone.startswith('9')):
                if len(clean_phone) < 8:
                    raise ValidationError('Ingresa un número de teléfono válido.')
        
        return phone

    def clean_address(self):
        address = self.cleaned_data.get('address')
        if address:
            return sanitize_input(address)
        return address

    def clean_city(self):
        city = self.cleaned_data.get('city')
        if city:
            return sanitize_input(city)
        return city


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
