@echo off
setlocal
cd /d "%~dp0"
title ElectroStock - Respaldo previo
 echo Este paso es obligatorio si ya tenes datos en PostgreSQL.
 echo Se hara un respaldo de electrostock_db en la carpeta backups.
 echo NO se borra ni modifica tu base de datos.
 echo.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\backup_postgres.ps1"
if errorlevel 1 (
 echo.
 echo ERROR: El respaldo no se completo. NO ACTUALICES antes de resolverlo.
 pause
 exit /b 1
)
echo.
echo Copia tambien el archivo .backup a una unidad externa o nube segura.
pause
exit /b 0
