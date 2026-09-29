# Registro de decisiones técnicas

Este documento explica **por qué** está construido ElectroStock de esta manera. Es una bitácora de decisiones del proyecto, no una afirmación de que todas las alternativas fueron implementadas y comparadas mediante benchmarks.

Cada decisión incluye el problema, la elección, el motivo, su consecuencia y cuándo conviene revisarla.

## DT-001 — Separar interfaz, API y base de datos

**Estado:** adoptada desde la versión cliente-servidor.  
**Problema:** un programa instalado y con datos ligados a un solo equipo dificulta la recuperación, la expansión y el acceso desde otros dispositivos.

**Decisión:** separar Flet, FastAPI y PostgreSQL, con comunicación HTTP entre la interfaz y la API.

**Por qué:** puedo evolucionar la pantalla de escritorio sin cambiar las reglas de inventario y, en el futuro, construir otro cliente que reutilice la API. PostgreSQL almacena datos independientemente de la ventana Flet.

**Costo y límites:** exige iniciar y mantener un servidor, gestionar conexiones y agregar seguridad antes de habilitar acceso remoto. La separación **no equivale** a tener respaldos automáticos ni una nube ya implementada.

## DT-002 — Elegir Flet para el primer frontend

**Estado:** adoptada.  
**Problema:** necesitaba pasar de un programa de consola a una interfaz sin abandonar Python durante esta etapa de aprendizaje.

**Decisión:** desarrollar la interfaz inicial con Flet.

**Por qué:** simplifica el prototipado de formularios, tablas y navegación en Python y permite estudiar posibles objetivos multiplataforma más adelante.

**Costo y límites:** debo comprobar la compatibilidad entre versiones de Flet y adaptar la experiencia para móviles; no basta con que la tecnología admita Android para declarar la aplicación Android terminada. Un cambio de API de Flet ya obligó a corregir el uso de diálogos durante el desarrollo.

## DT-003 — Utilizar FastAPI y SQLAlchemy

**Estado:** adoptada.  
**Problema:** colocar consultas SQL y validaciones directamente dentro de los botones de Flet dificultaría reutilizar y probar el inventario.

**Decisión:** exponer una API REST con FastAPI y mantener modelos y operaciones de base de datos en el backend mediante SQLAlchemy.

**Por qué:** separa presentación, rutas, lógica de negocio y persistencia; además permite comprobar endpoints desde `/docs` y automatizar pruebas.

**Costo y límites:** aumenta los archivos y exige contratos claros entre frontend y backend. Esta complejidad se justifica por el objetivo de ampliar el sistema.

## DT-004 — Usar PostgreSQL como almacenamiento principal

**Estado:** adoptada.  
**Problema:** necesitaba persistencia independiente de la interfaz y un camino para una futura arquitectura con varios clientes.

**Decisión:** usar PostgreSQL en la aplicación principal y SQLite temporal solo para algunas pruebas automatizadas.

**Por qué:** permite modelar relaciones, restricciones e historial de movimientos sobre una base de datos separada del cliente.

**Costo y límites:** requiere instalación, credenciales, mantenimiento y respaldos. Los resultados de tests con SQLite no sustituyen pruebas de integración con PostgreSQL.

## DT-005 — Una unidad base por producto y presentaciones convertibles

**Estado:** incorporada en v1.2.  
**Problema:** no debe sumarse directamente «2 rollos» a «50 metros» ni admitirse «0,5 térmicas».

**Decisión:** asignar una única unidad base por producto y definir presentaciones comerciales mediante un factor numérico positivo.

**Por qué:** las entradas y salidas mantienen una medida consistente sin perder la forma en la que se compró o vendió el material. Esto también permite reglas diferentes para metros y piezas enteras.

**Costo y límites:** los precios y el stock usan la unidad base; el programa necesita explicar la conversión. Cambiar la unidad principal de un producto con historial podría alterar el significado de sus datos, por lo que se restringe.

## DT-006 — Guardar una fotografía de la conversión en cada movimiento

