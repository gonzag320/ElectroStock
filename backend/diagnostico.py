"""Chequeo local de configuración y servidor PostgreSQL antes de iniciar FastAPI."""
import sys
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError


def main() -> int:
    print('=== ELECTROSTOCK: comprobación de PostgreSQL ===', flush=True)
    try:
        from backend.database.conexion import engine
    except (RuntimeError, ValueError, ImportError, ModuleNotFoundError) as exc:
        print(f'ERROR DE CONFIGURACION: {exc}', flush=True)
        print('Revisá backend\\.env (especialmente DB_PASSWORD).', flush=True)
        return 1

    try:
        with engine.connect() as conexion:
            conexion.execute(text('SELECT 1'))
            if engine.dialect.name == 'postgresql':
                base = conexion.scalar(text('SELECT current_database()'))
                print(f'OK: conexión a PostgreSQL. Base de datos: {base}', flush=True)
            else:
                print('ATENCION: usás una base diferente de PostgreSQL.', flush=True)
        return 0
    except SQLAlchemyError as exc:
        original = getattr(exc, 'orig', None)
        # Mensaje práctico sin imprimir la URL ni credenciales.
        detalle = str(original or exc).split('\n')[0]
        print(f'ERROR: PostgreSQL no está disponible: {detalle}', flush=True)
        print('Comprobá PostgreSQL, la base electrostock_db y la contraseña en backend\\.env.', flush=True)
        return 2


if __name__ == '__main__':
    sys.exit(main())
