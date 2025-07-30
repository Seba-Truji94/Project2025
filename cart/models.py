from django.db import models
from django.contrib.auth.models import User
from shop.models import Product
from decimal import Decimal


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
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
    def formatted_total_price(self):
        total = self.total_price
        return f"${int(total):,}".replace(',', '.')
    
    @property
    def shipping_cost(self):
        """Envío gratis para compras mayores a $15,000"""
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
        return self.total_price + self.shipping_cost
    
    @property
    def formatted_final_total(self):
        total = self.final_total
        return f"${int(total):,}".replace(',', '.')


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
        return self.product.price * self.quantity
    
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
            self.cart[product_id] = {'quantity': 0, 'price': str(product.price)}
        
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        
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
