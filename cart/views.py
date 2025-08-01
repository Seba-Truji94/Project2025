from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json

from shop.models import Product
from .models import Cart, CartItem, SessionCart


class CartDetailView(TemplateView):
    template_name = 'cart/cart_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.user.is_authenticated:
            # Carrito de usuario autenticado
            cart, created = Cart.objects.get_or_create(user=self.request.user)
            
            # Limpiar items con productos no disponibles o eliminados
            self.clean_invalid_cart_items(cart)
            
            context['cart'] = cart
            context['cart_items'] = cart.items.all()
            context['is_authenticated_cart'] = True
            
            # Productos recomendados (excluir los que ya están en el carrito)
            cart_product_ids = cart.items.values_list('product_id', flat=True)
            recommended_products = Product.objects.filter(available=True).exclude(id__in=cart_product_ids)[:4]
        else:
            # Carrito de sesión para usuarios no autenticados
            session_cart = SessionCart(self.request)
            context['session_cart'] = session_cart
            context['cart_items'] = list(session_cart)
            context['is_authenticated_cart'] = False
            
            # Calcular totales para carrito de sesión
            total_price = session_cart.get_total_price()
            shipping_cost = 0 if total_price >= 15000 else 3000
            context['cart_totals'] = {
                'total_price': total_price,
                'shipping_cost': shipping_cost,
                'final_total': total_price + shipping_cost,
                'total_items': len(session_cart)
            }
            
            # Productos recomendados (excluir los que ya están en el carrito de sesión)
            cart_product_ids = [item['product'].id for item in session_cart]
            recommended_products = Product.objects.filter(available=True).exclude(id__in=cart_product_ids)[:4]
        
        # Siempre incluir productos recomendados
        context['recommended_products'] = recommended_products
        return context
    
    def clean_invalid_cart_items(self, cart):
        """Limpiar items del carrito que tienen productos no disponibles o eliminados"""
        invalid_items = []
        
        for item in cart.items.all():
            try:
                product = item.product
                # Verificar si el producto existe y está disponible
                if not Product.objects.filter(id=product.id, available=True).exists():
                    invalid_items.append(item)
            except Product.DoesNotExist:
                invalid_items.append(item)
        
        # Eliminar items inválidos silenciosamente
        if invalid_items:
            for item in invalid_items:
                item.delete()
            
            # Log para debugging sin mostrar mensaje al usuario
            # Se eliminaron items no disponibles silenciosamente para evitar recargas


class MyCartView(TemplateView):
    """Vista unificada del carrito integrada con el perfil de usuario"""
    template_name = 'cart/my_cart.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.user.is_authenticated:
            # Carrito de usuario autenticado
            cart, created = Cart.objects.get_or_create(user=self.request.user)
            
            # Limpiar items con productos no disponibles o eliminados
            self.clean_invalid_cart_items(cart)
            
            context['cart'] = cart
            context['cart_items'] = cart.items.all()
            context['is_authenticated_cart'] = True
            
            # Calcular cantidad faltante para envío gratis
            missing_for_free_shipping = max(0, 15000 - cart.total_price) if cart.total_price < 15000 else 0
            context['missing_for_free_shipping'] = missing_for_free_shipping
            
            # Productos recomendados (excluir los que ya están en el carrito)
            cart_product_ids = cart.items.values_list('product_id', flat=True)
            recommended_products = Product.objects.filter(available=True).exclude(id__in=cart_product_ids)[:4]
        else:
            # Carrito de sesión para usuarios no autenticados
            session_cart = SessionCart(self.request)
            context['session_cart'] = session_cart
            context['cart_items'] = list(session_cart)
            context['is_authenticated_cart'] = False
            
            # Calcular totales para carrito de sesión
            total_price = session_cart.get_total_price()
            shipping_cost = 0 if total_price >= 15000 else 3000
            missing_for_free_shipping = max(0, 15000 - total_price) if total_price < 15000 else 0
            context['cart_totals'] = {
                'total_price': total_price,
                'shipping_cost': shipping_cost,
                'final_total': total_price + shipping_cost,
                'total_items': len(session_cart),
                'missing_for_free_shipping': missing_for_free_shipping
            }
            
            # Productos recomendados (excluir los que ya están en el carrito de sesión)
            cart_product_ids = [item['product'].id for item in session_cart]
            recommended_products = Product.objects.filter(available=True).exclude(id__in=cart_product_ids)[:4]
        
        # Siempre incluir productos recomendados
        context['recommended_products'] = recommended_products
        return context
    
    def clean_invalid_cart_items(self, cart):
        """Limpiar items del carrito que tienen productos no disponibles o eliminados"""
        invalid_items = []
        
        for item in cart.items.all():
            try:
                product = item.product
                # Verificar si el producto existe y está disponible
                if not Product.objects.filter(id=product.id, available=True).exists():
                    invalid_items.append(item)
            except Product.DoesNotExist:
                invalid_items.append(item)
        
        # Eliminar items inválidos silenciosamente
        if invalid_items:
            for item in invalid_items:
                item.delete()