**Estado:** incorporada en v1.2.  
**Problema:** si se modifica en el futuro el factor de una caja o de un rollo, los registros antiguos no deberían cambiar de significado.

**Decisión:** guardar la cantidad original, el nombre de la presentación y el factor utilizado en cada movimiento, además de la cantidad en unidad base.

**Por qué:** protege la interpretación histórica de las operaciones y facilita la trazabilidad.

**Costo y límites:** almacena algunos campos repetidos deliberadamente. Los movimientos antiguos de v1.1 no contienen estos nuevos campos, pero se conservan y siguen siendo legibles.

## DT-007 — Atributos técnicos dinámicos por categoría

**Estado:** incorporada en v1.2.  
**Problema:** una térmica y un cable necesitan campos distintos; crear columnas nuevas para cada material volvería rígida la tabla de productos.

**Decisión:** mantener los datos comunes en columnas y almacenar atributos técnicos específicos en un campo JSON. Las categorías definen qué campos muestra el formulario.

**Por qué:** puedo añadir tipos de materiales con distintos atributos sin cambiar todo el esquema cada vez.

**Costo y límites:** los datos JSON exigen validación de tipos y consistencia desde la aplicación. Si en el futuro se necesitan filtros o reportes intensivos sobre un atributo, habrá que evaluar índices o rediseñar parte del modelo.

## DT-008 — Cantidades decimales exactas y movimientos transaccionales

**Estado:** incorporada en v1.2.  
**Problema:** materiales medidos pueden necesitar fracciones y una falla intermedia no debe registrar un movimiento sin su actualización de stock.

**Decisión:** utilizar campos `Numeric(12,3)` para cantidades y aplicar validaciones y actualizaciones como operación del backend.

**Por qué:** evita errores típicos de representar unidades de inventario mediante `float` y favorece la consistencia entre existencias e historial.

**Costo y límites:** tres decimales son una decisión explícita de precisión. Si un rubro requiere más, deberé revisar todo el contrato de datos y sus pruebas.

## DT-009 — Actualizar v1.1 con una migración aditiva

**Estado:** incorporada en v1.2.  
**Problema:** ya existían productos y movimientos registrados que debían sobrevivir a una ampliación del modelo.

**Decisión:** añadir las nuevas tablas y columnas sin eliminar los campos anteriores ni sobrescribir el stock, y exigir un respaldo previo.

**Por qué:** proteger la continuidad de uso y reducir el riesgo de pérdida de información durante la evolución del sistema.

**Costo y límites:** por ahora la migración está implementada en el proyecto, no mediante una herramienta de migraciones versionadas como Alembic. Antes de futuras modificaciones complejas, debo evaluar ese cambio y probar una restauración real.

## DT-010 — Utilizar Git, GitHub y documentación de decisiones

**Estado:** adoptada al publicar la v1.2.  
**Problema:** necesitaba mantener un historial de lo desarrollado, recuperar versiones y explicar mis decisiones en un portfolio.

**Decisión:** versionar código y documentación, ignorar archivos `.env` y respaldos y publicar un repositorio con README, roadmap, pruebas y un registro de decisiones.

**Por qué:** hace visible la evolución del proyecto y permite que otra persona comprenda los cambios y sus motivos.

**Costo y límites:** Git no reemplaza el respaldo de PostgreSQL. Cada publicación requiere comprobar qué archivos están preparados y evitar incluir credenciales.

---

## Plantilla para la próxima decisión

```markdown
## DT-011 — Título breve

**Estado:** propuesta / adoptada / reemplazada.
**Versión:** vX.Y.
**Problema:** ¿qué necesidad apareció?
**Alternativas consideradas:** ¿qué opciones había?
**Decisión:** ¿qué elegí?
**Por qué:** ¿cuál fue el criterio principal?
**Consecuencias:** ¿qué simplifica y qué complica?
**Evidencia:** issue, prueba, captura, commit o documentación relacionada.
**Cuándo revisar:** ¿qué cambio podría volver obsoleta la decisión?
```
