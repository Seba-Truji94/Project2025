from django.db import models
from django.contrib.auth.models import User
from shop.models import Product
from decimal import Decimal


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    coupon = models.ForeignKey(
        'shop.DiscountCoupon', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='carts'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Carrito de {self.user.username}"
    
    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())
    
    @property
    def total_price(self):
        return sum(item.get_total_price() for item in self.items.all())
    
    @property
    def discount_amount(self):
        """Calcula el monto de descuento aplicado por el cupón"""
        if not self.coupon or not self.coupon.is_valid:
            return Decimal('0')
        
        subtotal = self.total_price
        
        # Verificar monto mínimo
        if subtotal < self.coupon.minimum_order_amount:
            return Decimal('0')
        
        # Calcular descuento según el tipo
        if self.coupon.discount_type == 'percentage':
            discount = subtotal * (self.coupon.discount_value / Decimal('100'))
            # Aplicar límite máximo si existe
            if self.coupon.maximum_discount_amount:
                discount = min(discount, self.coupon.maximum_discount_amount)
        elif self.coupon.discount_type == 'fixed_amount':
            discount = self.coupon.discount_value
        else:  # free_shipping
            discount = Decimal('0')  # El descuento se aplica al envío
        
        # No puede ser mayor al subtotal
        return min(discount, subtotal)
    
    @property
    def subtotal_after_discount(self):
        """Subtotal después de aplicar el descuento del cupón"""
        return self.total_price - self.discount_amount
    
    @property
    def formatted_discount_amount(self):
        discount = self.discount_amount
        if discount > 0:
            return f"-${int(discount):,}".replace(',', '.')
        return "$0"
    
    @property
    def formatted_total_price(self):
        total = self.total_price
        return f"${int(total):,}".replace(',', '.')
    
    @property
    def shipping_cost(self):
        """Envío gratis para compras mayores a $15,000 o con cupón de envío gratis"""
        # Si hay cupón de envío gratis
        if self.coupon and self.coupon.is_valid and self.coupon.discount_type == 'free_shipping':
            # Verificar monto mínimo del cupón
            if self.total_price >= self.coupon.minimum_order_amount:
                return 0
        
        # Envío gratis para compras mayores a $15,000
        if self.total_price >= 15000:
            return 0
        return 3000  # Costo de envío estándar
    
    @property
    def formatted_shipping_cost(self):
        if self.shipping_cost == 0:
            return "GRATIS"
        return f"${int(self.shipping_cost):,}".replace(',', '.')
    
    @property
    def final_total(self):
        return self.subtotal_after_discount + self.shipping_cost
    
    @property
    def formatted_final_total(self):
        total = self.final_total
        return f"${int(total):,}".replace(',', '.')
    
    def apply_coupon(self, coupon_code):
        """Aplica un cupón al carrito"""
        from shop.models import DiscountCoupon
        
        try:
            coupon = DiscountCoupon.objects.get(code=coupon_code.upper(), is_active=True)
            
            # Verificar validez del cupón
            if not coupon.is_valid:
                return False, "El cupón ha expirado o no está disponible"
            
            # Verificar monto mínimo
            if self.total_price < coupon.minimum_order_amount:
                return False, f"El monto mínimo para este cupón es ${int(coupon.minimum_order_amount):,}"
            
            # Verificar si ya se alcanzó el límite de usos
            if coupon.max_uses and coupon.current_uses >= coupon.max_uses:
                return False, "Este cupón ya no está disponible"
            
            # Aplicar cupón
            self.coupon = coupon
            self.save()
            
            return True, f"Cupón '{coupon.code}' aplicado exitosamente"
            
        except DiscountCoupon.DoesNotExist:
            return False, "El código de cupón no es válido"
    
    def remove_coupon(self):
        """Remueve el cupón del carrito"""
        self.coupon = None
        self.save()
        return True, "Cupón removido exitosamente"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('cart', 'product')
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
    def get_total_price(self):
        return self.product.current_price * self.quantity
    
    @property
    def formatted_total_price(self):
        total = self.get_total_price()
        return f"${int(total):,}".replace(',', '.')


# Para manejar carritos de usuarios no autenticados (sesiones)
class SessionCart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart
    
    def add(self, product, quantity=1, override_quantity=False):
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(product.current_price)}
        
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        
        # Actualizar precio en caso de que haya cambiado (usar current_price)
        self.cart[product_id]['price'] = str(product.current_price)
        
        self.save()
    
    def save(self):
        self.session.modified = True
    
    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()
    
    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())
    
    def clear(self):
        del self.session['cart']
        self.save()
    
    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()
        
        for product in products:
            cart[str(product.id)]['product'] = product
        
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item
    
    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())
