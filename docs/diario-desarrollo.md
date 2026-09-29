# Diario de desarrollo de ElectroStock

Este archivo cuenta **cómo evolucionó** el proyecto. A diferencia de `CHANGELOG.md` (qué se modificó), acá registro problemas, razonamientos, dificultades, pruebas y aprendizajes. Lo redacto como bitácora para poder explicarlo también en entrevistas técnicas.

## Etapa inicial — Del ejercicio de Python a un inventario

**Problema:** un inventario de productos eléctricos necesita códigos, unidades de medida, existencias y un registro de entradas y salidas.

**Enfoque:** partir de una versión sencilla, identificar operaciones básicas y comprender por qué modificar un número de stock sin historial no alcanza para auditar las operaciones.

**Aprendizaje:** antes de diseñar muchas pantallas, debo definir qué información se guarda, cómo cambia y qué reglas nunca pueden incumplirse.

## v1.1 — Primera arquitectura cliente-servidor

**Problema:** necesitaba conservar los datos, tener una interfaz gráfica y evitar que toda la lógica dependiera de una sola pantalla.

**Implementación:** interfaz Flet, API FastAPI y persistencia PostgreSQL mediante SQLAlchemy. Se incorporaron registro de productos, movimientos y un dashboard inicial.

**Dificultades observadas:** resolución de imports Python (`python -m frontend.main` desde la carpeta raíz), conexiones cuando el backend no está iniciado y cambios entre versiones de Flet.

**Comprobación realizada:** durante el desarrollo se registró una entrada de 100 metros para un cable y se observó que el producto y el movimiento seguían apareciendo después de volver a abrir la aplicación.

**Aprendizaje:** las capas deben iniciarse y comprobarse por separado. Que Flet abra no prueba, por sí solo, que PostgreSQL responda.

## v1.2 — Modelar materiales eléctricos correctamente

**Problema:** los materiales eléctricos no son intercambiables: los cables se gestionan en metros; las térmicas en unidades; las especificaciones técnicas y las presentaciones cambian según el artículo.

**Implementación en el código:** categorías con campos técnicos dinámicos, unidades base, presentaciones con factor de conversión, edición de productos y movimientos que conservan cantidad y factor originales.

**Por qué:** permite registrar compras en rollos o cajas y convertirlas a la medida correcta, sin perder el significado histórico de una operación.

**Protección de datos:** la actualización desde v1.1 agrega estructura sin eliminar productos ni movimientos existentes; requiere respaldo previo.

**Comprobaciones:** se diseñaron pruebas automatizadas aisladas, incluida una prueba de migración. En la aplicación local se observó el dashboard v1.2 leyendo datos previos. **Pendiente:** documentar la ejecución manual integral de todas las nuevas opciones de v1.2 contra una instancia PostgreSQL y una restauración de respaldo comprobada.

**Aprendizaje:** una nueva función no debe comprometer datos antiguos. Las reglas de inventario deben evaluarse también desde la API, no solamente desde el formulario.

## Publicación inicial en GitHub

**Problema:** el proyecto necesitaba control de versiones, documentación y una forma de mostrar su evolución.

**Trabajo realizado:** configuración de Git, archivos ignorados para proteger credenciales y respaldos, primer commit de código y publicación de `main` en GitHub.

**Dificultades observadas:** corregir el remoto, autenticar GitHub y unir dos commits iniciales independientes conservando la licencia existente en GitHub.

**Aprendizaje:** un commit guarda una versión local, pero no la publica. Conviene revisar los archivos preparados antes de hacer `push`, especialmente `.env`, bases y respaldos.

## Próxima entrada — v1.3 (plantilla)

**Objetivo:**

**Problema detectado:**

**Opciones consideradas:**

**Decisión y por qué:**

**Cambios implementados:**

**Cómo lo probé (comando, entorno y resultado):**

**Errores encontrados y soluciones:**

**Qué aprendí:**

**Qué dejo para la próxima versión:**

**Commits e issues relacionados:**

---

## Reglas para mantener el diario

- Escribir una entrada por fase o hito significativo, no por cada cambio de una línea.
- Explicar qué problema había **antes** de la solución.
- Separar lo que está implementado de lo que fue efectivamente probado.
- Agregar enlaces a commits, issues y capturas cuando existan; no inventar resultados.
- Actualizar también `CHANGELOG.md` y `ROADMAP.md` cuando se cierre una versión.
