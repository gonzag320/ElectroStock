from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from backend.database.conexion import get_db
from backend.database.modelos import Movimiento, Producto
from backend.schemas import MovimientoCrear, MovimientoLeer
from backend.services.inventario import registrar_movimiento

router = APIRouter(prefix='/api/movimientos', tags=['Movimientos'])


def preparar_movimiento(m: Movimiento, p: Producto):
    return {
        'id': m.id, 'producto_id': m.producto_id, 'tipo': m.tipo,
        'cantidad': m.cantidad, 'motivo': m.motivo, 'responsable': m.responsable,
        'fecha': m.fecha, 'codigo_producto': p.codigo, 'nombre_producto': p.nombre,
        'unidad_base': p.unidad, 'cantidad_original': m.cantidad_original,
        'presentacion_nombre': m.presentacion_nombre, 'factor_conversion': m.factor_conversion,
    }


@router.post('', status_code=201, response_model=MovimientoLeer)
def crear(datos: MovimientoCrear, db: Session = Depends(get_db)):
    movimiento = registrar_movimiento(db, datos)
    return preparar_movimiento(movimiento, db.get(Producto, movimiento.producto_id))


@router.get('', response_model=list[MovimientoLeer])
def listar(limite: int = Query(default=40, ge=1, le=200), db: Session = Depends(get_db)):
    stmt = (select(Movimiento, Producto).join(Producto, Producto.id == Movimiento.producto_id)
            .order_by(Movimiento.id.desc()).limit(limite))
    return [preparar_movimiento(m, p) for m, p in db.execute(stmt).all()]
