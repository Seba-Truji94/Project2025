# 🚀 GUÍA COMPLETA PARA DESPLEGAR EN RAILWAY

## 🌐 ¿Qué es Railway?

Railway es una plataforma moderna de hosting que hace el despliegue súper simple. No necesitas configurar servidores, todo es automático.

**Ventajas de Railway:**
- ✅ Despliegue automático desde Git
- ✅ PostgreSQL incluido gratis
- ✅ HTTPS automático
- ✅ Escalado automático
- ✅ $5/mes (plan Hobby)
- ✅ No necesitas configurar servidores

---

## 📋 PASOS PARA DESPLEGAR

### 1. 🔧 PREPARAR EL REPOSITORIO

Tu proyecto ya está preparado con estos archivos:
- ✅ `railway.json` - Configuración de Railway
- ✅ `start.sh` - Script de inicio
- ✅ `nixpacks.toml` - Configuración de build
- ✅ `.env.railway` - Variables de entorno
- ✅ `requirements.txt` - Actualizado con dependencias

### 2. 📤 SUBIR CÓDIGO A GITHUB

```bash
# En tu computadora (Windows PowerShell)
cd "c:\Users\cuent\Galletas Kati"

# Agregar todos los archivos
git add .

# Confirmar cambios
git commit -m "🚀 Preparado para Railway - Producción lista"

# Subir a GitHub
git push origin main
```

### 3. 🌐 CREAR CUENTA EN RAILWAY

