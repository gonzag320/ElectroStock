# Cambios

## v1.2 (ElectroStock)

- Migración conservadora v1.1 → v1.2 y categorías preconfiguradas. Preserva tabla de productos,
  tabla de movimientos y sus datos, agregando atributos JSON, categorías y presentaciones.
- Formularios dinámicos técnicos, edición de productos, gestión de presentaciones por producto.
- Validación por unidad base; no se aceptan fracciones de piezas ni stock negativo.
- Movimiento con snapshot de cantidad/factor de presentación para conservar historial legible.
- Interfaz con menú activo, fecha Argentina y cantidades adaptadas.
- Backup previo obligatorio recomendado; script manual Windows incluido.

## Límites conocidos

- No hay cambios de factor ni eliminación de presentaciones desde la interfaz; crear
  otra presentación si cambia el empaque, evitando reinterpretaciones accidentales.
- Por ahora se muestran hasta 300 productos en listados; el buscador permite filtrar.
- No hay permisos multiusuario, login, seguridad de red, ni backups automáticos.
