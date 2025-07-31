from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from shop.models import Product
import uuid


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('confirmed', 'Confirmado'),
        ('processing', 'En Preparación'),
        ('shipped', 'Enviado'),
        ('delivered', 'Entregado'),
        ('cancelled', 'Cancelado'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('paid', 'Pagado'),
        ('failed', 'Fallido'),
        ('refunded', 'Reembolsado'),
    ]
    
    REGION_CHOICES = [
        ('rm', 'Región Metropolitana'),
        ('v', 'V Región - Valparaíso'),
        ('viii', 'VIII Región - Biobío'),
        ('iv', 'IV Región - Coquimbo'),
        ('other', 'Otra Región'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('webpay', 'Webpay Plus'),
        ('transfer', 'Transferencia Bancaria'),
        ('cash', 'Pago contra entrega'),
    ]
    
    # Información básica del pedido
    order_number = models.CharField(max_length=20, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Información de entrega
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=250)
    city = models.CharField(max_length=100)
    region = models.CharField(max_length=10, choices=REGION_CHOICES)
    postal_code = models.CharField(max_length=10, blank=True)
    
    # Información de pago
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='webpay')
    
    # Precios
    subtotal = models.DecimalField(max_digits=10, decimal_places=0)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=0)
    
    # Fechas
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    # Notas adicionales
    notes = models.TextField(blank=True, help_text="Notas especiales para el pedido")
    tracking_number = models.CharField(max_length=100, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Pedido #{self.order_number}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generar número de pedido único
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)
    
    def generate_order_number(self):
        """Genera un número de pedido único"""
        import datetime
        today = datetime.date.today()
        # Formato: DB-YYYYMMDD-XXXX
        prefix = f"DB-{today.strftime('%Y%m%d')}"
        
        # Buscar el último pedido del día
        last_order = Order.objects.filter(
            order_number__startswith=prefix
        ).order_by('-order_number').first()
        
        if last_order:
            last_number = int(last_order.order_number.split('-')[-1])
            new_number = last_number + 1
        else:
            new_number = 1
        
        return f"{prefix}-{new_number:04d}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def formatted_subtotal(self):
        return f"${int(self.subtotal):,}".replace(',', '.')
    
    @property
    def formatted_shipping_cost(self):
        if self.shipping_cost == 0:
            return "GRATIS"
        return f"${int(self.shipping_cost):,}".replace(',', '.')
    
    @property
    def formatted_total(self):
        return f"${int(self.total):,}".replace(',', '.')
    
    def can_be_cancelled(self, user=None):
        """
        Verifica si el pedido puede ser cancelado por el usuario dado.
        
        Reglas:
        - Pedidos ya cancelados o entregados no se pueden cancelar
        - Pedidos no pagados en estado pendiente pueden ser cancelados por el usuario
        - Pedidos pagados solo pueden ser cancelados por superusuarios
        """
        if self.status in ['cancelled', 'delivered']:
            return False
            
        if user and user.is_superuser:
            return True
            
        # Usuario normal solo puede cancelar si no está pagado y está pendiente
        return self.payment_status != 'paid' and self.status == 'pending'
    
    @property
    def can_be_cancelled_simple(self):
        """Versión simple para templates sin usuario"""
        return self.status in ['pending', 'confirmed']
    
    @property
    def is_delivered(self):
        return self.status == 'delivered'
    
    def get_total_items(self):
        return sum(item.quantity for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=0)  # Precio al momento de la compra
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
    def get_total_price(self):
        return self.price * self.quantity
    
    @property
    def formatted_price(self):
        return f"${int(self.price):,}".replace(',', '.')
    
    @property
    def formatted_total_price(self):
        total = self.get_total_price()
        return f"${int(total):,}".replace(',', '.')


class OrderStatusHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES)
    changed_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-changed_at']
        verbose_name_plural = 'Order Status Histories'
    
    def __str__(self):
        return f"{self.order.order_number} - {self.get_status_display()}"


class BankAccount(models.Model):
    """Cuentas bancarias para recibir transferencias"""
    bank_name = models.CharField(max_length=100, verbose_name="Nombre del Banco")
    account_type = models.CharField(
        max_length=20, 
        choices=[
            ('checking', 'Cuenta Corriente'),
            ('savings', 'Cuenta de Ahorros'),
            ('vista', 'Cuenta Vista')
        ],
        default='checking',
        verbose_name="Tipo de Cuenta"
    )
    account_number = models.CharField(max_length=20, verbose_name="Número de Cuenta")
    account_holder = models.CharField(max_length=100, verbose_name="Titular de la Cuenta")
    rut = models.CharField(max_length=12, verbose_name="RUT del Titular")
    email_notification = models.EmailField(verbose_name="Email para Notificaciones")
    is_active = models.BooleanField(default=True, verbose_name="Cuenta Activa")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Cuenta Bancaria"
        verbose_name_plural = "Cuentas Bancarias"
        ordering = ['bank_name', 'account_number']
    
    def __str__(self):
        return f"{self.bank_name} - {self.account_number} ({self.account_holder})"


class TransferPayment(models.Model):
    """Pagos por transferencia bancaria"""
    TRANSFER_STATUS_CHOICES = [
        ('pending', 'Pendiente de Verificación'),
        ('verified', 'Verificado y Aprobado'),
        ('rejected', 'Rechazado'),
        ('expired', 'Expirado'),
    ]
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='transfer_payment')
    bank_account = models.ForeignKey(BankAccount, on_delete=models.CASCADE, verbose_name="Cuenta de Destino")
    
    # Información del comprobante
    transfer_amount = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="Monto Transferido")
    transfer_date = models.DateTimeField(verbose_name="Fecha de Transferencia")
    reference_number = models.CharField(max_length=50, verbose_name="Número de Referencia/Comprobante")
    sender_name = models.CharField(max_length=100, verbose_name="Nombre del Emisor")
    sender_rut = models.CharField(max_length=12, verbose_name="RUT del Emisor")
    sender_bank = models.CharField(max_length=100, verbose_name="Banco Emisor")
    
    # Comprobante de transferencia
    receipt_image = models.ImageField(
        upload_to='transfer_receipts/%Y/%m/%d/',
        verbose_name="Comprobante de Transferencia",
        help_text="Sube una imagen del comprobante de transferencia"
    )
    
    # Estado y verificación
    status = models.CharField(max_length=20, choices=TRANSFER_STATUS_CHOICES, default='pending')
    verification_notes = models.TextField(blank=True, verbose_name="Notas de Verificación")
    verified_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Verificado por"
    )
    verified_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Verificación")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Pago por Transferencia"
        verbose_name_plural = "Pagos por Transferencia"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Transferencia {self.order.order_number} - {self.get_status_display()}"
    
    def save(self, *args, **kwargs):
        # Si se verifica el pago, actualizar el pedido
        if self.status == 'verified' and self.order.payment_status == 'pending':
            self.order.payment_status = 'paid'
            self.order.status = 'confirmed'
            self.order.save()
            self.verified_at = timezone.now()
        elif self.status == 'rejected' and self.order.payment_status == 'pending':
            self.order.payment_status = 'failed'
            self.order.save()
        
        super().save(*args, **kwargs)
