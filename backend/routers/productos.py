from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload
from backend.database.conexion import get_db
from backend.database.modelos import Producto, Movimiento, Presentacion
from backend.schemas import ProductoCrear, ProductoActualizar, ProductoLeer
from backend.services.reglas import clave_unidad, validar_atributos, validar_minimo

router = APIRouter(prefix='/api/productos', tags=['Productos'])


@router.get('', response_model=list[ProductoLeer])
def listar(q: str = Query(default='', max_length=120), db: Session = Depends(get_db)):
    stmt = select(Producto).options(selectinload(Producto.presentaciones))
    if q.strip():
        # Escapar comodines SQL para que el buscador sea literal.
        filtro = '%' + q.strip().replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_') + '%'
        stmt = stmt.where(or_(Producto.codigo.ilike(filtro, escape='\\'),
                              Producto.nombre.ilike(filtro, escape='\\'),
                              Producto.categoria.ilike(filtro, escape='\\'),
                              Producto.marca.ilike(filtro, escape='\\')))
    return db.scalars(stmt.order_by(Producto.id.desc()).limit(300)).all()


@router.get('/{producto_id}', response_model=ProductoLeer)
def detalle(producto_id: int, db: Session = Depends(get_db)):
    producto = db.get(Producto, producto_id)
    if not producto:
        raise HTTPException(404, detail='Producto inexistente.')
    return producto


@router.post('', response_model=ProductoLeer, status_code=201)
def crear(datos: ProductoCrear, db: Session = Depends(get_db)):
    validar_minimo(datos.stock_minimo, datos.unidad)
    attrs = validar_atributos(db, datos.categoria, datos.atributos_tecnicos)
    producto = Producto(**{**datos.model_dump(exclude={'atributos_tecnicos'}), 'atributos_tecnicos': attrs})
    db.add(producto)
    try:
        db.commit()
        db.refresh(producto)
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, detail='Ese código ya existe.')
    return producto


@router.patch('/{producto_id}', response_model=ProductoLeer)
def actualizar(producto_id: int, datos: ProductoActualizar, db: Session = Depends(get_db)):
    producto = db.get(Producto, producto_id)
    if not producto:
        raise HTTPException(404, detail='Producto inexistente.')
    cambios = datos.model_dump(exclude_unset=True)
    nueva_unidad = cambios.get('unidad', producto.unidad)
    nueva_categoria = cambios.get('categoria', producto.categoria)
    if 'unidad' in cambios and clave_unidad(nueva_unidad) != clave_unidad(producto.unidad):
        # Una caja deja de ser comparable si cambiamos la unidad después de mover stock.
        historico = db.scalar(select(func.count(Movimiento.id)).where(Movimiento.producto_id == producto.id))
        empaques = db.scalar(select(func.count(Presentacion.id)).where(Presentacion.producto_id == producto.id))
        if historico or producto.stock or empaques:
            raise HTTPException(409, detail='No podés cambiar la unidad con stock, movimientos o presentaciones. Creá otro código de producto.')
    if 'stock_minimo' in cambios or 'unidad' in cambios:
        validar_minimo(cambios.get('stock_minimo', producto.stock_minimo), nueva_unidad)
    if 'categoria' in cambios and nueva_categoria != producto.categoria and 'atributos_tecnicos' not in cambios:
        # Si cambió categoría, no arrastrar atributos de la anterior.
        cambios['atributos_tecnicos'] = {}
    if 'atributos_tecnicos' in cambios and cambios['atributos_tecnicos'] is None:
        raise HTTPException(422, detail='Las características técnicas deben ser un objeto, no null.')
    if 'categoria' in cambios or 'atributos_tecnicos' in cambios:
        attrs = cambios.get('atributos_tecnicos', producto.atributos_tecnicos or {})
        cambios['atributos_tecnicos'] = validar_atributos(db, nueva_categoria, attrs)
    for clave, valor in cambios.items():
        setattr(producto, clave, valor)
    db.commit()
    db.refresh(producto)
    return producto
