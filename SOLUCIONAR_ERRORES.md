# Solución de problemas — ElectroStock 1.2

- **Conexión rechazada / WinError 10061**: ejecutá `02_INICIAR_BACKEND.bat`, mantenelo
  abierto y visitá http://127.0.0.1:8000/api/salud-db. Luego abrí Flet.
- **Contraseña incorrecta**: recuperá tu archivo `backend/.env` anterior y copialo a
  la nueva carpeta. No publiques ni fotografíes la contraseña.
- **No module named backend**: ejecutá desde la carpeta **principal** del ZIP, que
  contiene tanto `backend` como `frontend`. No ejecutes desde la subcarpeta backend.
- **Page object has no attribute open**: estás ejecutando un frontend antiguo.
  Iniciá `03_INICIAR_FLET.bat` **desde la nueva carpeta** y cerrá el de la versión 1.1.
- **Error de categorías/columnas en PostgreSQL al iniciar**: verificá si el script
  de respaldo previo funcionó, detené el backend, guardá el error y no borres tablas.
- **Error por cambio de unidad**: si hay movimientos, stock o presentaciones, esa
  conversión no puede hacerse editando; creá otro código para la otra unidad.
- **Intentaste registrar media térmica o medio rollo**: se rechazan piezas y
  envases fraccionarios por diseño; usá metros como base para comprar o cortar cable.
- **No se puede conectar desde un celular**: esta versión es LOCAL. No publiques
  el servidor sin usuarios, HTTPS, permisos y respaldos verificados.

## Prueba de diagnóstico

Desde la carpeta raíz en PowerShell:

```powershell
.\.venv\Scripts\python.exe -m backend.diagnostico
```

Si falla, copiá el texto del error sin tu contraseña. **No borres tu PostgreSQL
ni tu antigua carpeta** para intentar corregir un error de conexión.
