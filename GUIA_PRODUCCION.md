# 🚀 GUÍA COMPLETA PARA PRODUCCIÓN - DULCE BIAS

## 📋 PASOS PARA SUBIR A PRODUCCIÓN

### 1. 🔧 CONFIGURACIÓN DE VARIABLES DE ENTORNO

#### Crear archivo `.env` en producción:
```bash
# Variables obligatorias para producción
SECRET_KEY=tu-secret-key-super-segura-de-50-caracteres-minimo
DEBUG=False
ALLOWED_HOSTS=tudominio.com,www.tudominio.com,tu-ip-servidor

# Base de datos (PostgreSQL recomendado)
DATABASE_URL=postgresql://usuario:contraseña@localhost/dulce_bias_db

# Email para notificaciones
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password

# IPs permitidas para admin
ADMIN_IP_WHITELIST=tu-ip-casa,ip-oficina

# Configuraciones de seguridad
SECURE_SSL_REDIRECT=True
SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https
```

### 2. 🗄️ BASE DE DATOS EN PRODUCCIÓN

#### Opción A: PostgreSQL (Recomendado)
```bash
# Instalar PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib python3-psycopg2

# Crear base de datos
sudo -u postgres createdb dulce_bias_db
sudo -u postgres createuser dulce_bias_user

# Configurar permisos
sudo -u postgres psql
ALTER USER dulce_bias_user PASSWORD 'tu-contraseña-segura';
GRANT ALL PRIVILEGES ON DATABASE dulce_bias_db TO dulce_bias_user;
\q
```

#### Opción B: Mantener SQLite (Para proyectos pequeños)
```bash
# Solo asegurarse de que el archivo db.sqlite3 tenga permisos correctos
chmod 664 db.sqlite3
chown www-data:www-data db.sqlite3
```

### 3. 🐧 SERVIDOR LINUX (Ubuntu/Debian)

#### Instalación de dependencias:
```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python y herramientas
sudo apt install python3 python3-pip python3-venv nginx supervisor git

# Crear usuario para la aplicación
sudo adduser dulce_bias
sudo usermod -aG sudo dulce_bias
```

#### Configurar el proyecto:
```bash
# Cambiar al usuario de la aplicación
sudo su - dulce_bias

# Clonar el proyecto
git clone https://github.com/tu-usuario/dulce-bias.git
cd dulce-bias

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
pip install gunicorn psycopg2-binary

# Configurar variables de entorno
cp .env.example .env
nano .env  # Editar con valores reales
```

### 4. 🔧 CONFIGURACIÓN DE GUNICORN

#### Crear archivo de configuración:
```bash
# /home/dulce_bias/dulce-bias/gunicorn.conf.py
bind = "127.0.0.1:8000"
workers = 3
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
user = "dulce_bias"
group = "dulce_bias"
```

#### Crear script de inicio:
```bash
# /home/dulce_bias/dulce-bias/start_gunicorn.sh
#!/bin/bash
cd /home/dulce_bias/dulce-bias
source venv/bin/activate
exec gunicorn dulce_bias_project.wsgi:application -c gunicorn.conf.py
```

### 5. 🔄 CONFIGURACIÓN DE SUPERVISOR

#### Crear archivo de supervisor:
```bash
# /etc/supervisor/conf.d/dulce_bias.conf
[program:dulce_bias]
command=/home/dulce_bias/dulce-bias/start_gunicorn.sh
directory=/home/dulce_bias/dulce-bias
user=dulce_bias
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/dulce_bias.log
environment=DJANGO_SETTINGS_MODULE=dulce_bias_project.settings
```

### 6. 🌐 CONFIGURACIÓN DE NGINX

#### Configurar servidor web:
```nginx
# /etc/nginx/sites-available/dulce_bias
server {
    listen 80;
    server_name tudominio.com www.tudominio.com;

    # Redireccionar HTTP a HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name tudominio.com www.tudominio.com;

    # Certificados SSL (usar Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/tudominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tudominio.com/privkey.pem;

    # Configuraciones de seguridad SSL
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    add_header Strict-Transport-Security "max-age=31536000" always;

    client_max_body_size 10M;

    location /static/ {
        alias /home/dulce_bias/dulce-bias/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /home/dulce_bias/dulce-bias/media/;
        expires 1y;
        add_header Cache-Control "public";
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

### 7. 🔒 CONFIGURAR HTTPS (Let's Encrypt)

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx

# Obtener certificado SSL
sudo certbot --nginx -d tudominio.com -d www.tudominio.com

# Configurar renovación automática
sudo crontab -e
# Agregar: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 8. 📝 COMANDOS DE DESPLIEGUE

#### Script de despliegue automático:
```bash
#!/bin/bash
# deploy.sh

cd /home/dulce_bias/dulce-bias
source venv/bin/activate

# Obtener últimos cambios
git pull origin main

# Instalar nuevas dependencias
pip install -r requirements.txt

# Aplicar migraciones
python manage.py migrate

# Recopilar archivos estáticos
python manage.py collectstatic --noinput

# Reiniciar aplicación
sudo supervisorctl restart dulce_bias

# Reiniciar nginx
sudo systemctl reload nginx

echo "✅ Despliegue completado"
```

### 9. 🔍 MONITOREO Y LOGS

#### Comandos útiles:
```bash
# Ver logs de la aplicación
sudo tail -f /var/log/dulce_bias.log

# Estado de supervisor
sudo supervisorctl status

# Reiniciar aplicación
sudo supervisorctl restart dulce_bias

# Logs de nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 10. 🛡️ CHECKLIST DE SEGURIDAD FINAL

- [ ] `DEBUG=False` en producción
- [ ] `SECRET_KEY` única y segura
- [ ] Base de datos con contraseñas fuertes
- [ ] HTTPS habilitado
- [ ] Firewall configurado (solo puertos 80, 443, 22)
- [ ] Backups automáticos configurados
- [ ] Logs de seguridad funcionando
- [ ] Rate limiting activado
- [ ] IPs de admin restringidas

### 11. 📊 SERVICIOS EN LA NUBE

#### Opciones recomendadas:

**Opción 1: VPS Tradicional**
- DigitalOcean Droplet ($5-20/mes)
- Linode ($5-20/mes)
- Vultr ($5-20/mes)

**Opción 2: Plataforma como Servicio**
- Heroku (Fácil pero más caro)
- PythonAnywhere (Específico para Python)
- Railway.app (Moderno y simple)

**Opción 3: Contenedores**
- Docker + Docker Compose
- Kubernetes (para proyectos grandes)

### 🚀 COMANDOS RÁPIDOS DE PRODUCCIÓN

```bash
# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Recopilar archivos estáticos
python manage.py collectstatic

# Verificar configuración
python manage.py check --deploy

# Backup de base de datos
python manage.py dumpdata > backup_$(date +%Y%m%d).json
```

---

## 📞 CONTACTO Y SOPORTE

Una vez en producción, el sistema estará disponible 24/7 con todas las funcionalidades:
- 🛒 Carrito de compras funcional
- 💰 Sistema de descuentos
- 📦 Control de inventario
- 👥 Gestión de usuarios
- 📊 Panel administrativo

¡Tu e-commerce "Dulce Bias" estará listo para recibir pedidos reales! 🍪
