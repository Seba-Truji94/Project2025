# Configuración de Gunicorn para producción
# /home/dulce_bias/dulce-bias/gunicorn.conf.py

import multiprocessing
import os

# Configuración del servidor
bind = "127.0.0.1:8000"
backlog = 2048

# Configuración de workers
workers = min(4, (multiprocessing.cpu_count() * 2) + 1)
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2

# Configuración de procesos
preload_app = True
daemon = False
pidfile = "/tmp/gunicorn_dulce_bias.pid"

# Usuario y grupo
user = "dulce_bias"
group = "dulce_bias"

# Configuración de logging
loglevel = "info"
accesslog = "/var/log/dulce-bias/gunicorn_access.log"
errorlog = "/var/log/dulce-bias/gunicorn_error.log"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Configuración de seguridad
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Hooks para manejo de procesos
def on_starting(server):
    server.log.info("🚀 Dulce Bias - Iniciando servidor Gunicorn")

def on_reload(server):
    server.log.info("🔄 Dulce Bias - Recargando configuración")

def worker_int(worker):
    worker.log.info("💀 Worker recibió SIGINT o SIGQUIT")

def pre_fork(server, worker):
    server.log.info(f"👶 Worker {worker.pid} iniciando")

def post_fork(server, worker):
    server.log.info(f"✅ Worker {worker.pid} iniciado correctamente")

def worker_abort(worker):
    worker.log.info(f"💥 Worker {worker.pid} abortado")

# Variables de entorno
raw_env = [
    'DJANGO_SETTINGS_MODULE=dulce_bias_project.settings',
    'PYTHONPATH=/home/dulce_bias/dulce-bias',
]

# Configuración específica para Django
def when_ready(server):
    server.log.info("🎉 Dulce Bias - Servidor listo para recibir requests")
    server.log.info(f"👥 Configurado con {workers} workers")
    server.log.info(f"🔗 Escuchando en {bind}")

# Configuración de SSL si se usa
# ssl_version = 2  # SSL v2
# certfile = "/path/to/cert.pem"
# keyfile = "/path/to/key.pem"
