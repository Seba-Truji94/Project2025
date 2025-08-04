@echo off
title Galletas Kati - Subir Cambios
color 0A
cls

echo.
echo ================================================================
echo 🍪 GALLETAS KATI - SUBIENDO TODOS LOS CAMBIOS AL REPOSITORIO
echo ================================================================
echo.

rem Cambiar al directorio del proyecto
cd /d "c:\Users\cuent\Galletas Kati"

echo 📁 Directorio actual: %CD%
echo.

echo 📋 1. Verificando estado del repositorio...
git status
echo.

echo 📦 2. Agregando todos los archivos al staging...
git add .
echo.

echo 📊 3. Verificando archivos en staging...
git status --short
echo.

echo 💾 4. Creando commit con todos los cambios...
git commit -m "feat: Sistema completo actualizado

✅ Sistema de notificaciones implementado completamente
✅ Panel administrativo con dropdown menu integrado  
✅ Navbar corregido en TODAS las vistas del sistema
✅ Templates profesionales y responsivos
✅ CSS global para evitar superposicion de contenido
✅ Scripts de verificacion y mantenimiento
✅ Documentacion actualizada

Funcionalidades principales:
- Notificaciones Email/SMS/WhatsApp
- Dashboard administrativo completo
- Gestion de plantillas y usuarios
- Accesos directos en menu dropdown
- Navbar dinamico sin superposicion
- Sistema completamente funcional

URLs del sistema:
- /notifications/ - Panel principal
- /notifications/admin/ - Administracion
- /notifications/admin/templates/ - Plantillas
- /notifications/preferences/ - Preferencias

Autor: GitHub Copilot + Seba-Truji94
Fecha: 4 de Agosto 2025"

echo.

echo 🚀 5. Subiendo cambios al repositorio remoto...
git push origin main

echo.
echo ================================================================
echo 🎉 PROCESO COMPLETADO
echo ================================================================
echo.
echo ✅ Todos los cambios han sido subidos al repositorio
echo 📍 Verifica en: https://github.com/Seba-Truji94/Project2025
echo.
echo 📋 Cambios incluidos:
echo    • Sistema de notificaciones completo
echo    • Panel administrativo integrado
echo    • Navbar corregido globalmente
echo    • Templates y CSS optimizados
echo    • Scripts de mantenimiento
echo    • Documentacion actualizada
echo.
echo ================================================================
pause
