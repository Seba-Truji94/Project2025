#!/bin/bash

# ==============================================
# SCRIPT DE CONFIGURACIÓN PARA PRODUCCIÓN
# Dulce Bias E-commerce - Galletas Kati
# ==============================================

echo "🚀 Iniciando configuración para producción..."

# Verificar si estamos ejecutando como root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Este script debe ejecutarse como root (sudo)"
    exit 1
fi

# Variables
PROJECT_NAME="dulce-bias"
PROJECT_USER="dulce_bias"
PROJECT_DIR="/home/$PROJECT_USER/$PROJECT_NAME"
DOMAIN="tudominio.com"  # Cambiar por tu dominio real

echo "📋 Configurando para el dominio: $DOMAIN"

# ==============================================
# 1. ACTUALIZAR SISTEMA E INSTALAR DEPENDENCIAS
# ==============================================

echo "📦 Actualizando sistema e instalando dependencias..."
apt update && apt upgrade -y
apt install -y python3 python3-pip python3-venv nginx supervisor git \
               postgresql postgresql-contrib python3-psycopg2 \
               certbot python3-certbot-nginx ufw

# ==============================================
# 2. CREAR USUARIO DEL PROYECTO
# ==============================================

echo "👤 Creando usuario del proyecto..."
if ! id "$PROJECT_USER" &>/dev/null; then
    adduser --disabled-password --gecos "" $PROJECT_USER
    usermod -aG sudo $PROJECT_USER
    echo "✅ Usuario $PROJECT_USER creado"
else
    echo "✅ Usuario $PROJECT_USER ya existe"
fi

# ==============================================
# 3. CONFIGURAR BASE DE DATOS POSTGRESQL
# ==============================================

echo "🗄️ Configurando PostgreSQL..."
sudo -u postgres psql << EOF
CREATE DATABASE dulce_bias_db;
CREATE USER dulce_bias_user WITH PASSWORD 'dulce_bias_pass_2025';
GRANT ALL PRIVILEGES ON DATABASE dulce_bias_db TO dulce_bias_user;
ALTER USER dulce_bias_user CREATEDB;
\q
EOF

echo "✅ Base de datos PostgreSQL configurada"

# ==============================================
# 4. CONFIGURAR FIREWALL
# ==============================================

echo "🛡️ Configurando firewall..."
ufw --force enable
ufw allow ssh
ufw allow 'Nginx Full'
echo "✅ Firewall configurado"

# ==============================================
# 5. CREAR DIRECTORIOS NECESARIOS
# ==============================================

echo "📁 Creando directorios..."
mkdir -p /var/log/dulce-bias
mkdir -p /var/www/dulce-bias/static
mkdir -p /var/www/dulce-bias/media
mkdir -p /home/$PROJECT_USER/backups

# Cambiar permisos
chown -R $PROJECT_USER:$PROJECT_USER /var/www/dulce-bias
chown -R $PROJECT_USER:$PROJECT_USER /var/log/dulce-bias
chown -R $PROJECT_USER:$PROJECT_USER /home/$PROJECT_USER

echo "✅ Directorios creados"

# ==============================================
# 6. CONFIGURAR NGINX
# ==============================================

echo "🌐 Configurando Nginx..."
cat > /etc/nginx/sites-available/$PROJECT_NAME << EOF
# Redirección HTTP a HTTPS
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    return 301 https://\$server_name\$request_uri;
}

# Configuración HTTPS principal
server {
    listen 443 ssl http2;
    server_name $DOMAIN www.$DOMAIN;

    # Certificados SSL (se configurarán con Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;

    # Configuraciones de seguridad SSL
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Headers de seguridad
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-Frame-Options DENY always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Configuraciones generales
    client_max_body_size 10M;
    client_body_timeout 60s;
    client_header_timeout 60s;

    # Archivos estáticos
    location /static/ {
        alias /var/www/dulce-bias/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        add_header Vary Accept-Encoding;
        gzip_static on;
    }

    # Archivos de media
    location /media/ {
        alias /var/www/dulce-bias/media/;
        expires 1y;
        add_header Cache-Control "public";
        add_header Vary Accept-Encoding;
    }

    # Proxy a la aplicación Django
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        proxy_buffering off;
    }

    # Logs específicos
    access_log /var/log/nginx/dulce_bias_access.log;
    error_log /var/log/nginx/dulce_bias_error.log;
}
EOF

# Habilitar el sitio
ln -sf /etc/nginx/sites-available/$PROJECT_NAME /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

echo "✅ Nginx configurado"

# ==============================================
# 7. CONFIGURAR SUPERVISOR PARA GUNICORN
# ==============================================

echo "⚡ Configurando Supervisor..."
cat > /etc/supervisor/conf.d/dulce_bias.conf << EOF
[program:dulce_bias]
command=$PROJECT_DIR/venv/bin/gunicorn dulce_bias_project.wsgi:application
directory=$PROJECT_DIR
user=$PROJECT_USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/dulce-bias/gunicorn.log
stderr_logfile=/var/log/dulce-bias/gunicorn_error.log
environment=DJANGO_SETTINGS_MODULE=dulce_bias_project.settings

