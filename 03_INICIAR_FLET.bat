@echo off
setlocal
cd /d "%~dp0"
title ElectroStock - Interfaz
if not exist ".venv\Scripts\python.exe" (
 echo ERROR: Primero ejecuta 01_INSTALAR_WINDOWS.bat desde esta carpeta.
 pause
 exit /b 1
)
echo.
echo Asegurate de que el servidor 02_INICIAR_BACKEND.bat permanezca abierto.
echo Si aun no inicio, la pantalla de Flet te permitira reintentar.
echo.
".venv\Scripts\python.exe" -m frontend.main
if errorlevel 1 (
 echo ERROR: No se pudo iniciar la interfaz Flet. Copia el mensaje anterior.
 pause
 exit /b 1
)
exit /b 0
