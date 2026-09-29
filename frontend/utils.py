"""Funciones puras para textos y previsualización, independientes de Flet."""
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
try:
    from zoneinfo import ZoneInfo
    HORA_LOCAL = ZoneInfo('America/Argentina/Buenos_Aires')
except Exception:  # Windows sin paquete tzdata
    HORA_LOCAL = timezone(timedelta(hours=-3))


def numero(valor):
    try:
        v = format(Decimal(str(valor)), 'f')
        return v.rstrip('0').rstrip('.') if '.' in v else v
    except (InvalidOperation, ValueError):
        return str(valor)


def dinero(valor):
    try:
        salida = f'{Decimal(str(valor)):,.2f}'
        return '$ ' + salida.replace(',', '_').replace('.', ',').replace('_', '.')
    except (InvalidOperation, ValueError):
        return str(valor)


def fecha_local(valor):
    try:
        fecha = datetime.fromisoformat(valor.replace('Z', '+00:00'))
        if fecha.tzinfo is None:
            fecha = fecha.replace(tzinfo=timezone.utc)
        return fecha.astimezone(HORA_LOCAL).strftime('%d/%m/%Y %H:%M')
    except (TypeError, ValueError):
        return str(valor)


def conversion(cantidad, factor):
    try:
        valor = Decimal(str(cantidad).replace(',', '.')) * Decimal(str(factor))
        return numero(valor)
    except (InvalidOperation, ValueError):
        return '—'


def atributos_resumen(datos, categoria):
    por_clave = {c['clave']: c['etiqueta'] for c in categoria.get('campos', [])}
    return ' · '.join(f'{por_clave.get(k,k)}: {v}' for k, v in (datos or {}).items()) or 'Sin características cargadas'
