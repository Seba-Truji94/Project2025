import os
import re

print("🔧 Aplicando correcciones del navbar a todas las vistas...")

# Directorio base del proyecto
base_dir = r"c:\Users\cuent\Galletas Kati"

# Plantilla CSS para agregar a cada vista que extiende base.html
navbar_fix_css = """{% block extra_css %}
{{ block.super }}
<style>
    /* Fix para evitar que el navbar tape contenido */
    .container:first-child,
    .container-fluid:first-child {
        margin-top: 40px !important;
        padding-top: 20px !important;
    }
    
    .page-header,
    .content-header,
    h1:first-of-type,
    .card:first-child {
        margin-top: 30px !important;
    }
</style>
{% endblock %}"""

def process_template(file_path):
    """Procesar un template HTML"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Solo procesar archivos que extienden base.html
        if "{% extends 'base.html' %}" not in content:
            return False
        
        # Verificar si ya tiene el fix
        if "Fix para evitar que el navbar tape contenido" in content:
            return False
        
        # Buscar si ya tiene un bloque extra_css
        if "{% block extra_css %}" in content:
            # Agregar solo el CSS dentro del bloque existente
            css_addition = """    /* Fix para evitar que el navbar tape contenido */
    .container:first-child,
    .container-fluid:first-child {
        margin-top: 40px !important;
        padding-top: 20px !important;
    }
    
    .page-header,
    .content-header,
    h1:first-of-type,
    .card:first-child {
        margin-top: 30px !important;
    }"""
            
            # Buscar el lugar donde agregar el CSS
            if "<style>" in content:
                # Agregar después del <style> existente
                content = content.replace("<style>", f"<style>\n{css_addition}\n")
            else:
                # Agregar antes del {% endblock %}
                content = content.replace("{% endblock %}", f"<style>\n{css_addition}\n</style>\n{% endblock %}")
        
        else:
            # Agregar el bloque completo después del {% block title %}
            title_pattern = r"({% block title %}.*?{% endblock %})"
            if re.search(title_pattern, content, re.DOTALL):
                content = re.sub(title_pattern, r"\1\n\n" + navbar_fix_css, content, flags=re.DOTALL)
            else:
                # Si no hay block title, agregar después de extends
                extends_pattern = r"({% extends ['\"]base\.html['\"] %})"
                content = re.sub(extends_pattern, r"\1\n\n" + navbar_fix_css, content)
        
        # Escribir el archivo modificado
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
        
    except Exception as e:
        print(f"Error procesando {file_path}: {e}")
        return False

# Buscar todos los archivos HTML
html_files = []
for root, dirs, files in os.walk(base_dir):
    for file in files:
        if file.endswith('.html'):
            html_files.append(os.path.join(root, file))

# Filtrar solo templates que extienden base.html
templates_to_fix = []
for file_path in html_files:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if "{% extends 'base.html' %}" in content:
            templates_to_fix.append(file_path)
    except:
        continue

print(f"Encontrados {len(templates_to_fix)} templates que extienden base.html")

# Procesar cada template
fixed_count = 0
for template_path in templates_to_fix:
    relative_path = template_path.replace(base_dir, "").replace("\\", "/")
    if process_template(template_path):
        print(f"✅ Corregido: {relative_path}")
        fixed_count += 1
    else:
        print(f"⏭️  Ya corregido o no necesita fix: {relative_path}")

print(f"\n🎉 Proceso completado!")
print(f"📊 Templates procesados: {len(templates_to_fix)}")
print(f"✅ Templates corregidos: {fixed_count}")
print(f"⏭️  Templates que no necesitaban corrección: {len(templates_to_fix) - fixed_count}")

print(f"\n🌐 Ahora todas las vistas del sistema tienen la corrección del navbar aplicada.")
print(f"💡 El navbar ya no debería tapar títulos ni acciones importantes en ninguna vista.")
