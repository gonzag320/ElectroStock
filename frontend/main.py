"""Interfaz Flet 1.0.1. Ejecutar desde la raíz: python -m frontend.main"""
from decimal import Decimal, InvalidOperation
import re
import unicodedata
import flet as ft
from frontend.services import api
from frontend.utils import numero, dinero, fecha_local, conversion, atributos_resumen

FONDO = '#111A28'
PANEL = '#1D2B3C'
TEXTO_SUAVE = '#AFBED0'
VERDE = '#69D5A7'


def opt(clave, texto=None):
    return ft.DropdownOption(key=str(clave), text=str(texto or clave))


def slug(valor):
    texto = ''.join(c for c in unicodedata.normalize('NFKD', valor.lower()) if not unicodedata.combining(c))
    texto = re.sub(r'[^a-z0-9]+', '_', texto).strip('_')
    if texto and texto[0].isdigit():
        texto = 'campo_' + texto
    return texto[:50]


def main(page: ft.Page):
    page.title = 'ElectroStock | Inventario eléctrico'
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = FONDO
    page.padding = 18
    page.scroll = ft.ScrollMode.AUTO
    contenido = ft.Column(spacing=16)
    actual = 'Inicio'

    def aviso(mensaje, error=False):
        page.show_dialog(ft.SnackBar(content=ft.Text(str(mensaje)),
                        bgcolor='#A13030' if error else '#216B56', duration=4500))

    def api_error(error):
        if error.status is not None and error.status < 500:
            aviso(error, True)
            return
        contenido.controls = [
            ft.Text('No se pudo conectar con FastAPI', size=23, color='#FFAEAE'),
            ft.Text(str(error)),
            ft.Text('Iniciá 02_INICIAR_BACKEND.bat. Probá http://127.0.0.1:8000/api/salud-db.'),
            ft.FilledButton('Reintentar conexión', on_click=lambda _: ir(actual)),
        ]
        page.update()

    def bloque(controles):
        return ft.Container(content=ft.Column(controles, spacing=12),
                            padding=16, bgcolor=PANEL, border_radius=12)

    def cabecera(titulo):
        return ft.Row([ft.Text(titulo, size=24, weight=ft.FontWeight.BOLD),
                       ft.OutlinedButton('Actualizar', on_click=lambda _: ir(titulo))], wrap=True)

    def marcar_menu():
        nombres = ('Inicio', 'Productos', 'Movimientos', 'Categorías')
        nav.controls = [
            (ft.FilledButton if actual == nombre else ft.OutlinedButton)(
                nombre, on_click=lambda _, n=nombre: ir(n)) for nombre in nombres
        ]
        page.update()

    def ir(pantalla):
        nonlocal actual
        actual = pantalla
        marcar_menu()
        try:
            if pantalla == 'Inicio':
                inicio()
            elif pantalla == 'Productos':
                productos()
            elif pantalla == 'Movimientos':
                movimientos()
            elif pantalla == 'Categorías':
                categorias()
        except api.ApiError as exc:
            api_error(exc)

    def tarjeta(titulo, valor):
        return ft.Container(content=ft.Column([
            ft.Text(titulo, size=13, color=TEXTO_SUAVE),
            ft.Text(str(valor), size=24, weight=ft.FontWeight.BOLD)], spacing=6),
            padding=20, width=245, bgcolor=PANEL, border_radius=13)

    def inicio():
        datos = api.panel()
        historia = api.movimientos()
        vista = [cabecera('Inicio'),
                 ft.Text('Resumen del inventario eléctrico', color=TEXTO_SUAVE),
                 ft.Row([
                     tarjeta('Productos', datos['cantidad_productos']),
                     tarjeta('Stock bajo', datos['productos_stock_bajo']),
                     tarjeta('Valor a costo', dinero(datos['valor_inventario_costo'])),
                 ], wrap=True, spacing=12),
                 ft.Text('Últimos movimientos', size=17, weight=ft.FontWeight.BOLD)]
        for m in historia[:6]:
            signo = '+' if m['tipo'] == 'entrada' else '-'
            vista.append(ft.Container(content=ft.Text(
                f"{signo}{numero(m['cantidad'])} {m['unidad_base']} · {m['nombre_producto']} · {fecha_local(m['fecha'])}"),
                padding=12, bgcolor=PANEL, border_radius=8))
        if not historia:
            vista.append(ft.Text('Todavía no registraste movimientos.'))
        contenido.controls = vista
        page.update()

    def campos_producto(categorias_data, actual_producto=None):
        """Devuelve formulario reutilizado para ALTA y EDICIÓN y gestor de presentaciones."""
        anterior = actual_producto or {}
        nombres = [c['nombre'] for c in categorias_data]
        inicial = anterior.get('categoria') or ('Cables' if 'Cables' in nombres else nombres[0])
        lista_unidades = ['metros', 'unidad', 'litros', 'kg']
        if anterior.get('unidad') and anterior['unidad'] not in lista_unidades:
            lista_unidades.append(anterior['unidad'])
        categoria = ft.Dropdown(label='Categoría *', width=265, value=inicial,
                                options=[opt(nombre) for nombre in nombres])
        unidad = ft.Dropdown(label='Unidad base *', width=160,
                            value=anterior.get('unidad') or ('metros' if inicial in ('Cables', 'Conductores') else 'unidad'),
                            options=[opt(u) for u in lista_unidades])
        codigo = ft.TextField(label='Código *', width=165, value=anterior.get('codigo', ''),
                              hint_text='CAB-002', disabled=bool(actual_producto))
        nombre = ft.TextField(label='Nombre *', width=300, value=anterior.get('nombre', ''))
        marca = ft.TextField(label='Marca', width=190, value=anterior.get('marca', ''))
        especificacion = ft.TextField(label='Notas / especificación antigua', width=400,
                                     value=anterior.get('especificacion', ''), multiline=True, min_lines=1, max_lines=3)
        compra = ft.TextField(label='Precio de compra / unidad base', width=220,
                              value=numero(anterior.get('precio_compra', '0')))
        venta = ft.TextField(label='Precio de venta / unidad base', width=220,
                             value=numero(anterior.get('precio_venta', '0')))
        minimo = ft.TextField(label='Stock mínimo (unidad base)', width=215,
                              value=numero(anterior.get('stock_minimo', '0')))
        campos_panel = ft.Column(spacing=10)
        control_atributos = {}

        def render_campos(preservar=False):
            registro = next((c for c in categorias_data if c['nombre'] == categoria.value), None)
            nuevos = {}
            vista = []
            for c in registro.get('campos', []) if registro else []:
                valor_previo = (control_atributos.get(c['clave']).value if preservar and c['clave'] in control_atributos
                                else (anterior.get('atributos_tecnicos') or {}).get(c['clave'], '')
                                if categoria.value == anterior.get('categoria') else '')
                if c['tipo'] == 'opcion':
                    control = ft.Dropdown(label=c['etiqueta'], width=225,
                                          options=[opt(o) for o in c['opciones']], value=valor_previo or None)
                else:
                    control = ft.TextField(label=c['etiqueta'], width=225, hint_text=c.get('ayuda') or '',
                                           value=valor_previo)
                nuevos[c['clave']] = control
                vista.append(control)
            control_atributos.clear()
            control_atributos.update(nuevos)
            campos_panel.controls = [ft.Text('Características técnicas', weight=ft.FontWeight.BOLD),
                                     ft.Row(vista, wrap=True)] if vista else [ft.Text('Sin campos específicos.')]
            page.update()

        def cambio_categoria(_):
            if categoria.value in ('Cables', 'Conductores') and not actual_producto:
                unidad.value = 'metros'
            elif not actual_producto:
                unidad.value = 'unidad'
            render_campos()

        categoria.on_select = cambio_categoria
        # Construcción inicial sin redibujar page hasta que los controles estén montados.
        registro = next((c for c in categorias_data if c['nombre'] == inicial), None)
        for c in registro.get('campos', []) if registro else []:
            valor = (anterior.get('atributos_tecnicos') or {}).get(c['clave'], '')
            if c['tipo'] == 'opcion':
                control = ft.Dropdown(label=c['etiqueta'], width=225,
                                      options=[opt(o) for o in c['opciones']], value=valor or None)
            else:
                control = ft.TextField(label=c['etiqueta'], width=225,
                                       hint_text=c.get('ayuda') or '', value=valor)
            control_atributos[c['clave']] = control
        campos_panel.controls = [ft.Text('Características técnicas', weight=ft.FontWeight.BOLD),
                                  ft.Row(list(control_atributos.values()), wrap=True)]

        def datos_formulario():
            datos = {
                'nombre': nombre.value or '', 'categoria': categoria.value or '',
                'marca': marca.value or '', 'unidad': unidad.value or '',
                'especificacion': especificacion.value or '',
                'precio_compra': (compra.value or '0').replace(',', '.'),
                'precio_venta': (venta.value or '0').replace(',', '.'),
                'stock_minimo': (minimo.value or '0').replace(',', '.'),
                'atributos_tecnicos': {k: str(control.value).strip() for k, control in control_atributos.items()
                                     if control.value is not None and str(control.value).strip()},
            }
            if not actual_producto:
                datos['codigo'] = codigo.value or ''
            return datos

        def guardar(_):
            try:
                if actual_producto:
                    resultado = api.editar_producto(actual_producto['id'], datos_formulario())
                    aviso('Producto actualizado sin alterar su historial.')
                else:
                    resultado = api.crear_producto(datos_formulario())
                    aviso('Producto creado. Podés configurar presentaciones aquí.')
                editor(resultado['id'])
            except api.ApiError as exc:
                api_error(exc)

        nombre_form = 'Editar producto' if actual_producto else 'Nuevo material eléctrico'
        form = bloque([
            ft.Text(nombre_form, size=18, weight=ft.FontWeight.BOLD),
            ft.Row([codigo, nombre, marca], wrap=True),
            ft.Row([categoria, unidad], wrap=True),
            campos_panel,
            especificacion,
            ft.Row([compra, venta, minimo], wrap=True),
            ft.Text('El stock se modifica solamente desde Movimientos. Los precios son por unidad base.',
                    color=TEXTO_SUAVE, size=12),
            ft.Row([ft.FilledButton('Guardar cambios' if actual_producto else 'Crear producto', on_click=guardar),
                    ft.OutlinedButton('Volver al inventario', on_click=lambda _: ir('Productos'))], wrap=True),
        ])
        return form

    def editor(pid):
        try:
            p = api.producto(pid)
            cats = api.categorias()
            # Mantener selección correcta del menú incluso mientras se edita.
            detalle_presentaciones = [ft.Text('Presentaciones comerciales', size=18, weight=ft.FontWeight.BOLD),
                ft.Text(f"Stock actual: {numero(p['stock'])} {p['unidad']} · código {p['codigo']}", color=VERDE),
                ft.Text('Ejemplo: Rollo de 100 m → factor 100. Una compra de 2 rollos suma 200 metros.',
                        color=TEXTO_SUAVE, size=12)]
            p_nombre = ft.TextField(label='Presentación', hint_text='Rollo de 100 m / Caja de 10', width=265)
            p_factor = ft.TextField(label=f'Factor en {p["unidad"]}', hint_text='100', width=190)

            def agregar(_):
                try:
                    api.crear_presentacion(pid, {'nombre': p_nombre.value or '',
                                                 'factor': (p_factor.value or '').replace(',', '.')})
                    aviso('Presentación agregada. Los movimientos anteriores no cambian.')
                    editor(pid)
                except api.ApiError as exc:
                    api_error(exc)

            detalle_presentaciones.append(ft.Row([
                p_nombre, p_factor, ft.FilledButton('Agregar presentación', on_click=agregar)
            ], wrap=True))
            if p['presentaciones']:
                detalle_presentaciones += [ft.Text(
                    f"• {env['nombre']}: 1 = {numero(env['factor'])} {p['unidad']}")
                    for env in p['presentaciones']]
            else:
                detalle_presentaciones.append(ft.Text('Todavía no configuraste rollos ni cajas.'))
            contenido.controls = [ft.Text(f"Edición · {p['codigo']}", size=23),
                                  campos_producto(cats, p), bloque(detalle_presentaciones)]
            page.update()
        except api.ApiError as exc:
            api_error(exc)

    def productos(busqueda=''):
        cats = api.categorias()
        lista = api.productos(busqueda)
        buscar = ft.TextField(label='Buscar por código, nombre, marca o categoría', value=busqueda, width=365)
        buscar.on_submit = lambda _: productos(buscar.value or '')
        indice = {c['nombre']: c for c in cats}
        filas = []
        for p in lista:
            attrs = atributos_resumen(p.get('atributos_tecnicos'), indice.get(p['categoria'], {}))
            if not p.get('atributos_tecnicos') and p['especificacion']:
                attrs = p['especificacion']  # No ocultar las especificaciones de v1.1.
            bajo = Decimal(str(p['stock'])) <= Decimal(str(p['stock_minimo']))
            filas.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(p['codigo'])),
                ft.DataCell(ft.Text(p['nombre'])),
                ft.DataCell(ft.Text(p['categoria'])),
                ft.DataCell(ft.Text(attrs, size=12)),
                ft.DataCell(ft.Text(f"{numero(p['stock'])} {p['unidad']}")),
                ft.DataCell(ft.Text(dinero(p['precio_venta']))),
                ft.DataCell(ft.Text('BAJO' if bajo else 'OK', color='#FFB46B' if bajo else VERDE)),
                ft.DataCell(ft.OutlinedButton('Editar', on_click=lambda _, pid=p['id']: editor(pid))),
            ]))
        tabla = ft.DataTable(columns=[ft.DataColumn(ft.Text(t)) for t in
            ['Código', 'Nombre', 'Categoría', 'Características', 'Stock', 'Precio venta', 'Estado', '']], rows=filas)
        contenido.controls = [cabecera('Productos'), campos_producto(cats),
                             ft.Text('Inventario', size=18, weight=ft.FontWeight.BOLD),
                             ft.Row([buscar, ft.OutlinedButton('Buscar',
                                    on_click=lambda _: productos(buscar.value or ''))], wrap=True),
                             ft.Text(f'{len(lista)} resultados (máximo 300)', color=TEXTO_SUAVE),
                             ft.Row([tabla], scroll=ft.ScrollMode.AUTO)]
        page.update()

    def movimientos():
        hist = api.movimientos()
        codigo = ft.TextField(label='Buscar código del producto', hint_text='CAB-001', width=205)
        seleccionado = [None]
        info = ft.Text('Ingresá el código y presioná Seleccionar.', color=TEXTO_SUAVE)
        tipo = ft.Dropdown(label='Tipo', value='entrada', options=[opt('entrada'), opt('salida')], width=150)
        presentacion = ft.Dropdown(label='Cantidad expresada en', options=[opt('base', 'Unidad base')],
                                   value='base', width=265)
        cantidad = ft.TextField(label='Cantidad', hint_text='100', width=175)
        motivo = ft.TextField(label='Motivo', value='Compra', width=230)
        responsable = ft.TextField(label='Responsable', value='Operador', width=190)
        vista_conversion = ft.Text('Seleccioná un producto.', color=VERDE)

        def actualizar_conversion(_=None):
            p = seleccionado[0]
            if not p:
                return
            env = next((x for x in p['presentaciones'] if str(x['id']) == presentacion.value), None)
            if env:
                vista_conversion.value = (f"{numero(cantidad.value or 0)} × {numero(env['factor'])} "
                                          f"= {conversion(cantidad.value or 0, env['factor'])} {p['unidad']}")
            else:
                vista_conversion.value = f"Cantidad base: {numero(cantidad.value or 0)} {p['unidad']}"
            page.update()

        def seleccionar(_):
            try:
                coincidencias = api.productos((codigo.value or '').strip())
                p = next((x for x in coincidencias if x['codigo'] == (codigo.value or '').strip().upper()), None)
                if not p:
                    aviso('Código inexistente. Primero creá ese producto.', True)
                    return
                seleccionado[0] = p
                info.value = f"{p['nombre']} · Stock: {numero(p['stock'])} {p['unidad']}"
                presentacion.options = [opt('base', f"Unidad base: {p['unidad']}")] + [
                    opt(x['id'], f"{x['nombre']} ({numero(x['factor'])} {p['unidad']})")
                    for x in p['presentaciones']]
                presentacion.value = 'base'
                actualizar_conversion()
            except api.ApiError as exc:
                api_error(exc)

        codigo.on_submit = seleccionar
        cantidad.on_change = actualizar_conversion
        presentacion.on_select = actualizar_conversion

        def guardar(_):
            p = seleccionado[0]
            if not p:
                aviso('Seleccioná un producto antes de registrar.', True)
                return
            try:
                body = {'producto_id': p['id'], 'tipo': tipo.value,
                        'cantidad': (cantidad.value or '').replace(',', '.'),
                        'motivo': motivo.value or '', 'responsable': responsable.value or ''}
                if presentacion.value != 'base':
                    body['presentacion_id'] = int(presentacion.value)
                mov = api.registrar_movimiento(body)
                aviso(f"Movimiento registrado: {numero(mov['cantidad'])} {mov['unidad_base']}")
                movimientos()  # refrescar historial y selector para no mostrar stock viejo
            except api.ApiError as exc:
                api_error(exc)

        filas = []
        for m in hist:
            expresado = (f"{numero(m['cantidad_original'])} {m['presentacion_nombre']} → "
                         if m.get('presentacion_nombre') else '')
            filas.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(m['id']))),
                ft.DataCell(ft.Text(m['codigo_producto'])),
                ft.DataCell(ft.Text(m['nombre_producto'])),
                ft.DataCell(ft.Text(m['tipo'])),
                ft.DataCell(ft.Text(f"{expresado}{numero(m['cantidad'])} {m['unidad_base']}")),
                ft.DataCell(ft.Text(m['motivo'])),
                ft.DataCell(ft.Text(fecha_local(m['fecha']))),
            ]))
        tabla = ft.DataTable(columns=[ft.DataColumn(ft.Text(t)) for t in
            ['ID', 'Código', 'Producto', 'Tipo', 'Cantidad', 'Motivo', 'Fecha (Argentina)']], rows=filas)
        contenido.controls = [cabecera('Movimientos'),
            bloque([ft.Text('Registrar entrada o salida', size=18, weight=ft.FontWeight.BOLD),
                    ft.Row([codigo, ft.OutlinedButton('Seleccionar', on_click=seleccionar)], wrap=True),
                    info,
                    ft.Row([tipo, presentacion, cantidad, motivo, responsable], wrap=True),
                    vista_conversion,
                    ft.FilledButton('Registrar movimiento', on_click=guardar),
                    ft.Text('Rollos/cajas completos: número entero. Los metros permiten decimales. No admite stock negativo.',
                            color=TEXTO_SUAVE, size=12)]),
            ft.Text('Últimos 40 movimientos', size=18, weight=ft.FontWeight.BOLD),
            ft.Row([tabla], scroll=ft.ScrollMode.AUTO)]
        page.update()

    def categorias():
        actuales = api.categorias()
        nombre = ft.TextField(label='Nombre de nueva categoría', width=345)
        campo_nombre = ft.TextField(label='Etiqueta del nuevo campo', width=260,
                                    hint_text='Ej.: Diámetro en mm')
        campo_tipo = ft.Dropdown(label='Tipo de campo', width=170, value='texto',
                                  options=[opt('texto'), opt('numero'), opt('opcion')])
        opciones = ft.TextField(label='Opciones separadas por coma (si es tipo opción)', width=375)
        pendientes = []
        lista_pendientes = ft.Column()

        def actualizar_lista():
            lista_pendientes.controls = [ft.Text(
                f"• {x['etiqueta']} ({x['tipo']})" + (': ' + ', '.join(x['opciones']) if x['opciones'] else ''))
                for x in pendientes]
            page.update()

        def agregar_campo(_):
            label = (campo_nombre.value or '').strip()
            key = slug(label)
            if not key:
                aviso('Escribí el nombre del campo técnico.', True)
                return
            if any(x['clave'] == key for x in pendientes):
                aviso('Ese campo ya está agregado.', True)
                return
            tipo_elegido = campo_tipo.value or 'texto'
            lista_opciones = [x.strip() for x in (opciones.value or '').split(',') if x.strip()]
            if tipo_elegido == 'opcion' and not lista_opciones:
                aviso('Ingresá las opciones separadas por coma.', True)
                return
            pendientes.append({'clave': key, 'etiqueta': label, 'tipo': tipo_elegido,
                               'ayuda': '', 'opciones': lista_opciones if tipo_elegido == 'opcion' else []})
            campo_nombre.value = ''
            opciones.value = ''
            actualizar_lista()

        def guardar_categoria(_):
            try:
                api.crear_categoria({'nombre': nombre.value or '', 'campos': pendientes})
                aviso('Categoría creada; aparecerá en Nuevo producto.')
                categorias()
            except api.ApiError as exc:
                api_error(exc)

        panel_crear = bloque([
            ft.Text('Crear categoría', size=18, weight=ft.FontWeight.BOLD), nombre,
            ft.Text('Agregá los campos técnicos que aparecerán al crear productos.'),
            ft.Row([campo_nombre, campo_tipo, opciones,
                    ft.OutlinedButton('Agregar campo', on_click=agregar_campo)], wrap=True),
            lista_pendientes,
            ft.FilledButton('Guardar categoría', on_click=guardar_categoria),
            ft.Text('Por seguridad, las categorías existentes no se renombran ni borran en esta versión.',
                    color=TEXTO_SUAVE, size=12),
        ])
        tarjetas = [ft.Container(content=ft.Column([
            ft.Text(c['nombre'], weight=ft.FontWeight.BOLD),
            ft.Text(', '.join(x['etiqueta'] for x in c['campos']) or 'Sin campos especiales',
                    size=12, color=TEXTO_SUAVE)], spacing=6),
            padding=12, bgcolor=PANEL, border_radius=8, width=360) for c in actuales]
        contenido.controls = [cabecera('Categorías'), panel_crear,
                             ft.Text('Categorías disponibles', size=18, weight=ft.FontWeight.BOLD),
                             ft.Row(tarjetas, wrap=True, spacing=10)]
        page.update()

    cab = ft.Row([ft.Text('⚡ ELECTROSTOCK', size=25, color=VERDE, weight=ft.FontWeight.BOLD),
                  ft.Text('v1.2 · Desarrollo local', color=TEXTO_SUAVE, size=12)], wrap=True)
    nav = ft.Row(wrap=True, spacing=9)
    page.add(cab, nav, ft.Divider(), contenido)
    ir('Inicio')


if __name__ == '__main__':
    ft.run(main)
