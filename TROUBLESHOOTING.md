## Guía de Solución de Errores de Comunicación con el Servidor

### Error: "Error en la comunicación con el servidor"

Este error puede ocurrir por varias razones. Sigue estos pasos para solucionarlo:

### 1. Verificar que el Servidor Django esté ejecutándose

```bash
cd "c:\Users\cuent\Galletas Kati"
python manage.py runserver
```

El servidor debe mostrar:
```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
[Fecha] - Django version 4.2.20, using settings 'dulce_bias_project.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

### 2. Verificar que las URLs estén accesibles

Abre tu navegador y verifica estas URLs:
- http://127.0.0.1:8000/ (Página principal)
- http://127.0.0.1:8000/productos/ (Lista de productos)
- http://127.0.0.1:8000/cart/ (Carrito)

### 3. Verificar la Consola del Navegador

1. Presiona F12 para abrir las herramientas de desarrollador
2. Ve a la pestaña "Console"
3. Intenta agregar un producto al carrito
4. Busca mensajes de error que incluyan:
   - "URL solicitada:"
   - "Headers enviados:"
   - "Error HTTP detectado:"
   - "Error de JSON detectado:"
   - "Error de conexión detectado:"

### 4. Verificar la Pestaña Network

1. En las herramientas de desarrollador, ve a "Network"
2. Intenta agregar un producto al carrito
3. Busca la petición a `/cart/add/[ID]/`
4. Verifica:
   - Status Code (debe ser 200)
   - Response (debe ser JSON válido)
   - Headers de la petición

### 5. Errores Comunes y Soluciones

#### Error 404 - URL no encontrada
- Verifica que las URLs en `cart/urls.py` estén correctas
- Verifica que `cart` esté incluido en `dulce_bias_project/urls.py`

#### Error 403 - CSRF
- Verifica que el token CSRF esté presente en la página
- Verifica que se esté enviando en el header X-CSRFToken

#### Error 500 - Error interno del servidor
- Revisa los logs de Django en la terminal
- Verifica que no haya errores en `cart/views.py`

#### Error de JSON
- El servidor está devolviendo HTML en lugar de JSON
- Verifica que la vista esté devolviendo JsonResponse
- Verifica que no haya errores que causen redirecciones

### 6. Sistema de Verificación de Conectividad

El sistema ahora incluye:
- Indicador visual de conectividad (esquina superior derecha)
- Verificación automática cada 30 segundos
- Peticiones AJAX seguras con verificación previa

### 7. Logs Detallados

Revisa la consola del navegador para logs detallados que incluyen:
- URL de la petición
- Headers enviados
- Tipo específico de error
- Sugerencias de solución

### 8. Comando de Diagnóstico Rápido

Ejecuta estos comandos para verificar el estado del proyecto:

```bash
cd "c:\Users\cuent\Galletas Kati"
python manage.py check
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py runserver
```
