from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    REGION_CHOICES = [
        ('rm', 'Región Metropolitana'),
        ('v', 'V Región - Valparaíso'),
        ('viii', 'VIII Región - Biobío'),
        ('iv', 'IV Región - Coquimbo'),
        ('other', 'Otra Región'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    
    # Dirección por defecto
    address = models.CharField(max_length=250, blank=True)
    city = models.CharField(max_length=100, blank=True)
    region = models.CharField(max_length=10, choices=REGION_CHOICES, blank=True)
    postal_code = models.CharField(max_length=10, blank=True)
    
    # Preferencias
    newsletter_subscription = models.BooleanField(default=True)
    receives_offers = models.BooleanField(default=True)
    
    # Información adicional
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Perfil de {self.user.username}"
    
    @property
    def full_name(self):
        return f"{self.user.first_name} {self.user.last_name}".strip()
    
    @property
    def display_name(self):
        if self.full_name:
            return self.full_name
        return self.user.username
    
    def get_full_address(self):
        parts = [self.address, self.city, self.get_region_display()]
        return ', '.join(filter(None, parts))


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Crear automáticamente un perfil cuando se crea un usuario"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Guardar el perfil cuando se guarda el usuario"""
    if hasattr(instance, 'profile'):
        instance.profile.save()


class Address(models.Model):
    """Modelo para múltiples direcciones por usuario"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    name = models.CharField(max_length=100, help_text="Nombre para esta dirección (ej: Casa, Trabajo)")
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=250)
    city = models.CharField(max_length=100)
    region = models.CharField(max_length=10, choices=UserProfile.REGION_CHOICES)
    postal_code = models.CharField(max_length=10, blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Addresses'
        ordering = ['-is_default', '-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"
    
    def save(self, *args, **kwargs):
        # Si esta dirección se marca como predeterminada, 
        # quitar la marca de todas las demás del mismo usuario
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_address(self):
        parts = [self.address, self.city, self.get_region_display()]
        return ', '.join(filter(None, parts))


class Wishlist(models.Model):
    """Lista de deseos del usuario"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wishlist')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Lista de deseos de {self.user.username}"


class WishlistItem(models.Model):
    """Elementos en la lista de deseos"""
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('shop.Product', on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('wishlist', 'product')
        ordering = ['-added_at']
    
    def __str__(self):
        return f"{self.product.name} en lista de {self.wishlist.user.username}"