@require_POST
def add_to_cart(request, product_id):
    """Agregar producto al carrito"""
    try:
        product = get_object_or_404(Product, id=product_id)
        quantity = int(request.POST.get('quantity', 1))
        
        # Validar que el producto esté disponible
        if not product.available:
            messages.error(request, f'❌ {product.name} no está disponible')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': f'{product.name} no está disponible'
                })
            return redirect('shop:product_detail', slug=product.slug)
        
        # Validar stock disponible
        if product.stock < quantity:
            if product.stock == 0:
                message = f'❌ {product.name} está agotado'
            else:
                message = f'❌ Solo quedan {product.stock} unidades de {product.name}'
            
            messages.error(request, message)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': message
                })
            return redirect('shop:product_detail', slug=product.slug)
    
        if request.user.is_authenticated:
            # Usuario autenticado - usar carrito en BD
            cart, created = Cart.objects.get_or_create(user=request.user)
            cart_item, item_created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity}
            )
            
            if not item_created:
                # Validar que la nueva cantidad no exceda el stock
                new_quantity = cart_item.quantity + quantity
                if new_quantity > product.stock:
                    available_to_add = product.stock - cart_item.quantity
                    if available_to_add <= 0:
                        message = f'❌ Ya tienes el máximo disponible de {product.name} en tu carrito'
                    else:
                        message = f'❌ Solo puedes agregar {available_to_add} unidades más de {product.name}'
                    
                    messages.error(request, message)
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': False,
                            'message': message
                        })
                    return redirect('cart:cart_detail')
                
                cart_item.quantity = new_quantity
                cart_item.save()
            
            messages.success(
                request, 
                f'✅ {product.name} agregado al carrito (Cantidad: {cart_item.quantity})'
            )
            
            # Respuesta AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'{product.name} agregado al carrito',
                    'cart_count': cart.total_items,
                    'cart_total_items': cart.total_items,
                    'cart_total_price': cart.formatted_total_price,
                    'cart_final_total': cart.formatted_final_total,
                    # Información del producto para el modal
                    'product': {
                        'id': product.id,
                        'name': product.name,
                        'price': product.formatted_current_price,
                        'image_url': product.image.url if product.image else '',
                        'slug': product.slug,
                        'quantity_added': quantity,
                        'total_quantity_in_cart': cart_item.quantity
                    }
                })
        else:
            # Usuario no autenticado - usar carrito de sesión
            session_cart = SessionCart(request)
            session_cart.add(product=product, quantity=quantity)
            
            messages.success(
                request, 
                f'✅ {product.name} agregado al carrito'
            )
            
            # Respuesta AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Recalcular totales con precios actuales
                total_price = session_cart.get_total_price()
                shipping_cost = 0 if total_price >= 15000 else 3000
                final_total = total_price + shipping_cost
                
                return JsonResponse({
                    'success': True,
                    'message': f'{product.name} agregado al carrito',
                    'cart_count': len(session_cart),
                    'cart_total_items': len(session_cart),
                    'cart_total_price': f"${int(total_price):,}".replace(',', '.'),
                    'cart_final_total': f"${int(final_total):,}".replace(',', '.'),
                    # Información del producto para el modal
                    'product': {
                        'id': product.id,
                        'name': product.name,
                        'price': product.formatted_current_price,
                        'image_url': product.image.url if product.image else '',
                        'slug': product.slug,
                        'quantity_added': quantity,
                        'total_quantity_in_cart': session_cart.cart.get(str(product.id), {}).get('quantity', 0)
                    }
                })
        
        # Respuesta AJAX para carrito de sesión
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            total_price = session_cart.get_total_price()
            shipping_cost = 0 if total_price >= 15000 else 3000
            final_total = total_price + shipping_cost
            
            return JsonResponse({
                'success': True,
                'message': f'{product.name} agregado al carrito',
                'cart_total_items': len(session_cart),
                'cart_total_price': f"${int(total_price):,}".replace(',', '.'),
                'cart_final_total': f"${int(final_total):,}".replace(',', '.'),
                # Información del producto para el modal
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'price': product.formatted_current_price,
                    'image_url': product.image.url if product.image else '',
                    'slug': product.slug,
                    'quantity_added': quantity,
                    'total_quantity_in_cart': session_cart.cart.get(str(product.id), {}).get('quantity', 0)
                }
            })
    
        return redirect('cart:cart_detail')

    except Exception as e:
        # Manejo de errores generales
        error_message = f'Error al agregar producto al carrito: {str(e)}'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'Error interno del servidor. Por favor, intenta nuevamente.'
            }, status=500)
        else:
            messages.error(request, error_message)
            return redirect('shop:product_list')


