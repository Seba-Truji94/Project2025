from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError


class TaxConfiguration(models.Model):
    """Configuración de impuestos (IVA)"""
    name = models.CharField(max_length=100, help_text="Ej: IVA Chile")
    rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Porcentaje de impuesto (19% = 19.00)"
    )
    is_active = models.BooleanField(default=True)
    applies_to_shipping = models.BooleanField(default=False, help_text="¿Se aplica al costo de envío?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Configuración de Impuesto"
        verbose_name_plural = "Configuraciones de Impuestos"
        ordering = ['-is_active', 'name']
    
    def __str__(self):
        status = "✅" if self.is_active else "❌"
        return f"{status} {self.name} ({self.rate}%)"
    
    @property
    def formatted_rate(self):
        return f"{self.rate}%"


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
    tax_configuration = models.ForeignKey(
        TaxConfiguration, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Configuración de impuesto aplicable"
    )
    is_tax_exempt = models.BooleanField(default=False, help_text="¿Exento de impuestos?")
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
    
    @property
    def price_without_tax(self):
        """Precio sin impuestos"""
        if self.is_tax_exempt or not self.tax_configuration:
            return self.current_price
        
        tax_rate = self.tax_configuration.rate / 100
        return self.current_price / (1 + tax_rate)
    
    @property
    def tax_amount(self):
        """Monto del impuesto"""
        if self.is_tax_exempt or not self.tax_configuration:
            return Decimal('0')
        
        return self.current_price - self.price_without_tax
    
    @property
    def formatted_price_without_tax(self):
        """Precio sin impuestos formateado"""
        return f"${int(self.price_without_tax):,}".replace(',', '.')
    
    @property
    def formatted_tax_amount(self):
        """Impuesto formateado"""
        return f"${int(self.tax_amount):,}".replace(',', '.')
    
    @property
    def tax_info_display(self):
        """Información de impuestos para mostrar"""
        if self.is_tax_exempt:
            return "Exento de impuestos"
        elif self.tax_configuration:
            return f"{self.tax_configuration.name} ({self.tax_configuration.rate}%)"
        else:
            return "Sin configuración de impuesto"


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


class DiscountCoupon(models.Model):
    """Cupones de descuento"""
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Porcentaje'),
        ('fixed_amount', 'Monto Fijo'),
        ('free_shipping', 'Envío Gratis'),
    ]
    
    USAGE_TYPE_CHOICES = [
        ('single_use', 'Un solo uso'),
        ('multiple_use', 'Uso múltiple'),
        ('per_customer', 'Una vez por cliente'),
    ]
    
    code = models.CharField(max_length=50, unique=True, help_text="Código del cupón (ej: DESCUENTO20)")
    name = models.CharField(max_length=100, help_text="Nombre descriptivo del cupón")
    description = models.TextField(blank=True, help_text="Descripción para el cliente")
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Valor del descuento (% o monto en CLP)"
    )
    minimum_order_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Monto mínimo de compra para aplicar el cupón"
    )
    maximum_discount_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Monto máximo de descuento (solo para porcentajes)"
    )
    usage_type = models.CharField(max_length=20, choices=USAGE_TYPE_CHOICES, default='multiple_use')
    max_uses = models.PositiveIntegerField(
        null=True, 
        blank=True, 
        help_text="Número máximo de usos (vacío = ilimitado)"
    )
    current_uses = models.PositiveIntegerField(default=0)
    valid_from = models.DateTimeField(help_text="Fecha de inicio de validez")
    valid_until = models.DateTimeField(help_text="Fecha de expiración")
    is_active = models.BooleanField(default=True)
    categories = models.ManyToManyField(
        Category, 
        blank=True, 
        help_text="Categorías aplicables (vacío = todas)"
    )
    products = models.ManyToManyField(
        'Product', 
        blank=True, 
        help_text="Productos específicos (vacío = todos)"
    )
    excluded_products = models.ManyToManyField(
        'Product', 
        blank=True, 
        related_name='excluded_from_coupons',
        help_text="Productos excluidos del descuento"
    )
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Cupón de Descuento"
        verbose_name_plural = "Cupones de Descuento"
        ordering = ['-created_at']
    
    def __str__(self):
        status = "✅" if self.is_active and self.is_valid else "❌"
        if self.discount_type == 'percentage':
            value = f"{self.discount_value}%"
        elif self.discount_type == 'fixed_amount':
            value = f"${int(self.discount_value):,}"
        else:
            value = "Envío Gratis"
        return f"{status} {self.code} - {value}"
    
    @property
    def is_valid(self):
        """Verifica si el cupón está actualmente válido"""
        now = timezone.now()
        return (
            self.is_active and 
            self.valid_from <= now <= self.valid_until and
            (self.max_uses is None or self.current_uses < self.max_uses)
        )
    
    @property
    def is_expired(self):
        """Verifica si el cupón ha expirado"""
        return timezone.now() > self.valid_until
    
    def get_usage_count(self):
        """Obtiene el número total de usos del cupón"""
        return self.current_uses
    
    @property
    def remaining_uses(self):
        """Usos restantes del cupón"""
        if self.max_uses is None:
            return "Ilimitado"
        return max(0, self.max_uses - self.current_uses)
    
    @property
    def status_display(self):
        """Estado del cupón para mostrar"""
        if not self.is_active:
            return "❌ Inactivo"
        elif timezone.now() < self.valid_from:
            return "⏳ Programado"
        elif timezone.now() > self.valid_until:
            return "⏰ Expirado"
        elif self.max_uses and self.current_uses >= self.max_uses:
            return "🚫 Agotado"
        else:
            return "✅ Activo"
    
    def clean(self):
        """Validaciones personalizadas"""
        if self.valid_from and self.valid_until and self.valid_from >= self.valid_until:
            raise ValidationError("La fecha de inicio debe ser anterior a la fecha de expiración")
        
        if self.discount_type == 'percentage' and self.discount_value > 100:
            raise ValidationError("El porcentaje de descuento no puede ser mayor a 100%")
        
        if self.discount_type == 'fixed_amount' and self.discount_value <= 0:
            raise ValidationError("El monto de descuento debe ser mayor a 0")


