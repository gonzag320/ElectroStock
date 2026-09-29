"""Base aislada; la suite nunca usa el PostgreSQL del usuario."""
import os
import tempfile
from pathlib import Path

_pruebas = tempfile.TemporaryDirectory(prefix='electrostock_v12_')
os.environ['DATABASE_URL'] = 'sqlite+pysqlite:///' + str(Path(_pruebas.name) / 'suite.db')

def pytest_sessionfinish(session, exitstatus):
    from backend.database.conexion import engine

    # Cerrar las conexiones disponibles
    # antes de eliminar la base temporal.
    engine.dispose()

    # Eliminar los archivos temporales.
    _pruebas.cleanup()