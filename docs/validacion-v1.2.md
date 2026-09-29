# Validación funcional — ElectroStock v1.2

**Fecha:** 28/09/2026  
**Entorno:** Windows, Python, FastAPI, PostgreSQL y Flet.

## 1. Objetivo

Comprobar el correcto funcionamiento de la gestión de inventario eléctrico y verificar que la información pueda recuperarse mediante un respaldo de PostgreSQL.

## 2. Pruebas realizadas

| Prueba | Resultado |
|---|---|
| Pruebas automatizadas | 15 superadas |
| Registro de productos eléctricos | Correcto |
| Almacenamiento de características técnicas | Correcto |
| Conversión de rollos a metros | Correcto |
| Entradas y salidas | Correcto |
| Protección contra stock negativo | Correcto |
| Persistencia después del reinicio | Correcto |
| Restauración de datos en PostgreSQL | Correcto |

## 3. Recuperación de información

Se generó un respaldo de `electrostock_db` y se restauró en una base independiente llamada `electrostock_restore_test`.

La recuperación permitió verificar:

- 2 productos.
- 3 movimientos.
- 2 presentaciones comerciales.
- 10 categorías.
- Stock recuperado del producto de prueba: 175 metros.

## 4. Problemas detectados

Durante las pruebas se identificaron oportunidades de mejora:

- Incorporar búsqueda de productos por nombre, código y marca.
- Utilizar la unidad base como selección predeterminada en las salidas.
- Evitar el registro de presentaciones comerciales duplicadas.
- Mejorar los mensajes de error y las etiquetas de unidades.

## 5. Conclusión

Las pruebas realizadas permitieron validar las principales operaciones de inventario de ElectroStock v1.2 y la recuperación de sus registros mediante un respaldo.

Antes de utilizar el sistema en producción, quedan pendientes la prueba de recuperación completa desde la aplicación y otras verificaciones de seguridad y funcionamiento multiusuario.