@require_POST
def remove_from_cart(request, product_id):
    """Eliminar producto del carrito"""
    product = get_object_or_404(Product, id=product_id)
    
    if request.user.is_authenticated:
        # Usuario autenticado
        try:
            cart = Cart.objects.get(user=request.user)
            cart_item = CartItem.objects.get(cart=cart, product=product)
            cart_item.delete()
            
            messages.success(request, f'❌ {product.name} eliminado del carrito')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'{product.name} eliminado del carrito',
                    'cart_total_items': cart.total_items,
                    'cart_total_price': cart.formatted_total_price
                })
        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            messages.error(request, 'El producto no está en tu carrito')
    else:
        # Usuario no autenticado
        session_cart = SessionCart(request)
        session_cart.remove(product)
        
        messages.success(request, f'❌ {product.name} eliminado del carrito')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            total_price = session_cart.get_total_price()
            return JsonResponse({
                'success': True,
                'message': f'{product.name} eliminado del carrito',
                'cart_total_items': len(session_cart),
                'cart_total_price': f"${int(total_price):,}".replace(',', '.')
            })
    
    return redirect('cart:cart_detail')


@require_POST
def update_cart(request, product_id):
    """Actualizar cantidad de producto en el carrito"""
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity <= 0:
        return remove_from_cart(request, product_id)
    
    if request.user.is_authenticated:
        # Usuario autenticado
        try:
            cart = Cart.objects.get(user=request.user)
            cart_item = CartItem.objects.get(cart=cart, product=product)
            cart_item.quantity = quantity
            cart_item.save()
            
            messages.success(request, f'🔄 Cantidad actualizada: {quantity} x {product.name}')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Cantidad actualizada',
                    'item_total': cart_item.formatted_total_price,
                    'cart_total_items': cart.total_items,
                    'cart_total_price': cart.formatted_total_price,
                    'cart_final_total': cart.formatted_final_total
                })
        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            messages.error(request, 'El producto no está en tu carrito')
    else:
        # Usuario no autenticado
        session_cart = SessionCart(request)
        session_cart.add(product=product, quantity=quantity, override_quantity=True)
        
        messages.success(request, f'🔄 Cantidad actualizada: {quantity} x {product.name}')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            total_price = session_cart.get_total_price()
            shipping_cost = 0 if total_price >= 15000 else 3000
            final_total = total_price + shipping_cost
            
            return JsonResponse({
                'success': True,
                'message': 'Cantidad actualizada',
                'cart_total_items': len(session_cart),
                'cart_total_price': f"${int(total_price):,}".replace(',', '.'),
                'cart_final_total': f"${int(final_total):,}".replace(',', '.')
            })
    
    return redirect('cart:cart_detail')


