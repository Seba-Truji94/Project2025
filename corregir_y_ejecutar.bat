@echo off
echo ===========================================
echo   DIAGNOSTICO Y CORRECCION DE BASE DE DATOS
echo ===========================================

echo.
echo 1. Ejecutando diagnostico...
python diagnostico.py

echo.
echo 2. Intentando makemigrations...
python manage.py makemigrations notifications

echo.
echo 3. Intentando migrate...
python manage.py migrate

echo.
echo 4. Verificando nuevamente...
python diagnostico.py

echo.
echo 5. Si todo esta bien, iniciando servidor en puerto 8002...
python manage.py runserver 8002

pause
