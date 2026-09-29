@echo off
setlocal
cd /d "%~dp0"
title ElectroStock v1.2 - Servidor API
if not exist ".venv\Scripts\python.exe" (
 echo ERROR: Primero ejecuta 01_INSTALAR_WINDOWS.bat.
 goto error
)
if not exist "backend\.env" (
 echo ERROR: No existe backend\.env. Copia el antiguo o configura el nuevo.
 goto error
)
echo ELECTROSTOCK v1.2 - Servidor FastAPI
echo ATENCION: Si actualizas desde v1.1, PRIMERO hace un respaldo PostgreSQL.
echo La primera ejecucion agrega las nuevas tablas y columnas conservando los datos anteriores.
echo.
echo [1/2] Comprobando conexion a PostgreSQL...
".venv\Scripts\python.exe" -m backend.diagnostico
if errorlevel 1 goto error
echo.
echo [2/2] Iniciando FastAPI, deja esta ventana abierta...
echo http://127.0.0.1:8000/api/salud-db
".venv\Scripts\python.exe" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
if errorlevel 1 goto error
exit /b 0
:error
echo.
echo NO se inicio el servidor; guarda el mensaje del error.
pause
exit /b 1