def clear_cart(request):
    """Vaciar carrito completamente"""
    if request.user.is_authenticated:
        # Usuario autenticado
        try:
            cart = Cart.objects.get(user=request.user)
            cart.items.all().delete()
            messages.success(request, '🗑️ Carrito vaciado')
        except Cart.DoesNotExist:
            messages.info(request, 'Tu carrito ya está vacío')
    else:
        # Usuario no autenticado
        session_cart = SessionCart(request)
        session_cart.clear()
        messages.success(request, '🗑️ Carrito vaciado')
    
    return redirect('cart:cart_detail')


@login_required
def checkout(request):
    """Vista de checkout - procesar el pedido"""
    try:
        cart = Cart.objects.get(user=request.user)
        if not cart.items.exists():
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Tu carrito está vacío'
                })
            messages.error(request, 'Tu carrito está vacío')
            return redirect('cart:cart_detail')
        
        if request.method == 'POST':
            # Importar aquí para evitar imports circulares
            from orders.models import Order, OrderItem
            
            # Obtener datos del formulario
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            email = request.POST.get('email', '').strip()
            phone = request.POST.get('phone', '').strip()
            address = request.POST.get('address', '').strip()
            city = request.POST.get('city', '').strip()
            region = request.POST.get('region', '').strip()
            postal_code = request.POST.get('postal_code', '').strip()
            delivery_notes = request.POST.get('delivery_notes', '').strip()
            payment_method = request.POST.get('payment_method', 'webpay')
            
            # Validar campos requeridos
            required_fields = {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'phone': phone,
                'address': address,
                'city': city,
                'region': region,
            }
            
            missing_fields = [field for field, value in required_fields.items() if not value]
            if missing_fields:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': 'Por favor completa todos los campos requeridos'
                    })
                messages.error(request, 'Por favor completa todos los campos requeridos')
                return render(request, 'cart/checkout.html', {
                    'cart': cart,
                    'cart_items': cart.items.all()
                })
            
            # Crear el pedido
            order = Order.objects.create(
                user=request.user,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                address=address,
                city=city,
                region=region,
                postal_code=postal_code,
                notes=delivery_notes,
                subtotal=cart.total_price,
                shipping_cost=cart.shipping_cost,
                total=cart.final_total,
                payment_method=payment_method,
                status='pending'
            )
            
            # Crear los items del pedido
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
            
            # Vaciar el carrito
            cart.items.all().delete()
            
            # Redirigir según método de pago
            if payment_method == 'transfer':
                # Para transferencia, redirigir al proceso de pago
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    from django.urls import reverse
                    return JsonResponse({
                        'success': True,
                        'message': f'¡Pedido #{order.order_number} creado exitosamente! Ahora procede con el pago por transferencia.',
                        'redirect_url': reverse('orders:transfer_payment', kwargs={'order_number': order.order_number})
                    })
                
                messages.success(
                    request, 
                    f'🎉 ¡Pedido #{order.order_number} creado exitosamente! '
                    f'Ahora procede con el pago por transferencia bancaria.'
                )
                
                return redirect('orders:transfer_payment', order_number=order.order_number)
            else:
                # Para otros métodos de pago (webpay, etc.)
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': f'¡Pedido #{order.order_number} creado exitosamente!',
                        'redirect_url': f'/orders/{order.order_number}/'
                    })
                
                messages.success(
                    request, 
                    f'🎉 ¡Pedido #{order.order_number} creado exitosamente!'
                )
                
                return redirect('orders:order_detail', order_number=order.order_number)
        
        # GET request - mostrar formulario
        return render(request, 'cart/checkout.html', {
            'cart': cart,
            'cart_items': cart.items.all()
        })
        
    except Cart.DoesNotExist:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'No tienes productos en tu carrito'
            })
        messages.error(request, 'No tienes productos en tu carrito')
        return redirect('shop:product_list')
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': f'Error al procesar el pedido: {str(e)}'
            })
        messages.error(request, f'Error al procesar el pedido: {str(e)}')
        return redirect('cart:cart_detail')


