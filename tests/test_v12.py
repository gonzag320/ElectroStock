"""Categorías técnicas, envases, transacciones, migración no destructiva."""
from decimal import Decimal
from pathlib import Path
import tempfile
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text, inspect, select
from sqlalchemy.orm import Session
from backend.database.conexion import Base, engine
from backend.database import migraciones
from backend.database.modelos import Producto, Presentacion
from backend.main import app
from frontend.utils import numero, conversion, fecha_local


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def producto(codigo='CAB-002', categoria='Cables', unidad='metros', attrs=None):
    return {'codigo': codigo, 'nombre': 'Cable de prueba' if categoria == 'Cables' else 'Dispositivo de prueba',
            'categoria': categoria, 'unidad': unidad, 'precio_compra': '25.50',
            'precio_venta': '50', 'stock_minimo': '10' if unidad == 'metros' else '2',
            'atributos_tecnicos': attrs if attrs is not None else {}}


def movimiento(pid, tipo, cantidad, presentacion_id=None):
    data = {'producto_id': pid, 'tipo': tipo, 'cantidad': cantidad, 'motivo': 'Prueba', 'responsable': 'Operador'}
    if presentacion_id:
        data['presentacion_id'] = presentacion_id
    return data


def test_catalogo_fabricacion_y_campos_variables():
    with TestClient(app) as c:
        cats = c.get('/api/categorias').json()
        assert any(x['nombre'] == 'Cables' and len(x['campos']) >= 3 for x in cats)
        p = c.post('/api/productos', json=producto(attrs={'seccion_mm2': '2,5', 'tipo_cable': 'Unipolar', 'color': 'Rojo'}))
        assert p.status_code == 201, p.text
        assert p.json()['atributos_tecnicos']['seccion_mm2'] == '2.5'
        assert p.json()['stock'] == '0.000'
        assert c.post('/api/productos', json=producto('CAB-003', attrs={'seccion_mm2': 'mal'})).status_code == 422
        assert c.post('/api/productos', json=producto('CAB-003', attrs={'tipo_cable': 'Inexistente'})).status_code == 422
        assert c.post('/api/productos', json=producto('CAB-003', attrs={'voltaje': '220'})).status_code == 422
        assert c.post('/api/productos', json=producto()).status_code == 409


def test_piezas_enteras_y_atributos_de_termica():
    with TestClient(app) as c:
        p = c.post('/api/productos', json=producto('TER-020', 'Termomagnéticas', 'unidad',
                  {'corriente_a': '20', 'polos': '2P', 'curva': 'C', 'poder_corte_ka': '6'}))
        assert p.status_code == 201, p.text
        pid = p.json()['id']
        assert c.post('/api/movimientos', json=movimiento(pid, 'entrada', '1.5')).status_code == 422
        assert c.post('/api/movimientos', json=movimiento(pid, 'entrada', '2')).status_code == 201
        assert c.post('/api/movimientos', json=movimiento(pid, 'salida', '0.5')).status_code == 422
        assert c.get(f'/api/productos/{pid}').json()['stock'] == '2.000'
        assert c.patch(f'/api/productos/{pid}', json={'stock_minimo': '0.5'}).status_code == 422


def test_rollos_conversion_y_snapshot_no_mutable():
    with TestClient(app) as c:
        pid = c.post('/api/productos', json=producto()).json()['id']
        env = c.post(f'/api/productos/{pid}/presentaciones', json={'nombre': 'Rollo 100 m', 'factor': '100'})
        assert env.status_code == 201, env.text
        eid = env.json()['id']
        alta = c.post('/api/movimientos', json=movimiento(pid, 'entrada', '2', eid))
        assert alta.status_code == 201, alta.text
        assert alta.json()['cantidad'] == '200.000'
        assert alta.json()['presentacion_nombre'] == 'Rollo 100 m'
        assert alta.json()['factor_conversion'] == '100.000'
        assert c.post('/api/movimientos', json=movimiento(pid, 'entrada', '0.5', eid)).status_code == 422
        salida = c.post('/api/movimientos', json=movimiento(pid, 'salida', '15.375'))
        assert salida.status_code == 201, salida.text
        assert salida.json()['cantidad_original'] is None
        assert float(c.get(f'/api/productos/{pid}').json()['stock']) == 184.625
        assert c.post('/api/movimientos', json=movimiento(pid, 'salida', '2', eid)).status_code == 409
        # Suponiendo cambio futuro del factor, el movimiento conserva el factor histórico.
        with Session(engine) as db:
            item = db.get(Presentacion, eid)
            item.factor = Decimal('120')
            db.commit()
        historico = c.get('/api/movimientos').json()
        mov_original = next(m for m in historico if m['id'] == alta.json()['id'])
        assert mov_original['factor_conversion'] == '100.000'
        assert mov_original['cantidad_original'] == '2.000'
        assert c.get('/api/panel').json()['valor_inventario_costo'] == '4707.94'


