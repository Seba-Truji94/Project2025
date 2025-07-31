from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from decimal import Decimal


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('shop:category_detail', args=[self.slug])


class Product(models.Model):
    CATEGORY_CHOICES = [
        ('bestseller', 'Más Vendidas'),
        ('premium', 'Premium'),
        ('healthy', 'Saludables'),
        ('classic', 'Clásicas'),
    ]
    
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    product_type = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='classic')
    description = models.TextField()
    ingredients = models.TextField(help_text="Lista de ingredientes separados por comas")
    price = models.DecimalField(max_digits=10, decimal_places=0)  # Precios en CLP sin decimales
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Porcentaje de descuento (0-100)")
    discount_price = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True, help_text="Precio con descuento manual")
    is_on_sale = models.BooleanField(default=False, help_text="¿Está en oferta?")
    image = models.ImageField(upload_to='products/')
    stock = models.PositiveIntegerField(default=0)
    min_stock_alert = models.PositiveIntegerField(default=5, help_text="Alerta cuando el stock sea menor a este valor")
    available = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    weight = models.PositiveIntegerField(help_text="Peso en gramos", default=100)
    nutrition_facts = models.TextField(blank=True, help_text="Información nutricional")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['available']),
            models.Index(fields=['featured']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('shop:product_detail', args=[self.slug])
    
    @property
    def formatted_price(self):
        """Retorna el precio formateado para Chile"""
        return f"${int(self.price):,}".replace(',', '.')
    
    @property
    def current_price(self):
        """Retorna el precio actual (con descuento si aplica)"""
        if self.is_on_sale:
            if self.discount_price:
                return self.discount_price
            elif self.discount_percentage > 0:
                discount_amount = self.price * (Decimal(str(self.discount_percentage)) / Decimal('100'))
                return self.price - discount_amount
        return self.price
    
    @property
    def formatted_current_price(self):
        """Retorna el precio actual formateado"""
        return f"${int(self.current_price):,}".replace(',', '.')
    
    @property
    def discount_amount(self):
        """Retorna la cantidad de descuento en pesos"""
        if self.is_on_sale and self.current_price < self.price:
            return self.price - self.current_price
        return 0
    
    @property
    def formatted_discount_amount(self):
        """Retorna el descuento formateado"""
        return f"${int(self.discount_amount):,}".replace(',', '.')
    
    @property
    def has_discount(self):
        """Retorna True si el producto tiene descuento activo"""
        return self.is_on_sale and self.current_price < self.price
    
    @property
    def is_in_stock(self):
        return self.stock > 0 and self.available
    
    @property
    def is_low_stock(self):
        """Retorna True si el stock está bajo"""
        return self.stock <= self.min_stock_alert and self.stock > 0
    
    @property
    def stock_status(self):
        """Retorna el estado del stock como texto"""
        if not self.available:
            return "No disponible"
        elif self.stock == 0:
            return "Sin stock"
        elif self.is_low_stock:
            return f"¡Últimas {self.stock} unidades!"
        else:
            return f"{self.stock} disponibles"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='additional_images')
    image = models.ImageField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=100, blank=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_featured', 'created_at']
    
    def __str__(self):
        return f"Imagen de {self.product.name}"


class Review(models.Model):
    RATING_CHOICES = [
        (1, '1 - Muy malo'),
        (2, '2 - Malo'),
        (3, '3 - Regular'),
        (4, '4 - Bueno'),
        (5, '5 - Excelente'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('product', 'user')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating}⭐)"
