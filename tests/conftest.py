"""Base aislada; la suite nunca usa el PostgreSQL del usuario."""
import os
import tempfile
from pathlib import Path

_pruebas = tempfile.TemporaryDirectory(prefix='electrostock_v12_')
os.environ['DATABASE_URL'] = 'sqlite+pysqlite:///' + str(Path(_pruebas.name) / 'suite.db')
