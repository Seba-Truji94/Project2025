@echo off
echo 🍪 GALLETAS KATI - SUBIENDO TODOS LOS CAMBIOS
echo ================================================================
cd /d "c:\Users\cuent\Galletas Kati"

echo 📋 Verificando estado actual...
git status

echo.
echo 📦 Agregando todos los archivos...
git add -A

echo.
echo 📊 Verificando archivos agregados...
git status --porcelain

echo.
echo 💾 Creando commit...
git commit -m "feat: Actualizacion completa del sistema

- Sistema de notificaciones completamente implementado
- Panel administrativo con dropdown menu integrado
- Navbar corregido en todas las vistas del sistema
- Templates profesionales y responsivos
- CSS global para evitar superposicion de contenido
- Scripts de verificacion y mantenimiento
- Documentacion actualizada

Caracteristicas:
- Notificaciones Email/SMS/WhatsApp
- Dashboard administrativo completo
- Gestion de plantillas y usuarios
- Accesos directos en menu dropdown
- Navbar dinamico sin superposicion
- Sistema completamente funcional

URLs disponibles:
- /notifications/ - Panel principal
- /notifications/admin/ - Administracion
- /notifications/admin/templates/ - Plantillas
- /notifications/preferences/ - Preferencias"

echo.
echo 🚀 Subiendo cambios al repositorio...
git push origin main

echo.
echo ================================================================
echo 🎉 CAMBIOS SUBIDOS EXITOSAMENTE
echo ================================================================
pause
