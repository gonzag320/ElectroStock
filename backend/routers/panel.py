from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from backend.database.conexion import get_db
from backend.database.modelos import Producto

router = APIRouter(tags=['Sistema'])


@router.get('/')
def inicio():
    return {'aplicacion': 'ElectroStock', 'version': '1.2', 'documentacion': '/docs'}


@router.get('/api/salud-db')
def salud_db(db: Session = Depends(get_db)):
    try:
        db.execute(text('SELECT 1'))
        nombre = db.scalar(text('SELECT current_database()')) if db.bind.dialect.name == 'postgresql' else 'SQLite (pruebas)'
        return {'estado': 'Conexión exitosa', 'base_de_datos': nombre}
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail='Base de datos no disponible.')


@router.get('/api/panel')
def panel(db: Session = Depends(get_db)):
    cantidad = db.scalar(select(func.count(Producto.id))) or 0
    bajo = db.scalar(select(func.count(Producto.id)).where(Producto.stock <= Producto.stock_minimo)) or 0
    # No sumar cantidades de unidades diferentes: valorizar stock a costo.
    productos = db.scalars(select(Producto)).all()
    valorizacion = sum((p.stock * p.precio_compra for p in productos), Decimal('0'))
    return {
        'cantidad_productos': cantidad,
        'productos_stock_bajo': bajo,
        'valor_inventario_costo': str(valorizacion.quantize(Decimal('0.01'))),
    }
