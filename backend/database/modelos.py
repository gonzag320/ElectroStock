"""Tablas: columnas v1.1 intactas; v1.2 suma características y presentaciones."""
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, JSON, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .conexion import Base


class Producto(Base):
    __tablename__ = 'productos'
    __table_args__ = (
        CheckConstraint('stock >= 0', name='ck_productos_stock_no_negativo'),
        CheckConstraint('stock_minimo >= 0', name='ck_productos_minimo_no_negativo'),
        CheckConstraint('precio_compra >= 0', name='ck_precio_compra_no_negativo'),
        CheckConstraint('precio_venta >= 0', name='ck_precio_venta_no_negativo'),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(40), unique=True, index=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    categoria: Mapped[str] = mapped_column(String(70), nullable=False)
    marca: Mapped[str] = mapped_column(String(70), default='', nullable=False)
    especificacion: Mapped[str] = mapped_column(Text, default='', nullable=False)
    unidad: Mapped[str] = mapped_column(String(20), default='unidad', nullable=False)
    stock: Mapped[Decimal] = mapped_column(Numeric(12, 3), default=Decimal('0'), nullable=False)
    stock_minimo: Mapped[Decimal] = mapped_column(Numeric(12, 3), default=Decimal('0'), nullable=False)
    precio_compra: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal('0'), nullable=False)
    precio_venta: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal('0'), nullable=False)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    # JSON genérico permite PostgreSQL y SQLite de pruebas. Nunca sobreescribir el campo
    # 'especificacion' antiguo: los registros v1.1 siguen siendo legibles.
    atributos_tecnicos: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    movimientos: Mapped[list['Movimiento']] = relationship(back_populates='producto')
    presentaciones: Mapped[list['Presentacion']] = relationship(back_populates='producto', order_by='Presentacion.id')


class Categoria(Base):
    __tablename__ = 'categorias'
    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(70), unique=True, nullable=False)
    # [{clave, etiqueta, tipo, ayuda, opciones}]; editables para nuevas categorías.
    campos: Mapped[list] = mapped_column(JSON, default=list, nullable=False)


class Presentacion(Base):
    __tablename__ = 'presentaciones'
    __table_args__ = (
        UniqueConstraint('producto_id', 'nombre', name='uq_presentacion_producto_nombre'),
        CheckConstraint('factor > 0', name='ck_presentacion_factor_positivo'),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    producto_id: Mapped[int] = mapped_column(ForeignKey('productos.id', ondelete='RESTRICT'), nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(60), nullable=False)
    factor: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    producto: Mapped[Producto] = relationship(back_populates='presentaciones')


class Movimiento(Base):
    __tablename__ = 'movimientos'
    __table_args__ = (
        CheckConstraint('cantidad > 0', name='ck_mov_cantidad_positiva'),
        CheckConstraint("tipo IN ('entrada', 'salida')", name='ck_mov_tipo_valido'),
        Index('ix_movimientos_fecha', 'fecha'),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    producto_id: Mapped[int] = mapped_column(ForeignKey('productos.id', ondelete='RESTRICT'), nullable=False, index=True)
    tipo: Mapped[str] = mapped_column(String(10), nullable=False)
    cantidad: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)  # SIEMPRE en unidad base
    motivo: Mapped[str] = mapped_column(String(200), nullable=False)
    responsable: Mapped[str] = mapped_column(String(80), default='Operador', nullable=False)
    fecha: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    # NULL para todos los movimientos v1.1; históricos se conservan intactos.
    cantidad_original: Mapped[Decimal | None] = mapped_column(Numeric(12, 3), nullable=True)
    presentacion_nombre: Mapped[str | None] = mapped_column(String(60), nullable=True)
    factor_conversion: Mapped[Decimal | None] = mapped_column(Numeric(12, 3), nullable=True)
    producto: Mapped[Producto] = relationship(back_populates='movimientos')
