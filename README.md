# ⚡ ElectroStock v1.2 — Flet + FastAPI + PostgreSQL

**Prototipo de desarrollo local** de un inventario especializado en electricidad. Código fuente incluido.
Esta versión incorpora formularios según categoría, actualización de productos, presentaciones
(rollos, cajas), cantidades decimales para materiales medidos y cantidades enteras para piezas.

## Novedades v1.2

- Categorías eléctricas preconfiguradas: **Cables, Termomagnéticas, Diferenciales, LED** y otras.
  Se pueden crear categorías propias con campos de texto, numéricos o de opciones desde la interfaz.
  No permite modificar/eliminar categorías anteriores por seguridad en esta versión.
- Características técnicas separadas para cada producto: amperios, polos, sección, potencia, etc.
- **Unidades base**: metros (con hasta tres decimales), unidades individuales (enteros), litros, kg.
  La app impide vender 0,5 interruptores y evita stock negativo.
- **Presentaciones** definidas por producto: 1 rollo de 100 m = 100 metros; 1 caja de 10 = 10 unidades.
  Se configuran desde **Productos → Editar → Presentaciones comerciales**.
- Registro de la cantidad ORIGINAL (ej. 2 rollos) y su conversión **congelada** en el historial
  (200 metros), incluso si cambia una presentación futura.
- Edición de precios, marca, características y mínimo, sin alterar stock ni movimientos previos.
- Historial con fechas de Argentina y cantidades sin ceros finales innecesarios.
- Se conserva la columna antigua `especificacion` y los datos existentes de PostgreSQL v1.1.

## 1. Actualizar desde v1.1 sin perder datos

1. **Cerrá** las ventanas del servidor y de Flet de la v1.1.
2. **No borres** la carpeta anterior ni desinstales PostgreSQL.
3. Abrí la carpeta antigua de ElectroStock y ejecutá su respaldo, si ya lo tenés;
   o usá `00_RESPALDAR_BD_ANTES_DE_ACTUALIZAR.bat` de este ZIP.
   El archivo `.backup` debe quedar generado **antes** de ejecutar la v1.2.
   **Copialo también a otra unidad o nube segura.** Verificá que existe y no está vacío.
4. Descomprimí ESTE ZIP **en una carpeta nueva** (por ejemplo `Documentos/ElectroStock_v1_2`).
   No sobrescribas ni mezcles archivos de versiones anteriores.
5. Ejecutá `01_INSTALAR_WINDOWS.bat` (requiere Internet la primera vez).
6. Copiá **tu antiguo `backend/.env`** a `backend/.env` de esta nueva carpeta,
   o escribí tu contraseña actual de PostgreSQL en el nuevo `backend/.env` generado.
   **No envíes ni publiques el archivo `.env`**. `frontend/.env` apunta por defecto a
   `http://127.0.0.1:8000` y se crea con el instalador.
7. Ejecutá `02_INICIAR_BACKEND.bat`. La primera vez agregará columnas nuevas y tablas faltantes
   mediante una **migración aditiva**; los registros de las tablas antiguas permanecen.
   Debe mostrar `OK: conexión a PostgreSQL` y permanecer abierto.
8. Probá `http://127.0.0.1:8000/api/salud-db` en tu navegador.
9. Sin cerrar el backend, ejecutá `03_INICIAR_FLET.bat` y abrí Productos.

**La base existente es `electrostock_db`. No ejecutes `CREATE DATABASE` ni borres las tablas.**
Si necesitás volver a v1.1, restaurá antes el respaldo previo en un entorno apropiado:
no intentes deshacer la migración eliminando columnas a mano.

### Si empezás desde cero

Asegurate de que PostgreSQL 18 esté instalado y de que exista la base `electrostock_db`.
Configurá `backend/.env`, ejecutá primero el instalador, luego backend y Flet.
No es necesario crear las tablas manualmente.

## 2. Instrucciones manuales en VS Code (Windows + Python 3.12)

Abrí la **carpeta principal** donde están `backend`, `frontend`, `README.md` y los `.bat`.
En la terminal de VS Code:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt -r frontend\requirements.txt
Copy-Item backend\.env.example backend\.env
notepad backend\.env
```

Si ya existe `.env`, **no lo sobrescribas**: usá el que tiene tu clave correcta.
En **dos terminales diferentes**:

```powershell
# Primera terminal, desde la carpeta principal
.\.venv\Scripts\python.exe -m backend.diagnostico
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

```powershell
# Segunda terminal, sin cerrar la anterior
.\.venv\Scripts\python.exe -m frontend.main
```

API documentada en `http://127.0.0.1:8000/docs`.

## 3. Ejemplo con tus datos existentes

- Tu producto previo `CAB-001` con 100 metros y el historial anterior seguirá en Productos.
- Entrá en **Editar** para agregar `Sección: 2.5` y `Color: rojo`.
  El campo de descripción técnica anterior no se borra.
- Debajo del editor, cargá la presentación `Rollo de 100 m` con factor `100`.
- En **Movimientos**, escribí `CAB-001` → **Seleccionar**, elegí la presentación
  `Rollo de 100 m`, ingresá `2`, tipo **entrada** y motivo **Compra**.
  El programa debe mostrar **200 metros** como vista previa. **Esa prueba suma 200 al stock real**;
  si solo querés comprobar la pantalla, NO presiones Registrar movimiento.
- Probá con una térmica: crea `TER-020` en categoría Termomagnéticas,
  corriente 20 A, 2 polos, curva C, unidad base **unidad**. La API rechaza una salida de 0,5.

## 4. Qué significan las unidades y los precios

- Cada producto **siempre tiene UNA unidad de inventario**. Las presentaciones convierten hacia ella.
- El precio de compra y venta es **por unidad base** (ej., por metro, NO por rollo).
- Los datos previos de precios no se convierten automáticamente. Revisá si antes habías
  registrado algún precio por rollo cuando la unidad decía "metros".
- Si un producto ya tiene movimientos, stock o presentaciones, no se puede cambiar
  arbitrariamente su unidad base; deberás crear otro código para otro tipo de unidad.
- Registramos cantidades con `Numeric(12,3)` para evitar errores de punto flotante.

## 5. Problemas frecuentes

- `No module named backend`: abriste la subcarpeta, no la raíz; volvé a la carpeta que contiene `backend`.
- `No se pudo conectar con FastAPI`: iniciá primero `02_INICIAR_BACKEND.bat` y verificá el navegador.
- `Contraseña incorrecta`: revisá `backend/.env`; no compartas la clave en capturas.
- `address already in use`: hay otro FastAPI en el puerto 8000; cerralo.
- `psql no se reconoce`: la herramienta está en `C:\Program Files\PostgreSQL\18\bin`.
- Si la actualización no arranca, no borres tablas: enviá el error textual sin contraseña.

## 6. Pruebas y seguridad

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
```

Las pruebas automatizadas utilizan SQLite **temporal y aislada**, nunca tu `electrostock_db`.
Se comprueba por separado una migración desde el esquema v1.1 real en SQLite.
Esta entrega NO fue ejecutada contra tu instancia local de PostgreSQL, ni se probó
el renderizado gráfico de Flet en tu computadora; ambas cosas se verifican siguiendo
los pasos de instalación.

**No publiques FastAPI en Internet.** Falta login, autorización, HTTPS, respaldos automáticos
verificados y despliegue seguro. El ZIP no genera todavía una APK Android. Aún no hay
facturación, ventas o gestión avanzada de proveedores.