def migrate_session_cart(request):
    """Migrar carrito de sesión a carrito de usuario cuando se autentica"""
    if request.user.is_authenticated:
        session_cart = SessionCart(request)
        if len(session_cart) > 0:
            cart, created = Cart.objects.get_or_create(user=request.user)
            
            # Migrar items del carrito de sesión
            for item in session_cart:
                product = item['product']
                quantity = item['quantity']
                
                cart_item, item_created = CartItem.objects.get_or_create(
                    cart=cart,
                    product=product,
                    defaults={'quantity': quantity}
                )
                
                if not item_created:
                    cart_item.quantity += quantity
                    cart_item.save()
            
            # Limpiar carrito de sesión
            session_cart.clear()
            
            messages.info(request, f'📦 Productos del carrito sincronizados ({cart.total_items} items)')


# Vista AJAX para obtener contenido del carrito
def cart_summary(request):
    """Obtener resumen del carrito para modal/dropdown"""
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            items = []
            for item in cart.items.all()[:5]:  # Mostrar solo los primeros 5
                items.append({
                    'id': item.product.id,
                    'name': item.product.name,
                    'quantity': item.quantity,
                    'price': f"${int(item.product.price):,}".replace(',', '.'),
                    'total': item.formatted_total_price,
                    'image': item.product.image.url if item.product.image else None
                })
            
            return JsonResponse({
                'success': True,
                'items': items,
                'total_items': cart.total_items,
                'total_price': cart.formatted_total_price,
                'shipping_cost': cart.formatted_shipping_cost,
                'final_total': cart.formatted_final_total,
                'has_more': cart.items.count() > 5
            })
        except Cart.DoesNotExist:
            return JsonResponse({
                'success': True,
                'items': [],
                'total_items': 0,
                'total_price': '$0',
                'final_total': '$0'
            })
    else:
        # Carrito de sesión
        session_cart = SessionCart(request)
        items = []
        for item in list(session_cart)[:5]:
            items.append({
                'id': item['product'].id,
                'name': item['product'].name,
                'quantity': item['quantity'],
                'price': f"${int(item['price']):,}".replace(',', '.'),
                'total': f"${int(item['total_price']):,}".replace(',', '.'),
                'image': item['product'].image.url if item['product'].image else None
            })
        
        total_price = session_cart.get_total_price()
        shipping_cost = 0 if total_price >= 15000 else 3000
        final_total = total_price + shipping_cost
        
        return JsonResponse({
            'success': True,
            'items': items,
            'total_items': len(session_cart),
            'total_price': f"${int(total_price):,}".replace(',', '.'),
            'shipping_cost': "GRATIS" if shipping_cost == 0 else f"${shipping_cost:,}".replace(',', '.'),
            'final_total': f"${int(final_total):,}".replace(',', '.'),
            'has_more': len(session_cart) > 5
        })
