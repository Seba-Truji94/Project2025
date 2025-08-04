# Scripts y Herramientas de Desarrollo

Este directorio contiene scripts auxiliares y herramientas de desarrollo para el proyecto Galletas Kati.

## Estructura

### `debug/`
Scripts de diagnóstico y debugging:
- `test_*.py` - Scripts de testing manual
- `debug_*.py` - Scripts de debugging del carrito y funcionalidades
- `analyze_*.py` - Scripts de análisis de datos
- `diagnose_*.py` - Scripts de diagnóstico del sistema
- `verify_*.py` - Scripts de verificación de configuración
- `validate_*.py` - Scripts de validación
- `fix_*.py` - Scripts de corrección automática

### `setup/`
Scripts de configuración e inicialización:
- `setup_*.py` - Scripts de configuración del sistema
- `populate_*.py` - Scripts para poblar la base de datos

## Uso

Estos scripts están diseñados para ejecutarse desde el directorio raíz del proyecto:

```bash
cd "c:\Users\cuent\Galletas Kati"
python scripts/setup/populate_db.py
python scripts/debug/test_cart_views.py
```

## Nota

Los archivos en este directorio utilizan `print()` statements para output de debugging y no siguen las convenciones de logging del proyecto principal. Esto es intencional para facilitar el debugging manual.
