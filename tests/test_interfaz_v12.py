"""Recorre las pantallas Flet con controles simulados, sin instalar Flutter."""
import importlib
import sys
from types import SimpleNamespace


def test_interfaz_carga_formularios_y_menus(monkeypatch):
    from frontend.services import api

    class Control:
        def __init__(self, *args, **kw):
            self.args = args
            self.kwargs = kw
            self.controls = kw.get('controls', args[0] if args and isinstance(args[0], list) else [])
            self.value = kw.get('value')
            self.options = kw.get('options', [])
            self.on_click = kw.get('on_click')
            self.on_select = kw.get('on_select')
            self.on_change = kw.get('on_change')
            self.on_submit = kw.get('on_submit')

    class Page:
        def __init__(self):
            self.controls = []
            self.refrescos = 0
            self.mensajes = []
        def add(self, *args):
            self.controls.extend(args)
        def update(self):
            self.refrescos += 1
        def show_dialog(self, obj):
            self.mensajes.append(obj)

    fake = SimpleNamespace(Page=Page, ThemeMode=SimpleNamespace(DARK='dark'),
                           FontWeight=SimpleNamespace(BOLD='bold'),
                           ScrollMode=SimpleNamespace(AUTO='auto'), run=lambda main: None)
    for name in ['Text','Row','Column','Container','DataTable','DataCell','DataColumn','DataRow',
                 'FilledButton','OutlinedButton','Divider','TextField','Dropdown','DropdownOption','SnackBar']:
        setattr(fake, name, Control)
    monkeypatch.setitem(sys.modules, 'flet', fake)
    monkeypatch.delitem(sys.modules, 'frontend.main', raising=False)
    view = importlib.import_module('frontend.main')
    monkeypatch.setattr(api, 'panel', lambda: {'cantidad_productos': 1, 'productos_stock_bajo': 0,
                                             'valor_inventario_costo': '100.00'})
    monkeypatch.setattr(api, 'movimientos', lambda: [])
    monkeypatch.setattr(api, 'categorias', lambda: [{'id': 1, 'nombre': 'Cables', 'campos': [
        {'clave': 'seccion_mm2', 'etiqueta': 'Sección', 'tipo': 'numero', 'ayuda': '', 'opciones': []}]}])
    monkeypatch.setattr(api, 'productos', lambda q='': [])
    pagina = Page()
    view.main(pagina)
    nav = pagina.controls[1]
    contenido = pagina.controls[-1]
    assert len(nav.controls) == 4
    nav.controls[1].on_click(None)  # Productos
    assert len(contenido.controls) >= 5
    # Botón de nueva alta dentro del formulario.
    formulario = contenido.controls[1]
    form_column = formulario.kwargs['content']
    botones = form_column.controls[-1]
    assert botones.controls[0].args[0] == 'Crear producto'
    # Cambios en categoría regeneran campos sin destruir la pantalla.
    seccion_unidad = form_column.controls[2]
    select_categoria = seccion_unidad.controls[0]
    select_categoria.on_select(None)
    nav.controls[2].on_click(None)  # Movimientos
    assert 'Movimientos' == contenido.controls[0].args[0][0].args[0]
    nav.controls[3].on_click(None)  # Categorías
    assert 'Categorías' == contenido.controls[0].args[0][0].args[0]
    assert pagina.refrescos >= 5
    sys.modules.pop('frontend.main', None)
