# 🚀 SCRIPT RÁPIDO PARA RAILWAY

# ==============================================
# EJECUTA ESTOS COMANDOS EN POWERSHELL
# ==============================================

Write-Host "🚀 Preparando proyecto para Railway..." -ForegroundColor Green

# Navegar al directorio del proyecto
Set-Location "c:\Users\cuent\Galletas Kati"

# Verificar que estamos en la carpeta correcta
if (!(Test-Path "manage.py")) {
    Write-Host "❌ Error: No se encontró manage.py. Verifica la ruta." -ForegroundColor Red
    exit 1
}

Write-Host "✅ Directorio correcto encontrado" -ForegroundColor Green

# Verificar estado de Git
Write-Host "📋 Verificando estado de Git..." -ForegroundColor Yellow
git status

# Agregar todos los archivos nuevos
Write-Host "📤 Agregando archivos al repositorio..." -ForegroundColor Yellow
git add .

# Confirmar cambios
Write-Host "💾 Confirmando cambios..." -ForegroundColor Yellow
git commit -m "🚀 Configurado para Railway - Listo para producción

- Agregado railway.json
- Configurado start.sh para Railway  
- Agregado nixpacks.toml
- Configurado WhiteNoise para archivos estáticos
- Agregado soporte para PostgreSQL con dj-database-url
- Variables de entorno para Railway configuradas"

# Subir a GitHub
Write-Host "🌐 Subiendo a GitHub..." -ForegroundColor Yellow
git push origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ ¡Código subido exitosamente a GitHub!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🎯 PRÓXIMOS PASOS:" -ForegroundColor Cyan
    Write-Host "=================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. 🌐 Ve a https://railway.app" -ForegroundColor White
    Write-Host "2. 🔑 Inicia sesión con GitHub" -ForegroundColor White
    Write-Host "3. ➕ Clic en 'New Project'" -ForegroundColor White  
    Write-Host "4. 📂 Selecciona 'Deploy from GitHub repo'" -ForegroundColor White
    Write-Host "5. 🔍 Busca y selecciona 'Project2025'" -ForegroundColor White
    Write-Host "6. 🗄️ Agrega PostgreSQL database" -ForegroundColor White
    Write-Host "7. ⚙️ Configura variables de entorno" -ForegroundColor White
    Write-Host ""
    Write-Host "📋 VARIABLES DE ENTORNO NECESARIAS:" -ForegroundColor Yellow
    Write-Host "====================================" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "DEBUG=False" -ForegroundColor Gray
    Write-Host "SECRET_KEY=genera-una-clave-nueva-de-50-caracteres" -ForegroundColor Gray
    Write-Host "ALLOWED_HOSTS=*.railway.app,*.up.railway.app" -ForegroundColor Gray
    Write-Host "USE_WHITENOISE=True" -ForegroundColor Gray
    Write-Host "EMAIL_HOST_USER=tu-email@gmail.com" -ForegroundColor Gray
    Write-Host "EMAIL_HOST_PASSWORD=tu-app-password" -ForegroundColor Gray
    Write-Host ""
    Write-Host "🔑 Para generar SECRET_KEY ejecuta:" -ForegroundColor Magenta
    Write-Host "python -c `"import secrets; print(secrets.token_urlsafe(50))`"" -ForegroundColor Gray
    Write-Host ""
    Write-Host "📖 Guía completa en: RAILWAY_DEPLOY.md" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "🎉 Una vez configurado, tu e-commerce estará en:" -ForegroundColor Green
    Write-Host "https://tu-proyecto.up.railway.app" -ForegroundColor White
    Write-Host ""
    Write-Host "👤 Usuario admin: SebaAdmin / admin123" -ForegroundColor Yellow
} else {
    Write-Host "❌ Error al subir a GitHub. Verifica tu conexión." -ForegroundColor Red
    Write-Host "💡 Intenta: git push origin main" -ForegroundColor Yellow
}
