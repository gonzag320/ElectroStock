"""
ALTER de columnas nuevas; el código es idempotente para instalación en PC local.
IMPORTANTE: ejecutar previamente pg_dump y guardar el respaldo fuera de la PC.
"""
from sqlalchemy import inspect, select, text
from sqlalchemy.orm import Session
from backend.catalogo import PREDEFINIDAS
from .conexion import Base, engine
from . import modelos  # noqa: F401
from .modelos import Categoria, Producto


def preparar_base():
    Base.metadata.create_all(bind=engine)
    
    with engine.begin() as conn:
        inspector = inspect(conn)
        cols_producto = {c['name'] for c in inspector.get_columns('productos')}
        if 'atributos_tecnicos' not in cols_producto:
            
            conn.execute(text("ALTER TABLE productos ADD COLUMN atributos_tecnicos JSON DEFAULT '{}' NOT NULL"))
        cols_mov = {c['name'] for c in inspector.get_columns('movimientos')}
        
        if 'cantidad_original' not in cols_mov:
            conn.execute(text('ALTER TABLE movimientos ADD COLUMN cantidad_original NUMERIC(12,3)'))
        if 'presentacion_nombre' not in cols_mov:
            
            conn.execute(text('ALTER TABLE movimientos ADD COLUMN presentacion_nombre VARCHAR(60)'))
        if 'factor_conversion' not in cols_mov:
            
            conn.execute(text('ALTER TABLE movimientos ADD COLUMN factor_conversion NUMERIC(12,3)'))
    
    with Session(engine) as db:
        guardadas = {v.casefold() for v in db.scalars(select(Categoria.nombre)).all()}
        for nombre, campos in PREDEFINIDAS.items():
            if nombre.casefold() not in guardadas:
                db.add(Categoria(nombre=nombre, campos=campos))
                guardadas.add(nombre.casefold())
        db.flush()
        for nombre in db.scalars(select(Producto.categoria).distinct()).all():
            if nombre.casefold() not in guardadas:
                db.add(Categoria(nombre=nombre, campos=[]))
                guardadas.add(nombre.casefold())
        db.commit()
