# Imagen base de Python
FROM python:3.11-slim

# Metadatos
LABEL maintainer="Dulce Bias - Galletas Kati"
LABEL description="E-commerce para Galletas Kati - Dulce Bias"

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=dulce_bias_project.settings

# Crear directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        gcc \
        python3-dev \
        libpq-dev \
        curl \
        && rm -rf /var/lib/apt/lists/*

# Crear usuario no-root para seguridad
RUN addgroup --system django \
    && adduser --system --ingroup django django

# Copiar requirements y instalar dependencias de Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install gunicorn psycopg2-binary

# Copiar el proyecto
COPY . /app/

# Crear directorios necesarios
RUN mkdir -p /app/staticfiles /app/media /app/logs \
    && chown -R django:django /app

# Cambiar al usuario no-root
USER django

# Recopilar archivos estáticos
RUN python manage.py collectstatic --noinput

# Healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Exponer puerto
EXPOSE 8000

# Comando por defecto
CMD ["gunicorn", "dulce_bias_project.wsgi:application", "-c", "gunicorn.conf.py"]
