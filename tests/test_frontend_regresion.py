"""Regresión de la incidencia reportada, sin necesidad de abrir ventana."""
from pathlib import Path


def test_flet_10_sin_page_open():
    codigo = (Path(__file__).resolve().parents[1] / 'frontend' / 'main.py').read_text(encoding='utf8')
    assert 'page.open(' not in codigo.replace('page.open() fue retirado', '')
    assert 'page.show_dialog(ft.SnackBar(' in codigo


def test_flet_muestra_reintentar_cuando_api_falla():
    codigo = (Path(__file__).resolve().parents[1] / 'frontend' / 'main.py').read_text(encoding='utf8')
    assert 'Reintentar conexión' in codigo
    assert 'contenido.controls = [' in codigo


def test_flet_offline_y_reintento(monkeypatch):
    """Smoke test de lógica de UI sin abrir la ventana nativa de Flet."""
    import importlib
    import sys
    from types import SimpleNamespace
    from frontend.services import api

    class Control:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs
            self.controls = []

    class Page:
        def __init__(self):
            self.controls = []
            self.actualizaciones = 0

        def add(self, *controls):
            self.controls.extend(controls)

        def update(self):
            self.actualizaciones += 1

        def show_dialog(self, _):
            pass

    ft = SimpleNamespace(
        Page=Page,
        ThemeMode=SimpleNamespace(DARK='dark'),
        FontWeight=SimpleNamespace(BOLD='bold'),
        ScrollMode=SimpleNamespace(AUTO='auto'),
        run=lambda f: None,
    )
    for nombre in ['Text','Column','Row','Container','OutlinedButton',
                   'FilledButton','Divider','TextField','SnackBar','DataTable',
                   'DataCell','DataColumn','DataRow']:
        setattr(ft, nombre, Control)

    monkeypatch.setitem(sys.modules, 'flet', ft)
    monkeypatch.delitem(sys.modules, 'frontend.main', raising=False)
    view = importlib.import_module('frontend.main')
    estado = {'online': False}

    def panel():
        if not estado['online']:
            raise api.ApiError('No responde FastAPI')
        return {'cantidad_productos': 0, 'productos_stock_bajo': 0,
                'valor_inventario_costo': '0.00'}

    monkeypatch.setattr(api, 'panel', panel)
    monkeypatch.setattr(api, 'movimientos', lambda: [])
    pagina = Page()
    view.main(pagina)
    contenido = pagina.controls[-1]
    assert 'No se pudo conectar' in contenido.controls[0].args[0]
    estado['online'] = True
    contenido.controls[-1].kwargs['on_click'](None)
    assert contenido.controls[0].args[0][0].args[0] == 'Inicio'
    assert pagina.actualizaciones >= 2
    sys.modules.pop('frontend.main', None)
