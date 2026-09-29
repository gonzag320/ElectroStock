"""Reglas de inventario; nunca sumar metros con unidades ni vender medias térmicas."""
from decimal import Decimal, InvalidOperation
from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from backend.database.modelos import Categoria

CONTINUAS = {'metro', 'metros', 'm', 'litro', 'litros', 'l', 'kg', 'kilogramo', 'kilogramos'}
UNIDADES = {'unidad', 'unidades', 'u', 'pieza', 'piezas'}


def clave_unidad(valor: str) -> str:
    clave = valor.strip().lower()
    if clave in CONTINUAS:
        return {'m': 'metros', 'metro': 'metros', 'metros': 'metros', 'l': 'litros', 'litro': 'litros',
                'litros': 'litros', 'kg': 'kg', 'kilogramo': 'kg', 'kilogramos': 'kg'}[clave]
    if clave in UNIDADES:
        return 'unidad'
    return clave  # Otras unidades se tratan como discretas por seguridad.


def validar_cantidad_base(cantidad: Decimal, unidad: str):
    if cantidad <= 0:
        raise HTTPException(422, detail='La cantidad debe ser mayor a cero.')
    if clave_unidad(unidad) not in {'metros', 'litros', 'kg'} and cantidad != cantidad.to_integral_value():
        raise HTTPException(422, detail=f'{unidad} se registra en cantidades enteras. Los decimales se permiten en metros, litros y kg.')
    if cantidad > Decimal('999999999.999'):
        raise HTTPException(422, detail='La cantidad supera el máximo permitido.')


def validar_minimo(minimo: Decimal, unidad: str):
    if clave_unidad(unidad) not in {'metros', 'litros', 'kg'} and minimo != minimo.to_integral_value():
        raise HTTPException(422, detail='El stock mínimo debe ser entero para productos por unidad.')


def validar_atributos(db: Session, categoria: str, atributos: dict[str, str]):
    registro = db.scalar(select(Categoria).where(func.lower(Categoria.nombre) == categoria.strip().lower()))
    if registro is None:
        raise HTTPException(422, detail='Seleccioná una categoría existente o creala en Categorías.')
    campos = {campo['clave']: campo for campo in (registro.campos or [])}
    extras = set(atributos) - set(campos)
    if extras:
        raise HTTPException(422, detail=f'Campos técnicos desconocidos para esta categoría: {", ".join(sorted(extras))}.')
    salida = {}
    for clave, valor in atributos.items():
        if not isinstance(valor, str):
            raise HTTPException(422, detail=f'El campo {clave} debe ser texto.')
        valor = valor.strip()
        if not valor:
            continue
        if len(valor) > 120:
            raise HTTPException(422, detail=f'El campo {clave} es demasiado largo.')
        campo = campos[clave]
        if campo['tipo'] == 'numero':
            try:
                numero = Decimal(valor.replace(',', '.'))
            except InvalidOperation:
                raise HTTPException(422, detail=f'{campo["etiqueta"]}: ingresá un número válido.')
            if not numero.is_finite() or numero <= 0:
                raise HTTPException(422, detail=f'{campo["etiqueta"]} debe ser positivo.')
            valor = format(numero, 'f')
        if campo['tipo'] == 'opcion' and valor.casefold() not in {x.casefold() for x in campo['opciones']}:
            raise HTTPException(422, detail=f'{campo["etiqueta"]}: elegí una opción permitida.')
        salida[clave] = valor
    return salida
