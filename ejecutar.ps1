Write-Host "=== GALLETAS KATI - DIAGNÓSTICO Y CORRECCIÓN ===" -ForegroundColor Green
Write-Host ""

Set-Location "c:\Users\cuent\Galletas Kati"

Write-Host "1. Verificando archivos..." -ForegroundColor Yellow
if (Test-Path "manage.py") {
    Write-Host "✅ manage.py encontrado" -ForegroundColor Green
} else {
    Write-Host "❌ manage.py NO encontrado" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "2. Ejecutando diagnóstico..." -ForegroundColor Yellow
python test_simple.py

Write-Host ""
Write-Host "3. Ejecutando migraciones..." -ForegroundColor Yellow
python manage.py makemigrations notifications
python manage.py migrate

Write-Host ""
Write-Host "4. Iniciando servidor..." -ForegroundColor Yellow
Write-Host "🚀 Servidor iniciando en http://127.0.0.1:8002" -ForegroundColor Green
python manage.py runserver 8002
