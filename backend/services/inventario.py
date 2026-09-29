"""Entradas/salidas atómicas; la conversión queda congelada en el historial."""
from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy import update
from sqlalchemy.orm import Session
from backend.database.modelos import Producto, Movimiento, Presentacion
from backend.schemas import MovimientoCrear
from backend.services.reglas import validar_cantidad_base


def registrar_movimiento(db: Session, datos: MovimientoCrear) -> Movimiento:
    producto = db.get(Producto, datos.producto_id)
    if producto is None:
        raise HTTPException(404, detail='Producto inexistente.')
    factor = Decimal('1')
    nombre = None
    if datos.presentacion_id is not None:
        presentacion = db.get(Presentacion, datos.presentacion_id)
        if presentacion is None or presentacion.producto_id != producto.id:
            raise HTTPException(422, detail='La presentación no pertenece a este producto.')
        factor = presentacion.factor
        nombre = presentacion.nombre
        # La presentación identifica envases o rollos completos, no mitades de cajas.
        if datos.cantidad != datos.cantidad.to_integral_value():
            raise HTTPException(422, detail='Los rollos y cajas deben registrarse en cantidades enteras.')

    base = datos.cantidad * factor
    validar_cantidad_base(base, producto.unidad)
    delta = base if datos.tipo == 'entrada' else -base
    consulta = update(Producto).where(Producto.id == datos.producto_id)
    if datos.tipo == 'salida':
        consulta = consulta.where(Producto.stock >= base)
    resultado = db.execute(consulta.values(stock=Producto.stock + delta))
    if resultado.rowcount != 1:
        db.rollback()
        raise HTTPException(409, detail='Stock insuficiente para la salida solicitada.')
    movimiento = Movimiento(
        producto_id=datos.producto_id, tipo=datos.tipo, cantidad=base,
        motivo=datos.motivo, responsable=datos.responsable,
        cantidad_original=datos.cantidad if nombre else None,
        presentacion_nombre=nombre, factor_conversion=factor if nombre else None,
    )
    db.add(movimiento)
    try:
        db.commit()
        db.refresh(movimiento)
    except Exception:
        db.rollback()
        raise
    return movimiento
