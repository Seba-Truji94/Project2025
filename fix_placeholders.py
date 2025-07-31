#!/usr/bin/env python
import os
import re
from pathlib import Path

def replace_placeholders():
    """Reemplazar todos los placeholders externos con locales"""
    
    # Patrón para encontrar URLs de via.placeholder.com
    pattern = r'https://via\.placeholder\.com/(\d+)x(\d+)/([A-Fa-f0-9]+)/([A-Fa-f0-9]+)\?text=([^"\']+)'
    
    # Buscar archivos HTML
    templates_dir = Path('templates')
    html_files = []
    
    for root, dirs, files in os.walk(templates_dir):
        for file in files:
            if file.endswith('.html'):
                html_files.append(Path(root) / file)
    
    replacements_made = 0
    
    for html_file in html_files:
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Función para reemplazar cada coincidencia
            def replace_match(match):
                width, height, bg_color, text_color, text = match.groups()
                # Decodificar URL encoding básico
                text = text.replace('%F0%9F%A5%9C', '🥜')
                text = text.replace('%F0%9F%8D%AA', '🍪')
                text = text.replace('%F0%9F%8D%AF', '🍯')
                text = text.replace('%F0%9F%8D%AB', '🍫')
                text = text.replace('%F0%9F%8C%B0', '🌰')
                
                return f"{{% placeholder_url {width} {height} '{bg_color}' '{text_color}' '{text}' %}}"
            
            # Reemplazar todas las coincidencias
            new_content = re.sub(pattern, replace_match, content)
            
            if new_content != original_content:
                # Verificar si ya tiene el load del template tag
                if '{% load placeholder_tags %}' not in new_content:
                    # Agregar el load después del extends
                    extends_pattern = r'({% extends [^%]+%})'
                    if re.search(extends_pattern, new_content):
                        new_content = re.sub(
                            extends_pattern, 
                            r'\1\n{% load placeholder_tags %}', 
                            new_content
                        )
                
                # Guardar archivo modificado
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                replacements_made += 1
                print(f"✅ Actualizado: {html_file}")
        
        except Exception as e:
            print(f"❌ Error procesando {html_file}: {e}")
    
    print(f"\n🎉 Proceso completado: {replacements_made} archivos actualizados")

if __name__ == "__main__":
    replace_placeholders()
