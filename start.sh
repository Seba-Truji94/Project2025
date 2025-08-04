#!/bin/bash

# Script de inicio para Railway
# Este archivo se ejecuta automáticamente cuando Railway despliega tu app

echo "🚀 Iniciando aplicación en Railway..."

# Aplicar migraciones
echo "📊 Aplicando migraciones de base de datos..."
python manage.py migrate --noinput

# Crear superusuario si no existe
echo "👤 Configurando usuario administrador..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()

if not User.objects.filter(username='SebaAdmin').exists():
    print('Creando usuario administrador...')
    User.objects.create_superuser(
        username='SebaAdmin',
        email='sebastian.f.trujilloescobar@gmail.com',
        password='admin123'
    )
    print('✅ Usuario administrador creado')
else:
    print('✅ Usuario administrador ya existe')
EOF

# Recopilar archivos estáticos
echo "📁 Recopilando archivos estáticos..."
python manage.py collectstatic --noinput

# Verificar configuración
echo "🔍 Verificando configuración..."
python manage.py check --deploy

echo "✅ Configuración completada. Iniciando servidor..."

# Iniciar servidor con Gunicorn
exec gunicorn dulce_bias_project.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 2 \
    --worker-class sync \
    --worker-connections 1000 \
    --max-requests 1000 \
    --timeout 30 \
    --keep-alive 2 \
    --log-level info \
    --access-logfile - \
    --error-logfile -
