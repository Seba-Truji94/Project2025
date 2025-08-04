@echo off
chcp 65001 >nul
echo 🍪 GALLETAS KATI - SUBIENDO CAMBIOS
echo ================================================================
cd /d "c:\Users\cuent\Galletas Kati"

echo 📋 Estado actual del repositorio:
git status

echo.
echo 📦 Agregando todos los archivos...
git add -A

echo.
echo 📊 Archivos preparados para commit:
git status --porcelain

echo.
echo 💾 Creando commit...
git commit -m "feat: Sistema de notificaciones completo y navbar fixes - Implementacion completa con templates, panel admin, CSS global y correcciones navbar en todas las vistas"

echo.
echo 🚀 Subiendo cambios a GitHub...
git push origin main

echo.
echo ================================================================
echo 🎉 PROCESO COMPLETADO
echo ================================================================
echo.
echo 📍 Verifica tu repositorio en:
echo    https://github.com/Seba-Truji94/Project2025
echo.
echo ✅ El sistema de notificaciones completo ya esta en GitHub
echo ================================================================
pause
