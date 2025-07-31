from django.http import HttpResponse
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_GET
import io
from PIL import Image, ImageDraw, ImageFont
from urllib.parse import parse_qs


@require_GET
@cache_control(max_age=3600)  # Cache por 1 hora
def placeholder_image(request, width, height):
    """Generar imagen placeholder localmente"""
    try:
        # Parámetros por defecto
        bg_color = request.GET.get('bg', 'A0522D')  # Color de fondo por defecto
        text_color = request.GET.get('color', 'ffffff')  # Color de texto por defecto
        text = request.GET.get('text', '🍪')  # Texto por defecto
        
        # Validar dimensiones
        width = min(max(int(width), 10), 800)  # Entre 10 y 800 px
        height = min(max(int(height), 10), 800)  # Entre 10 y 800 px
        
        # Convertir colores hex
        try:
            bg_color = tuple(int(bg_color[i:i+2], 16) for i in (0, 2, 4))
        except:
            bg_color = (160, 82, 45)  # Color por defecto si hay error
            
        try:
            text_color = tuple(int(text_color[i:i+2], 16) for i in (0, 2, 4))
        except:
            text_color = (255, 255, 255)  # Blanco por defecto
        
        # Crear imagen
        image = Image.new('RGB', (width, height), bg_color)
        draw = ImageDraw.Draw(image)
        
        # Calcular tamaño de fuente dinámico
        font_size = min(width, height) // 3
        
        try:
            # Intentar usar una fuente del sistema
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            try:
                # Intentar fuente alternativa
                font = ImageFont.load_default()
            except:
                # Si no hay fuentes disponibles, usar fuente por defecto
                font = None
        
        # Calcular posición centrada del texto
        if font:
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        else:
            # Estimación sin fuente
            text_width = len(text) * (font_size // 2)
            text_height = font_size
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        # Dibujar texto
        draw.text((x, y), text, fill=text_color, font=font)
        
        # Guardar imagen en memoria
        img_io = io.BytesIO()
        image.save(img_io, format='PNG', optimize=True)
        img_io.seek(0)
        
        response = HttpResponse(img_io.getvalue(), content_type='image/png')
        response['Cache-Control'] = 'public, max-age=3600'
        return response
        
    except Exception as e:
        # En caso de error, devolver imagen simple
        return simple_placeholder(width, height)


def simple_placeholder(width, height):
    """Imagen placeholder simple sin dependencias externas"""
    # SVG simple
    svg_content = f'''
    <svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
        <rect width="100%" height="100%" fill="#A0522D"/>
        <text x="50%" y="50%" text-anchor="middle" dy=".3em" 
              font-family="Arial, sans-serif" font-size="{min(width, height)//3}" 
              fill="white">🍪</text>
    </svg>
    '''
    
    response = HttpResponse(svg_content, content_type='image/svg+xml')
    response['Cache-Control'] = 'public, max-age=3600'
    return response
