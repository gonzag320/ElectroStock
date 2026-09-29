"""Factor: cantidad de unidades base contenidas en UNA presentación."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from backend.database.conexion import get_db
from backend.database.modelos import Producto, Presentacion
from backend.schemas import PresentacionCrear, PresentacionLeer
from backend.services.reglas import validar_cantidad_base

router = APIRouter(prefix='/api/productos', tags=['Presentaciones'])


@router.get('/{producto_id}/presentaciones', response_model=list[PresentacionLeer])
def listar(producto_id: int, db: Session = Depends(get_db)):
    if not db.get(Producto, producto_id):
        raise HTTPException(404, detail='Producto inexistente.')
    return db.scalars(select(Presentacion).where(Presentacion.producto_id == producto_id)
                      .order_by(Presentacion.id)).all()


@router.post('/{producto_id}/presentaciones', status_code=201, response_model=PresentacionLeer)
def crear(producto_id: int, datos: PresentacionCrear, db: Session = Depends(get_db)):
    producto = db.get(Producto, producto_id)
    if not producto:
        raise HTTPException(404, detail='Producto inexistente.')
    validar_cantidad_base(datos.factor, producto.unidad)
    if datos.factor <= 1:
        raise HTTPException(422, detail='La presentación debe equivaler a más de una unidad base.')
    obj = Presentacion(producto_id=producto_id, **datos.model_dump())
    db.add(obj)
    try:
        db.commit()
        db.refresh(obj)
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, detail='Ya existe una presentación con ese nombre para este producto.')
    return obj
