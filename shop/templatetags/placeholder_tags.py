from django import template
from django.urls import reverse
from urllib.parse import urlencode

register = template.Library()


@register.simple_tag
def placeholder_url(width, height, bg_color='A0522D', text_color='ffffff', text='🍪'):
    """
    Generar URL para imagen placeholder local
    
    Uso: {% placeholder_url 60 60 'A0522D' 'ffffff' '🥜' %}
    """
    base_url = reverse('shop:placeholder', kwargs={'width': width, 'height': height})
    
    params = {}
    if bg_color != 'A0522D':
        params['bg'] = bg_color
    if text_color != 'ffffff':
        params['color'] = text_color
    if text != '🍪':
        params['text'] = text
    
    if params:
        return f"{base_url}?{urlencode(params)}"
    return base_url


@register.filter
def placeholder_for_product(product, size='120x120'):
    """
    Generar placeholder específico para un producto
    
    Uso: {{ product|placeholder_for_product:"60x60" }}
    """
    try:
        width, height = map(int, size.split('x'))
    except:
        width, height = 120, 120
    
    # Determinar emoji y color basado en la categoría o nombre del producto
    if hasattr(product, 'category') and product.category:
        category_name = product.category.name.lower()
        if 'chocolate' in category_name:
            return placeholder_url(width, height, '8B4513', 'ffffff', '🍫')
        elif 'miel' in category_name or 'honey' in category_name:
            return placeholder_url(width, height, 'CD853F', 'ffffff', '🍯')
        elif 'nuez' in category_name or 'nut' in category_name:
            return placeholder_url(width, height, 'A0522D', 'ffffff', '🥜')
        elif 'galleta' in category_name or 'cookie' in category_name:
            return placeholder_url(width, height, 'D2691E', 'ffffff', '🍪')
    
    # Placeholder genérico
    return placeholder_url(width, height, 'A0522D', 'ffffff', '🍪')
