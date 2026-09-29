# Requiere el PostgreSQL local de la instalacion guiada (v18), solicita la contraseña
# en la consola; no copia ni muestra secretos de backend/.env.
$ErrorActionPreference = 'Stop'
$raiz = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$destino = Join-Path $raiz 'backups'
New-Item -ItemType Directory -Force -Path $destino | Out-Null
$fecha = Get-Date -Format 'yyyyMMdd_HHmmss'
$archivo = Join-Path $destino "electrostock_$fecha.backup"
$pgdump = 'C:\Program Files\PostgreSQL\18\bin\pg_dump.exe'
if (!(Test-Path $pgdump)) { throw "No se encuentra pg_dump en $pgdump. Ajusta esta ruta segun tu version de PostgreSQL." }
Write-Host 'Realizando respaldo de electrostock_db. Ingresa tu clave PostgreSQL cuando se solicite.'
& $pgdump -h localhost -U postgres -d electrostock_db -F c -f $archivo
if ($LASTEXITCODE -ne 0) { throw 'Falló pg_dump. Comproba PostgreSQL y tu contraseña.' }
if (!(Test-Path $archivo) -or (Get-Item $archivo).Length -le 0) { throw 'Respaldo no válido: archivo vacío o inexistente.' }
Write-Host "OK: respaldo creado: $archivo"
Write-Host 'Guarda OTRA COPIA en un disco externo o almacenamiento seguro, fuera de la PC.'
