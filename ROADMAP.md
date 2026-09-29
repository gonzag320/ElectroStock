# Roadmap de ElectroStock

Este documento muestra el orden de trabajo y los criterios para considerar terminada cada fase. Las fechas futuras son orientativas; no representan compromisos de publicación.

**Estado actual:** v1.2 implementada y ejecutada como prototipo local. Pendiente: completar la validación funcional de todos los nuevos flujos y automatizar más pruebas contra PostgreSQL.

## Fase 0 — Primer prototipo de inventario

**Objetivo:** llevar los ejercicios de Python a un caso práctico: productos, existencias y movimientos.

- [x] Definir el problema y la especialización en electricidad.
- [x] Probar una primera versión de inventario.
- [x] Identificar la necesidad de conservar movimientos, además del stock final.

**Aprendizaje:** una cantidad por sí sola no explica por qué cambió el inventario.

## Fase 1 — Arquitectura cliente-servidor (v1.1)

**Objetivo:** separar interfaz, reglas de negocio y almacenamiento.

- [x] API con FastAPI.
- [x] Base PostgreSQL y acceso mediante SQLAlchemy.
- [x] Interfaz Flet conectada por HTTP.
- [x] Altas de productos y registro de entradas y salidas.
- [x] Dashboard con lectura de datos persistidos.

**Criterio verificado:** registro de una entrada y persistencia después de cerrar y abrir la aplicación en el equipo de desarrollo.

## Fase 2 — Inventario eléctrico (v1.2)

**Objetivo:** representar materiales eléctricos sin distorsionar unidades ni historiales.

- [x] Categorías con campos técnicos específicos.
- [x] Unidades base y validación de decimales/enteros según el material.
- [x] Presentaciones comerciales con factores de conversión.
- [x] Registro histórico de presentación, factor y cantidad original.
- [x] Edición de información de producto sin modificar stock directamente.
- [x] Migración aditiva que conserva el esquema anterior.
- [ ] Completar una lista manual de pruebas sobre PostgreSQL real para cada categoría y presentación.
- [ ] Verificar que el respaldo puede restaurarse en un entorno separado.

**Criterio de finalización:** probar cables en metros, piezas en enteros, rollos/cajas, rechazos de cantidades inválidas, historial y migración desde una copia de v1.1.

## Fase 3 — Consolidación del catálogo (v1.3 prevista)

**Objetivo:** convertir los formularios actuales en una experiencia consistente y comprobable.

- [ ] Ficha de producto con datos generales, especificaciones, presentaciones e historial.
- [ ] Revisar buscador, filtros y paginación de productos.
- [ ] Mostrar correctamente la unidad en todos los listados y documentos.
- [ ] Mejorar mensajes de error y validaciones de interfaz.
- [ ] Añadir pruebas de integración con una base PostgreSQL de pruebas, aislada de los datos reales.
- [ ] Documentar capturas y resultados de pruebas.

## Fase 4 — Proveedores y compras

- [ ] Catálogo de proveedores.
- [ ] Órdenes y registros de compra con sus detalles.
- [ ] Recepción de mercadería que genere movimientos de stock trazables.
- [ ] Definir y documentar la estrategia de costos antes de implementarla.

## Fase 5 — Clientes y ventas

- [ ] Clientes y búsqueda de productos para venta.
- [ ] Confirmación de venta que descuente stock en una operación consistente.
- [ ] Comprobantes internos y presupuestos PDF; evaluar requisitos fiscales por separado.
- [ ] Devoluciones y anulaciones sin eliminar la trazabilidad.

## Fase 6 — Seguridad y continuidad

- [ ] Inicio de sesión y autorización por roles.
- [ ] Configuración segura para despliegue remoto y HTTPS.
- [ ] Estrategia de backups automáticos con restauraciones verificadas.
- [ ] Registro de operaciones sensibles.

## Fase 7 — Reportes y acceso multiplataforma

- [ ] Informes de movimientos, stock crítico y valoración, con filtros y exportación.
- [ ] Validar experiencia Flet para pantallas pequeñas.
- [ ] Evaluar despliegue Android y las particularidades de conexión a la API.
- [ ] Preparar infraestructura remota **solo después** de completar la seguridad.

## Cómo actualizar este plan

Cuando comienzo una fase, creo tareas concretas en GitHub Issues. Cuando termino una funcionalidad, compruebo su comportamiento, actualizo `CHANGELOG.md` y agrego una entrada en `docs/diario-desarrollo.md`. Si una decisión cambia la arquitectura, registro el motivo y las consecuencias en `docs/decisiones-tecnicas.md`. Solo marco una fase como finalizada cuando cumpla sus criterios de aceptación.