def test_presentaciones_son_del_producto_y_unidades_no_se_redefinen():
    with TestClient(app) as c:
        pid1 = c.post('/api/productos', json=producto()).json()['id']
        pid2 = c.post('/api/productos', json=producto('TER-002', 'Termomagnéticas', 'unidad')).json()['id']
        env = c.post(f'/api/productos/{pid1}/presentaciones', json={'nombre': 'Rollo', 'factor': '100'}).json()['id']
        assert c.post('/api/movimientos', json=movimiento(pid2, 'entrada', '2', env)).status_code == 422
        assert c.patch(f'/api/productos/{pid1}', json={'unidad': 'unidad'}).status_code == 409
        assert c.post(f'/api/productos/{pid2}/presentaciones', json={'nombre': 'Caja 10', 'factor': '2.5'}).status_code == 422
        caj = c.post(f'/api/productos/{pid2}/presentaciones', json={'nombre': 'Caja 10', 'factor': '10'})
        assert caj.status_code == 201
        assert c.post(f'/api/productos/{pid2}/presentaciones', json={'nombre': 'Caja 10', 'factor': '10'}).status_code == 409


def test_edicion_sin_perder_stock_y_categoria_personalizada():
    with TestClient(app) as c:
        categoria = {'nombre': 'Conectores especiales', 'campos': [
            {'clave': 'diametro_mm', 'etiqueta': 'Diámetro', 'tipo': 'numero'},
            {'clave': 'material', 'etiqueta': 'Material', 'tipo': 'opcion', 'opciones': ['Cobre', 'Aluminio']},
        ]}
        assert c.post('/api/categorias', json=categoria).status_code == 201
        assert c.post('/api/categorias', json=categoria).status_code == 409
        p = c.post('/api/productos', json=producto('CON-001', 'Conectores especiales', 'unidad',
                                                   {'diametro_mm': '12.7', 'material': 'Cobre'}))
        assert p.status_code == 201, p.text
        pid = p.json()['id']
        c.post('/api/movimientos', json=movimiento(pid, 'entrada', '10'))
        mod = c.patch(f'/api/productos/{pid}', json={'precio_venta': '70', 'marca': 'Nuevo fabricante'})
        assert mod.status_code == 200
        assert mod.json()['atributos_tecnicos']['material'] == 'Cobre'
        assert mod.json()['stock'] == '10.000'
        assert c.patch(f'/api/productos/{pid}', json={'unidad': 'metros'}).status_code == 409
        assert c.patch(f'/api/productos/{pid}', json={'stock': '999'}).status_code == 422
        assert c.patch(f'/api/productos/{pid}', json={'categoria': 'Otros'}).json()['atributos_tecnicos'] == {}
        assert len(c.get('/api/movimientos').json()) == 1


def test_migracion_old_schema_sin_perdida_y_repetible(monkeypatch, tmp_path):
    legacy = create_engine('sqlite+pysqlite:///' + str(tmp_path / 'legado.db'))
    # Simular las dos tablas antiguas y un producto real con un movimiento anterior.
    with legacy.begin() as conn:
        conn.execute(text('''CREATE TABLE productos (id INTEGER PRIMARY KEY, codigo VARCHAR(40),
            nombre VARCHAR(120), categoria VARCHAR(70), marca VARCHAR(70), especificacion TEXT,
            unidad VARCHAR(20), stock NUMERIC(12,3), stock_minimo NUMERIC(12,3),
            precio_compra NUMERIC(12,2), precio_venta NUMERIC(12,2), creado_en DATETIME)'''))
        conn.execute(text('''CREATE TABLE movimientos (id INTEGER PRIMARY KEY, producto_id INTEGER,
            tipo VARCHAR(10), cantidad NUMERIC(12,3), motivo VARCHAR(200),
            responsable VARCHAR(80), fecha DATETIME)'''))
        conn.execute(text('''INSERT INTO productos (id,codigo,nombre,categoria,marca,especificacion,unidad,stock,
            stock_minimo,precio_compra,precio_venta,creado_en) VALUES
            (1,'CAB-001','Cable previo','Cables','Prysmian','2,5mm rojo','metros',100,20,650,950,'2026-09-27')'''))
        conn.execute(text('''INSERT INTO movimientos (id,producto_id,tipo,cantidad,motivo,responsable,fecha)
            VALUES (1,1,'entrada',100,'Compra','Operador','2026-09-27')'''))
    monkeypatch.setattr(migraciones, 'engine', legacy)
    migraciones.preparar_base()
    migraciones.preparar_base()  # No recrea productos ni multiplica categorías.
    with legacy.connect() as conn:
        assert 'atributos_tecnicos' in {c['name'] for c in inspect(conn).get_columns('productos')}
        assert 'factor_conversion' in {c['name'] for c in inspect(conn).get_columns('movimientos')}
        assert conn.scalar(text('SELECT stock FROM productos WHERE id=1')) == 100
        assert conn.scalar(text('SELECT COUNT(*) FROM movimientos')) == 1
        assert conn.scalar(text('SELECT especificacion FROM productos WHERE id=1')) == '2,5mm rojo'
        assert conn.scalar(text('SELECT COUNT(*) FROM categorias WHERE nombre="Cables"')) == 1
        assert conn.scalar(text('SELECT COUNT(*) FROM presentaciones')) == 0


def test_formato_cantidad_y_hora():
    assert numero('100.000') == '100'
    assert numero('125.500') == '125.5'
    assert conversion('2', '100') == '200'
    assert '27/09/2026 15:42' == fecha_local('2026-09-27T18:42:00+00:00')
