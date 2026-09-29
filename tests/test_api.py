"""Pruebas funcionales de la API con SQLite temporal; NO toca PostgreSQL."""
from fastapi.testclient import TestClient  # noqa: E402
from backend.database.conexion import Base, engine  # noqa: E402
from backend.main import app  # noqa: E402


def producto(codigo='CAB-001'):
    return {
        'codigo': codigo, 'nombre': 'Cable unipolar 2,5 mm²',
        'categoria': 'Cables', 'marca': 'Prysmian',
        'unidad': 'metros', 'stock_minimo': '20',
        'precio_compra': '550', 'precio_venta': '800',
    }


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_sistema_y_conexion():
    with TestClient(app) as c:
        assert c.get('/').status_code == 200
        assert c.get('/api/salud-db').json()['estado'] == 'Conexión exitosa'


def test_alta_y_busqueda_y_codigo_unico():
    with TestClient(app) as c:
        creado = c.post('/api/productos', json=producto()).json()
        assert creado['codigo'] == 'CAB-001'
        assert float(creado['stock']) == 0
        assert len(c.get('/api/productos?q=Prysmian').json()) == 1
        assert c.post('/api/productos', json=producto()).status_code == 409
        assert c.get('/api/productos/999').status_code == 404


def test_entradas_salidas_rollback_si_insuficiente():
    with TestClient(app) as c:
        pid = c.post('/api/productos', json=producto()) .json()['id']
        mov = {'producto_id': pid, 'tipo': 'entrada', 'cantidad': '100.5',
               'motivo': 'Compra', 'responsable': 'Administrador'}
        assert c.post('/api/movimientos', json=mov).status_code == 201
        mov.update(tipo='salida', cantidad='15.250', motivo='Venta')
        assert c.post('/api/movimientos', json=mov).status_code == 201
        mov.update(cantidad='999')
        assert c.post('/api/movimientos', json=mov).status_code == 409
        assert float(c.get(f'/api/productos/{pid}').json()['stock']) == 85.25
        assert len(c.get('/api/movimientos').json()) == 2
        assert c.get('/api/panel').json()['valor_inventario_costo'] == '46887.50'


def test_validacion_y_edicion_sin_stock_directo():
    with TestClient(app) as c:
        assert c.post('/api/productos', json=producto('   ')).status_code == 422
        pid = c.post('/api/productos', json=producto()).json()['id']
        assert c.patch(f'/api/productos/{pid}', json={'precio_venta':'975.50'}).status_code == 200
        assert c.patch(f'/api/productos/{pid}', json={'stock':'500'}).status_code == 422
        assert float(c.get(f'/api/productos/{pid}').json()['stock']) == 0
        assert c.post('/api/movimientos', json={
            'producto_id':pid, 'tipo':'entrada','cantidad':'-1','motivo':'Compra',
        }).status_code == 422
