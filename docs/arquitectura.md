# Arquitectura de ElectroStock

**Alcance:** arquitectura del prototipo local v1.2. No describe un despliegue multiusuario ya existente.

```text
  ┌────────────────────────────────┐
  │     Flet (cliente Windows)     │
  │  formularios, tablas, panel    │
  └──────────────┬─────────────────┘
                 │ HTTP / JSON
                 ▼
  ┌────────────────────────────────┐
  │      FastAPI (backend)         │
  │ routers → services → reglas    │
  └──────────────┬─────────────────┘
                 │ SQLAlchemy
                 ▼
  ┌────────────────────────────────┐
  │       PostgreSQL local         │
  │ productos, movimientos,        │
  │ categorías y presentaciones    │
  └────────────────────────────────┘
```

## Distribución de responsabilidades

- **`frontend/`**: recibe las acciones del usuario y llama a los endpoints de FastAPI. Evita incorporar lógica de persistencia directamente en la interfaz.
- **`backend/routers/`**: define la API para categorías, productos, presentaciones, movimientos y panel.
- **`backend/services/`**: concentra operaciones y reglas de inventario (validación de unidades, conversión de presentaciones, control de stock).
- **`backend/database/`**: define modelos SQLAlchemy, crea conexiones y aplica la migración aditiva actual.
- **`tests/`**: comprueba rutas, reglas y regresiones usando una base de pruebas temporal. PostgreSQL local requiere comprobaciones adicionales.

## Modelo de datos actual

| Entidad | Responsabilidad |
| --- | --- |
| Producto | Código único, nombre, marca, categoría, unidad base, stock, mínimo, precios, atributos técnicos JSON. |
| Categoría | Nombre único y definición de los campos dinámicos. |
| Presentación | Nombre comercial y factor de conversión hacia la unidad base del producto. |
| Movimiento | Entrada o salida con cantidad en unidad base, motivo, responsable, fecha y fotografía de la conversión original. |

Los **precios** se expresan por unidad base, no automáticamente por rollo o caja. Cada producto mantiene una sola unidad principal.

## Flujo de un movimiento

1. La interfaz solicita el producto y, si corresponde, una presentación.
2. La persona ingresa una cantidad y un motivo.
3. La API valida el dato y calcula la equivalencia en la unidad base.
4. El servicio registra el movimiento y modifica el stock mediante una operación transaccional.
5. La respuesta actualiza la interfaz. El historial conserva la cantidad presentada originalmente y el factor aplicado.

**Ejemplo:** `2 rollos × 100 m = 200 m`. El inventario almacena `200 m`; el historial conserva `2`, `Rollo 100 m` y `100` para que un cambio posterior de empaque no reinterprete una operación pasada.

## Evolución y límites

La migración v1.1 → v1.2 agrega columnas y tablas sin sobrescribir el campo legado `especificacion`. Antes de ejecutarla en datos existentes se requiere un respaldo. No hay sistema de migraciones versionado con Alembic en esta versión; es una mejora posible para futuras fases.

Actualmente Flet se utiliza como cliente de escritorio y la API se ejecuta en la PC local. **No habilitar acceso por Internet** antes de implementar autenticación, autorización, HTTPS y una estrategia de restauración de copias verificadas.
