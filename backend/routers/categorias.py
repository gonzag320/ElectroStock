"""Catálogo editable de categorías con sus campos técnicos."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from backend.database.conexion import get_db
from backend.database.modelos import Categoria
from backend.schemas import CategoriaCrear, CategoriaLeer

router = APIRouter(prefix='/api/categorias', tags=['Categorías'])


@router.get('', response_model=list[CategoriaLeer])
def listar(db: Session = Depends(get_db)):
    return db.scalars(select(Categoria).order_by(Categoria.nombre)).all()


@router.post('', status_code=201, response_model=CategoriaLeer)
def crear(datos: CategoriaCrear, db: Session = Depends(get_db)):
    claves = [campo.clave for campo in datos.campos]
    if len(claves) != len(set(claves)):
        raise HTTPException(422, detail='No se pueden repetir nombres internos de campos.')
    for campo in datos.campos:
        if campo.tipo == 'opcion' and not campo.opciones:
            raise HTTPException(422, detail=f'Agregá opciones para {campo.etiqueta}.')
    if db.scalar(select(Categoria.id).where(func.lower(Categoria.nombre) == datos.nombre.lower())):
        raise HTTPException(409, detail='Ya existe una categoría con ese nombre.')
    obj = Categoria(nombre=datos.nombre, campos=[c.model_dump() for c in datos.campos])
    db.add(obj)
    try:
        db.commit()
        db.refresh(obj)
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, detail='La categoría ya existe.')
    return obj