1. Ve a [railway.app](https://railway.app)
2. Haz clic en "Start a New Project"
3. Conecta con tu cuenta de GitHub
4. Autoriza Railway para acceder a tus repositorios

### 4. 🚀 DESPLEGAR EL PROYECTO

#### Paso 4.1: Crear nuevo proyecto
1. En Railway, clic en "New Project"
2. Selecciona "Deploy from GitHub repo"
3. Busca y selecciona tu repositorio "Project2025"
4. Railway detectará automáticamente que es Django

#### Paso 4.2: Agregar base de datos
1. En tu proyecto, clic en "Add Service"
2. Selecciona "Database" → "PostgreSQL"
3. Railway creará automáticamente la base de datos
4. La variable `DATABASE_URL` se configurará sola

### 5. ⚙️ CONFIGURAR VARIABLES DE ENTORNO

En el dashboard de Railway, ve a tu servicio web → Variables → Raw Editor y pega:

```bash
DEBUG=False
SECRET_KEY=genera-una-clave-super-secreta-aqui-de-50-caracteres
ALLOWED_HOSTS=*.railway.app,*.up.railway.app
USE_WHITENOISE=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password-gmail
RATE_LIMIT_LOGIN=5/m
SECURE_SSL_REDIRECT=True
SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https
```

**IMPORTANTE**: Genera una SECRET_KEY nueva:
```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

### 6. 🔄 REINICIAR DESPLIEGUE

1. Guarda las variables
2. Ve a "Deployments"
3. Clic en "Redeploy"
4. Espera 2-3 minutos

### 7. ✅ VERIFICAR DESPLIEGUE

1. Ve a "Settings" → "Domains"
2. Copia la URL (algo como: `https://tu-proyecto.up.railway.app`)
3. Abre la URL en tu navegador
4. ¡Tu e-commerce debería estar funcionando!

---

## 🔐 CONFIGURAR USUARIO ADMINISTRADOR

Después del primer despliegue, necesitas configurar el usuario admin:

### Opción 1: Railway CLI (Recomendado)

1. Instala Railway CLI:
```bash
npm install -g @railway/cli
```

2. Login y conecta a tu proyecto:
```bash
railway login
railway link
```

3. Crear superusuario:
```bash
railway run python manage.py createsuperuser
```

### Opción 2: Usar el código automático

El código ya incluye creación automática del usuario:
- **Usuario**: `SebaAdmin`
- **Email**: `sebastian.f.trujilloescobar@gmail.com`
- **Contraseña**: `admin123`

---

## 🌐 CONFIGURAR DOMINIO PERSONALIZADO

### 1. En Railway (Opcional)
1. Ve a "Settings" → "Domains"
2. Clic "Add Domain"
3. Ingresa tu dominio: `galletaskati.com`
4. Railway te dará instrucciones DNS

### 2. En tu proveedor de dominio
1. Agregar registro CNAME:
   - Nombre: `www`
   - Valor: `tu-proyecto.up.railway.app`
2. Agregar registro A:
   - Nombre: `@`
   - Valor: IP que te dé Railway

---

## 📊 MONITOREO Y LOGS

### Ver logs en tiempo real:
```bash
railway logs
```

### Ver métricas:
1. Dashboard → Tu proyecto
2. Pestaña "Metrics"
3. Ver CPU, memoria, requests

### Ver base de datos:
1. Dashboard → PostgreSQL service
2. "Data" tab
3. Query browser incluido

---

## 💰 COSTOS DE RAILWAY

### Plan Hobby ($5/USD mes):
- ✅ 512 MB RAM
- ✅ 1 GB storage
- ✅ PostgreSQL incluido
- ✅ $5/mes total (no por servicio)
- ✅ HTTPS automático
- ✅ Dominio personalizado

### Plan Pro ($20/USD mes):
- ✅ 8 GB RAM
- ✅ 100 GB storage
- ✅ Mejor rendimiento

**Para empezar**: Plan Hobby es más que suficiente

---

## 🔧 COMANDOS ÚTILES

### Ejecutar comandos en Railway:
```bash
# Migraciones
railway run python manage.py migrate

# Crear superusuario
railway run python manage.py createsuperuser

# Shell de Django
railway run python manage.py shell

# Ver archivos
railway run ls -la

# Backup de BD
railway run python manage.py dumpdata > backup.json
```

### Actualizaciones automáticas:
Cada vez que hagas `git push`, Railway automáticamente:
1. Descarga el código nuevo
2. Instala dependencias
3. Ejecuta migraciones
4. Reinicia la aplicación

---

## 🚨 TROUBLESHOOTING

### Error 500 - Internal Server Error:
1. Verificar logs: `railway logs`
2. Verificar variables de entorno
3. Verificar SECRET_KEY configurada

### Base de datos no conecta:
1. Verificar que PostgreSQL esté agregado
2. Variable `DATABASE_URL` debe existir automáticamente

### Archivos estáticos no cargan:
1. Verificar `USE_WHITENOISE=True`
2. Verificar que `whitenoise` esté en requirements.txt

### Email no funciona:
1. Configurar `EMAIL_HOST_USER` y `EMAIL_HOST_PASSWORD`
2. Usar App Password de Gmail (no contraseña normal)

---

## ✅ CHECKLIST FINAL

- [ ] ✅ Código subido a GitHub
- [ ] ✅ Proyecto creado en Railway
- [ ] ✅ PostgreSQL agregado
- [ ] ✅ Variables de entorno configuradas
- [ ] ✅ SECRET_KEY generada y configurada
- [ ] ✅ Despliegue completado
- [ ] ✅ URL funcionando
- [ ] ✅ Admin panel accesible
- [ ] ✅ Productos visibles
- [ ] ✅ Carrito funcionando
- [ ] ✅ Registro de usuarios funciona

---

## 🎉 RESULTADO FINAL

**URL de tu e-commerce**: `https://tu-proyecto.up.railway.app`  
**Panel admin**: `https://tu-proyecto.up.railway.app/admin/`  
**Usuario admin**: `SebaAdmin` / `admin123`

### Funcionalidades listas:
✅ Catálogo de productos  
✅ Carrito de compras  
✅ Sistema de usuarios  
✅ Panel administrativo  
✅ Descuentos y promociones  
✅ Control de inventario  
✅ Gestión de pedidos  

---

## 📞 SOPORTE

### Si tienes problemas:
1. Revisa los logs: `railway logs`
2. Verifica variables de entorno
3. Consulta [docs.railway.app](https://docs.railway.app)

### Para actualizaciones:
1. Modifica código localmente
2. `git add . && git commit -m "mensaje"`
3. `git push origin main`
4. Railway se actualiza automáticamente

---

**🍪 ¡Tu negocio de galletas ya está online en Railway!**

**Próximo paso**: Configurar dominio personalizado y empezar a recibir pedidos reales.
