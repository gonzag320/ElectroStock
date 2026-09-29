"""Configuración de SQLAlchemy. La contraseña nunca va dentro del código."""
import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv(Path(__file__).resolve().parents[1] / '.env')


def construir_url():
    # DATABASE_URL permite ejecutar pruebas aisladas con SQLite.
    if os.getenv('DATABASE_URL'):
        return os.environ['DATABASE_URL']
    clave = os.getenv('DB_PASSWORD')
    if not clave or clave == 'REEMPLAZAR_CON_TU_CONTRASENA':
        raise RuntimeError('Configura DB_PASSWORD en backend/.env (ver README.md).')
    return URL.create(
        'postgresql+psycopg2',
        username=os.getenv('DB_USER', 'postgres'),
        password=clave,
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', '5432')),
        database=os.getenv('DB_NAME', 'electrostock_db'),
    )


DB_URL = construir_url()
engine = create_engine(
    DB_URL,
    pool_pre_ping=True,
    connect_args={'check_same_thread': False} if str(DB_URL).startswith('sqlite') else {},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    with SessionLocal() as session:
        yield session