class CouponUsage(models.Model):
    """Registro de uso de cupones"""
    coupon = models.ForeignKey(DiscountCoupon, on_delete=models.CASCADE, related_name='usages')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, null=True, blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    used_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Uso de Cupón"
        verbose_name_plural = "Usos de Cupones"
        ordering = ['-used_at']
    
    def __str__(self):
        return f"{self.coupon.code} - {self.user.username} - ${int(self.discount_amount):,}"


class ProductStock(models.Model):
    """Registro de movimientos de stock"""
    MOVEMENT_TYPE_CHOICES = [
        ('entry', 'Entrada'),
        ('exit', 'Salida'),
        ('adjustment', 'Ajuste'),
        ('sale', 'Venta'),
        ('return', 'Devolución'),
        ('damage', 'Producto Dañado'),
        ('expired', 'Producto Vencido'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_movements')
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPE_CHOICES)
    quantity = models.IntegerField(help_text="Cantidad (positiva para entradas, negativa para salidas)")
    previous_stock = models.PositiveIntegerField()
    new_stock = models.PositiveIntegerField()
    reason = models.CharField(max_length=200, help_text="Motivo del movimiento")
    reference = models.CharField(max_length=100, blank=True, help_text="Referencia (ej: # de orden)")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Movimiento de Stock"
        verbose_name_plural = "Movimientos de Stock"
        ordering = ['-created_at']
    
    def __str__(self):
        symbol = "+" if self.quantity > 0 else ""
        return f"{self.product.name} - {symbol}{self.quantity} ({self.get_movement_type_display()})"


class Supplier(models.Model):
    """Proveedores de productos"""
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default="Chile")
    tax_id = models.CharField(max_length=20, blank=True, help_text="RUT del proveedor")
    is_active = models.BooleanField(default=True)
    rating = models.DecimalField(
        max_digits=3, 
        decimal_places=1, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Calificación del proveedor (1-5)"
    )
    notes = models.TextField(blank=True, help_text="Notas internas sobre el proveedor")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ['name']
    
    def __str__(self):
        status = "✅" if self.is_active else "❌"
        rating = f" ({self.rating}⭐)" if self.rating else ""
        return f"{status} {self.name}{rating}"


class ProductSupplier(models.Model):
    """Relación producto-proveedor con costos"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='supplier_info')
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='products')
    supplier_sku = models.CharField(max_length=100, blank=True, help_text="SKU del proveedor")
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Precio de costo")
    minimum_order_quantity = models.PositiveIntegerField(default=1)
    lead_time_days = models.PositiveIntegerField(help_text="Días de entrega")
    is_primary = models.BooleanField(default=False, help_text="¿Es el proveedor principal?")
    last_order_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Producto-Proveedor"
        verbose_name_plural = "Productos-Proveedores"
        unique_together = ['product', 'supplier']
        ordering = ['-is_primary', 'supplier__name']
    
    def __str__(self):
        primary = "⭐ " if self.is_primary else ""
        return f"{primary}{self.product.name} - {self.supplier.name}"
    
    @property
    def profit_margin(self):
        """Margen de ganancia"""
        if self.cost_price > 0:
            return ((self.product.price - self.cost_price) / self.cost_price) * 100
        return 0
    
    @property
    def formatted_profit_margin(self):
        return f"{self.profit_margin:.1f}%"
