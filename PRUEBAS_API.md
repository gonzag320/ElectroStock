# API ElectroStock v1.2

Iniciá `02_INICIAR_BACKEND.bat` y abrí http://127.0.0.1:8000/docs.

Endpoints:

- `GET /api/salud-db` comprueba conexión a PostgreSQL.
- `GET /api/panel` muestra indicadores de stock.
- `GET /api/categorias` categorías y campos específicos.
- `POST /api/categorias` crea categoría con campos definidos por el comercio.
- `GET /api/productos?q=` busca por nombre, código, categoría y marca (máximo 300).
- `POST /api/productos` agrega material eléctrico (stock inicial = 0).
- `GET /api/productos/{id}` incluye `atributos_tecnicos` y sus presentaciones.
- `PATCH /api/productos/{id}` edita atributos, precios y mínimo sin tocar existencias.
- `GET /api/productos/{id}/presentaciones` enumera rollos, cajas y paquetes.
- `POST /api/productos/{id}/presentaciones` crea una presentación y su factor.
- `GET /api/movimientos` consulta historial.
- `POST /api/movimientos` realiza entrada o salida atómica en unidad base.

**Crear cable** (ejemplo para el formulario Swagger):

```json
{
  "codigo": "CAB-100",
  "nombre": "Cable unipolar 2,5 mm²",
  "categoria": "Cables",
  "marca": "Prysmian",
  "unidad": "metros",
  "stock_minimo": "20",
  "precio_compra": "650",
  "precio_venta": "950",
  "atributos_tecnicos": {
    "seccion_mm2": "2.5",
    "tipo_cable": "Unipolar",
    "color": "Rojo",
    "material": "Cobre"
  }
}
```

**Agregar presentación**: `POST /api/productos/1/presentaciones`:

```json
{"nombre": "Rollo 100 m", "factor": "100"}
```

**Entrada de 2 rollos** (`presentacion_id` debe ser el que devolvió tu API):

```json
{
  "producto_id": 1,
  "tipo": "entrada",
  "presentacion_id": 1,
  "cantidad": "2",
  "motivo": "Compra",
  "responsable": "Operador"
}
```

El movimiento generado guarda `cantidad=200.000` (metros base), `cantidad_original=2.000`,
`presentacion_nombre=Rollo 100 m`, `factor_conversion=100.000`. Si omitís `presentacion_id`,
`cantidad` se interpreta **directamente** en unidad base.

**Atención:** los ejemplos de Swagger escriben sobre TU base si los ejecutás; usá códigos
nuevos o datos de prueba solo cuando realmente quieras registrar esos movimientos.
