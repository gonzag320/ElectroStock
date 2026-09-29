"""Cliente HTTP: Flet NO almacena ni conoce la contraseña de PostgreSQL."""
import json
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / '.env')
BASE_URL = os.getenv('API_URL', 'http://127.0.0.1:8000').rstrip('/')


class ApiError(Exception):
    def __init__(self, texto: str, status: int | None = None):
        super().__init__(texto)
        self.status = status


def solicitud(metodo: str, ruta: str, datos: dict | None = None):
    cuerpo = None if datos is None else json.dumps(datos, ensure_ascii=False).encode('utf-8')
    req = Request(f'{BASE_URL}{ruta}', data=cuerpo, method=metodo,
                  headers={'Content-Type': 'application/json', 'Accept': 'application/json'})
    try:
        with urlopen(req, timeout=8) as respuesta:
            return json.loads(respuesta.read().decode('utf-8'))
    except HTTPError as error:
        try:
            mensaje = json.loads(error.read().decode('utf-8')).get('detail', 'Error de servidor.')
            if isinstance(mensaje, list):
                mensaje = '; '.join(str(item.get('msg', item)) for item in mensaje)
        except (ValueError, AttributeError):
            mensaje = f'Error HTTP {error.code}'
        raise ApiError(str(mensaje), error.code) from error
    except (URLError, TimeoutError, OSError) as error:
        raise ApiError(f'No se pudo conectar con FastAPI en {BASE_URL}. Verificá 02_INICIAR_BACKEND.bat.') from error


def panel():
    return solicitud('GET', '/api/panel')


def categorias():
    return solicitud('GET', '/api/categorias')


def crear_categoria(datos):
    return solicitud('POST', '/api/categorias', datos)


def productos(q=''):
    return solicitud('GET', '/api/productos?' + urlencode({'q': q}))


def producto(pid):
    return solicitud('GET', f'/api/productos/{pid}')


def crear_producto(datos):
    return solicitud('POST', '/api/productos', datos)


def editar_producto(pid, datos):
    return solicitud('PATCH', f'/api/productos/{pid}', datos)


def crear_presentacion(pid, datos):
    return solicitud('POST', f'/api/productos/{pid}/presentaciones', datos)


def movimientos():
    return solicitud('GET', '/api/movimientos')


def registrar_movimiento(datos):
    return solicitud('POST', '/api/movimientos', datos)
