#!/bin/bash

# ==============================================
# SCRIPT DE DESPLIEGUE RÁPIDO
# Dulce Bias - Deploy to Production
# ==============================================

set -e  # Detener si hay errores

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar mensajes
show_message() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

show_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠️  $1${NC}"
}

show_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ❌ $1${NC}"
}

# Variables
PROJECT_DIR="/home/dulce_bias/dulce-bias"
BACKUP_DIR="/home/dulce_bias/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# ==============================================
# VERIFICACIONES PREVIAS
# ==============================================

show_message "🔍 Verificando configuración del sistema..."

# Verificar que estamos en el directorio correcto
if [ ! -d "$PROJECT_DIR" ]; then
    show_error "Directorio del proyecto no encontrado: $PROJECT_DIR"
    exit 1
fi

cd "$PROJECT_DIR"

# Verificar que existe el entorno virtual
if [ ! -d "venv" ]; then
    show_error "Entorno virtual no encontrado. Ejecuta: python3 -m venv venv"
    exit 1
fi

# Verificar archivo .env
if [ ! -f ".env" ]; then
    show_warning "Archivo .env no encontrado. Usando configuración por defecto."
fi

# ==============================================
# BACKUP ANTES DE DESPLEGAR
# ==============================================

show_message "💾 Creando backup antes del despliegue..."

# Crear directorio de backup si no existe
mkdir -p "$BACKUP_DIR"

# Backup de base de datos
if command -v pg_dump &> /dev/null; then
    show_message "📊 Creando backup de PostgreSQL..."
    pg_dump -U dulce_bias_user -h localhost dulce_bias_db > "$BACKUP_DIR/db_backup_$DATE.sql"
else
    show_message "📊 Creando backup de SQLite..."
    cp db.sqlite3 "$BACKUP_DIR/db_backup_$DATE.sqlite3" 2>/dev/null || true
fi

# Backup de archivos media
if [ -d "media" ]; then
    show_message "🖼️ Creando backup de archivos media..."
    tar -czf "$BACKUP_DIR/media_backup_$DATE.tar.gz" media/
fi

show_message "✅ Backup completado en: $BACKUP_DIR"

# ==============================================
# OBTENER ÚLTIMOS CAMBIOS
# ==============================================

show_message "📥 Obteniendo últimos cambios del repositorio..."

# Verificar si es un repositorio git
if [ -d ".git" ]; then
    # Guardar cambios locales si existen
    if ! git diff-index --quiet HEAD --; then
        show_warning "Se encontraron cambios locales no confirmados"
        git stash push -m "Deploy backup $DATE"
    fi
    
    # Obtener cambios del repositorio
    git pull origin main || git pull origin master
else
    show_warning "No es un repositorio git. Saltando actualización de código."
fi

# ==============================================
# CONFIGURAR ENTORNO VIRTUAL
# ==============================================

show_message "🐍 Configurando entorno virtual..."

# Activar entorno virtual
source venv/bin/activate

# Actualizar pip
pip install --upgrade pip

# Instalar/actualizar dependencias
show_message "📦 Instalando dependencias..."
pip install -r requirements.txt

# Instalar Gunicorn si no está
pip show gunicorn &> /dev/null || pip install gunicorn

# ==============================================
# MIGRACIONES DE BASE DE DATOS
# ==============================================

show_message "🗄️ Aplicando migraciones de base de datos..."

# Verificar estado de migraciones
python manage.py showmigrations

# Crear migraciones si hay cambios
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# ==============================================
# RECOPILAR ARCHIVOS ESTÁTICOS
# ==============================================

show_message "📁 Recopilando archivos estáticos..."

# Crear directorio si no existe
mkdir -p /var/www/dulce-bias/static

# Recopilar archivos estáticos
python manage.py collectstatic --noinput

# ==============================================
# VERIFICACIONES DE SEGURIDAD
# ==============================================

show_message "🛡️ Ejecutando verificaciones de seguridad..."

# Verificar configuración de Django
python manage.py check --deploy

# Verificar configuración de archivos estáticos
if [ ! -d "/var/www/dulce-bias/static" ]; then
    show_error "Directorio de archivos estáticos no encontrado"
    exit 1
fi

# ==============================================
# CREAR/ACTUALIZAR SUPERUSUARIO ADMIN
# ==============================================

show_message "👤 Verificando usuario administrador..."

# Script para crear superusuario si no existe
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()

# Verificar si existe el usuario admin
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

# ==============================================
# REINICIAR SERVICIOS
# ==============================================

show_message "🔄 Reiniciando servicios..."

# Reiniciar aplicación con Supervisor
if command -v supervisorctl &> /dev/null; then
    show_message "⚡ Reiniciando aplicación (Supervisor)..."
    sudo supervisorctl restart dulce_bias
    sudo supervisorctl status dulce_bias
else
    show_warning "Supervisor no encontrado. Reinicio manual requerido."
fi

# Recargar Nginx
if command -v nginx &> /dev/null; then
    show_message "🌐 Recargando Nginx..."
    sudo nginx -t && sudo systemctl reload nginx
    sudo systemctl status nginx --no-pager -l
else
    show_warning "Nginx no encontrado."
fi

# ==============================================
# VERIFICACIONES POST-DESPLIEGUE
# ==============================================

show_message "✅ Ejecutando verificaciones post-despliegue..."

# Verificar que la aplicación responde
sleep 5  # Esperar a que se inicie

if curl -f -s http://127.0.0.1:8000 > /dev/null; then
    show_message "✅ Aplicación respondiendo correctamente en puerto 8000"
else
    show_error "❌ Aplicación no responde en puerto 8000"
fi

# Verificar logs recientes
if [ -f "/var/log/dulce-bias/gunicorn.log" ]; then
    show_message "📋 Últimas líneas del log:"
    tail -n 5 "/var/log/dulce-bias/gunicorn.log"
fi

# ==============================================
# LIMPIAR BACKUPS ANTIGUOS
# ==============================================

show_message "🧹 Limpiando backups antiguos (más de 30 días)..."
find "$BACKUP_DIR" -type f -mtime +30 -delete 2>/dev/null || true

# ==============================================
# RESUMEN FINAL
# ==============================================

show_message "🎉 ¡DESPLIEGUE COMPLETADO EXITOSAMENTE!"
echo ""
echo "📊 Resumen del despliegue:"
echo "=========================="
echo "📅 Fecha: $(date)"
echo "📂 Proyecto: $PROJECT_DIR"
echo "💾 Backup: $BACKUP_DIR/db_backup_$DATE.*"
echo "🌐 URL: http://tudominio.com"
echo "👤 Admin: SebaAdmin / admin123"
echo ""
echo "🔧 Comandos útiles:"
echo "- Ver logs: sudo tail -f /var/log/dulce-bias/gunicorn.log"
echo "- Estado servicios: sudo supervisorctl status"
echo "- Reiniciar app: sudo supervisorctl restart dulce_bias"
echo "- Monitor sistema: /home/dulce_bias/monitor.sh"
echo ""
echo "✅ Sistema listo para recibir pedidos reales 🍪"