[program:dulce_bias_worker]
command=$PROJECT_DIR/venv/bin/python manage.py runserver 127.0.0.1:8000
directory=$PROJECT_DIR
user=$PROJECT_USER
autostart=false
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/dulce-bias/django.log
EOF

systemctl enable supervisor
systemctl start supervisor

echo "✅ Supervisor configurado"

# ==============================================
# 8. CREAR SCRIPTS DE UTILIDAD
# ==============================================

echo "📝 Creando scripts de utilidad..."

# Script de backup
cat > /home/$PROJECT_USER/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/home/dulce_bias/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup de base de datos
pg_dump -U dulce_bias_user -h localhost dulce_bias_db > "$BACKUP_DIR/db_backup_$DATE.sql"

# Backup de archivos media
tar -czf "$BACKUP_DIR/media_backup_$DATE.tar.gz" /var/www/dulce-bias/media/

# Limpiar backups antiguos (más de 30 días)
find "$BACKUP_DIR" -type f -mtime +30 -delete

echo "✅ Backup completado: $DATE"
EOF

# Script de despliegue
cat > /home/$PROJECT_USER/deploy.sh << 'EOF'
#!/bin/bash
cd /home/dulce_bias/dulce-bias

echo "🚀 Iniciando despliegue..."

# Activar entorno virtual
source venv/bin/activate

# Obtener últimos cambios
git pull origin main

# Instalar/actualizar dependencias
pip install -r requirements.txt

# Aplicar migraciones
python manage.py migrate

# Recopilar archivos estáticos
python manage.py collectstatic --noinput

# Reiniciar aplicación
sudo supervisorctl restart dulce_bias

# Recargar nginx
sudo systemctl reload nginx

echo "✅ Despliegue completado"
EOF

# Script de monitoreo
cat > /home/$PROJECT_USER/monitor.sh << 'EOF'
#!/bin/bash
echo "📊 Estado del sistema Dulce Bias"
echo "================================"

echo "🌐 Estado de Nginx:"
systemctl is-active nginx

echo "⚡ Estado de Supervisor:"
supervisorctl status

echo "🗄️ Estado de PostgreSQL:"
systemctl is-active postgresql

echo "🔒 Estado del Firewall:"
ufw status

echo "💾 Espacio en disco:"
df -h / | tail -1 | awk '{print "Usado: "$3" / "$2" ("$5")"}'

echo "🔍 Últimas líneas del log de aplicación:"
tail -n 5 /var/log/dulce-bias/gunicorn.log
EOF

# Hacer scripts ejecutables
chmod +x /home/$PROJECT_USER/*.sh
chown $PROJECT_USER:$PROJECT_USER /home/$PROJECT_USER/*.sh

echo "✅ Scripts de utilidad creados"

# ==============================================
# 9. CONFIGURAR CRON PARA BACKUPS AUTOMÁTICOS
# ==============================================

echo "⏰ Configurando backups automáticos..."
(crontab -u $PROJECT_USER -l 2>/dev/null; echo "0 2 * * * /home/$PROJECT_USER/backup.sh") | crontab -u $PROJECT_USER -

echo "✅ Backups automáticos configurados (diarios a las 2:00 AM)"

# ==============================================
# 10. MOSTRAR INFORMACIÓN FINAL
# ==============================================

echo ""
echo "🎉 ¡CONFIGURACIÓN COMPLETADA!"
echo "=============================="
echo ""
echo "📍 Próximos pasos:"
echo "1. Clonar tu proyecto en: $PROJECT_DIR"
echo "2. Configurar el archivo .env con datos reales"
echo "3. Obtener certificado SSL: sudo certbot --nginx -d $DOMAIN"
echo "4. Ejecutar el script de despliegue: /home/$PROJECT_USER/deploy.sh"
echo ""
echo "📂 Ubicaciones importantes:"
echo "- Proyecto: $PROJECT_DIR"
echo "- Logs: /var/log/dulce-bias/"
echo "- Backups: /home/$PROJECT_USER/backups/"
echo "- Nginx config: /etc/nginx/sites-available/$PROJECT_NAME"
echo ""
echo "🔧 Comandos útiles:"
echo "- Ver logs: sudo tail -f /var/log/dulce-bias/gunicorn.log"
echo "- Reiniciar app: sudo supervisorctl restart dulce_bias"
echo "- Deploy: sudo -u $PROJECT_USER /home/$PROJECT_USER/deploy.sh"
echo "- Backup: sudo -u $PROJECT_USER /home/$PROJECT_USER/backup.sh"
echo "- Monitor: sudo -u $PROJECT_USER /home/$PROJECT_USER/monitor.sh"
echo ""
echo "🔐 Credenciales de BD:"
echo "- Base de datos: dulce_bias_db"
echo "- Usuario: dulce_bias_user"
echo "- Contraseña: dulce_bias_pass_2025"
echo ""
echo "⚠️  IMPORTANTE: Cambia la contraseña de la BD antes de poner en producción"
echo ""
