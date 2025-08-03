@echo off
echo ===========================================
echo     INICIANDO SERVIDOR GALLETAS KATI
echo ===========================================
echo.
echo 🚀 Servidor con todas las funcionalidades:
echo   ✅ Módulo de administración completo
echo   ✅ Sistema de seguridad empresarial
echo   ✅ Control de acceso por roles
echo   ✅ 6 nuevos modelos implementados
echo.
echo 🌐 URLs disponibles:
echo   📍 Tienda: http://127.0.0.1:8000/
echo   🔐 Admin: http://127.0.0.1:8000/admin/
echo.
echo 👤 Usuarios disponibles:
echo   🔴 admin / Admin123!@# (Superusuario)
echo   🟡 tienda_admin / Tienda123!@# (Admin Tienda)
echo   🟢 stock_operator / Stock123!@# (Solo Stock)
echo.
echo Iniciando servidor...
echo.

python manage.py runserver 127.0.0.1:8000
