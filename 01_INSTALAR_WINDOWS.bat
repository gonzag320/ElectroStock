@echo off
cd /d "%~dp0"
echo ELECTROSTOCK - INSTALACION
if not exist .venv\Scripts\python.exe (
    python -m venv .venv
    if errorlevel 1 goto fail
)
.venv\Scripts\python.exe -m pip install --upgrade pip
if errorlevel 1 goto fail
.venv\Scripts\python.exe -m pip install -r backend\requirements.txt -r frontend\requirements.txt
if errorlevel 1 goto fail
if not exist backend\.env copy backend\.env.example backend\.env
if not exist frontend\.env copy frontend\.env.example frontend\.env
cls
echo LISTO. Edita backend\.env y reemplaza DB_PASSWORD por tu clave PostgreSQL.
echo Despues ejecuta 02_INICIAR_BACKEND.bat y 03_INICIAR_FLET.bat.
pause
exit /b 0
:fail
echo ERROR. Revisa el texto anterior (Python o conexion a Internet).
pause
exit /b 1
