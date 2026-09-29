"""Contratos HTTP de ElectroStock v1.2. Compatible con payloads de v1.1."""
from datetime import datetime
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator

TipoCampo = Literal['texto', 'numero', 'opcion']


class CampoTecnico(BaseModel):
    model_config = ConfigDict(extra='forbid')
    clave: str = Field(min_length=1, max_length=50, pattern=r'^[a-z][a-z0-9_]*$')
    etiqueta: str = Field(min_length=1, max_length=70)
    tipo: TipoCampo = 'texto'
    ayuda: str = Field(default='', max_length=120)
    opciones: list[str] = Field(default_factory=list, max_length=25)

    @field_validator('etiqueta')
    @classmethod
    def sin_vacio(cls, valor):
        if not valor.strip():
            raise ValueError('La etiqueta no puede quedar vacía.')
        return valor.strip()


class CategoriaCrear(BaseModel):
    model_config = ConfigDict(extra='forbid')
    nombre: str = Field(min_length=1, max_length=70)
    campos: list[CampoTecnico] = Field(default_factory=list, max_length=20)

    @field_validator('nombre')
    @classmethod
    def nombre_real(cls, valor):
        if not valor.strip():
            raise ValueError('Ingresá el nombre de la categoría.')
        return valor.strip()


class CategoriaLeer(CategoriaCrear):
    model_config = ConfigDict(from_attributes=True)
    id: int


class PresentacionCrear(BaseModel):
    model_config = ConfigDict(extra='forbid')
    nombre: str = Field(min_length=1, max_length=60)
    factor: Decimal = Field(gt=0, max_digits=12, decimal_places=3)

    @field_validator('nombre')
    @classmethod
    def nombre_real(cls, valor):
        if not valor.strip():
            raise ValueError('Ingresá un nombre de presentación.')
        return valor.strip()


class PresentacionLeer(PresentacionCrear):
    model_config = ConfigDict(from_attributes=True)
    id: int
    producto_id: int


class ProductoBase(BaseModel):
    model_config = ConfigDict(extra='forbid')
    codigo: str = Field(min_length=1, max_length=40)
    nombre: str = Field(min_length=1, max_length=120)
    categoria: str = Field(min_length=1, max_length=70)
    marca: str = Field(default='', max_length=70)
    especificacion: str = Field(default='', max_length=1000)
    unidad: str = Field(default='unidad', min_length=1, max_length=20)
    stock_minimo: Decimal = Field(default=Decimal('0'), ge=0, max_digits=12, decimal_places=3)
    precio_compra: Decimal = Field(default=Decimal('0'), ge=0, max_digits=12, decimal_places=2)
    precio_venta: Decimal = Field(default=Decimal('0'), ge=0, max_digits=12, decimal_places=2)
    atributos_tecnicos: dict[str, str] = Field(default_factory=dict)

    @field_validator('codigo', 'nombre', 'categoria', 'unidad')
    @classmethod
    def requeridos(cls, valor):
        if not valor.strip():
            raise ValueError('No puede quedar vacío.')
        return valor.strip()

    @field_validator('marca', 'especificacion')
    @classmethod
    def sin_espacios(cls, valor):
        return valor.strip()

    @field_validator('codigo')
    @classmethod
    def codigo_normalizado(cls, valor):
        return valor.strip().upper()


class ProductoCrear(ProductoBase):
    pass


class ProductoActualizar(BaseModel):
    model_config = ConfigDict(extra='forbid')
    nombre: str | None = Field(default=None, min_length=1, max_length=120)
    categoria: str | None = Field(default=None, min_length=1, max_length=70)
    marca: str | None = Field(default=None, max_length=70)
    especificacion: str | None = Field(default=None, max_length=1000)
    unidad: str | None = Field(default=None, min_length=1, max_length=20)
    stock_minimo: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=3)
    precio_compra: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    precio_venta: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    atributos_tecnicos: dict[str, str] | None = None

    @field_validator('nombre', 'categoria', 'unidad')
    @classmethod
    def no_vacio(cls, valor):
        if valor is not None and not valor.strip():
            raise ValueError('No puede quedar vacío.')
        return valor.strip() if valor is not None else valor

    @field_validator('marca', 'especificacion')
    @classmethod
    def trim(cls, valor):
        return valor.strip() if valor is not None else valor


class ProductoLeer(ProductoBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    stock: Decimal
    creado_en: datetime
    presentaciones: list[PresentacionLeer] = Field(default_factory=list)


class MovimientoCrear(BaseModel):
    model_config = ConfigDict(extra='forbid')
    producto_id: int = Field(gt=0)
    tipo: Literal['entrada', 'salida']
    # Sin presentacion_id: cantidad en unidad base. Con presentacion_id: cantidad en envases.
    cantidad: Decimal = Field(gt=0, max_digits=12, decimal_places=3)
    presentacion_id: int | None = Field(default=None, gt=0)
    motivo: str = Field(min_length=1, max_length=200)
    responsable: str = Field(default='Operador', min_length=1, max_length=80)

    @field_validator('motivo', 'responsable')
    @classmethod
    def sin_vacio(cls, valor):
        if not valor.strip():
            raise ValueError('No puede quedar vacío.')
        return valor.strip()


class MovimientoLeer(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    producto_id: int
    tipo: Literal['entrada', 'salida']
    cantidad: Decimal  # valor en unidad base, compatible con v1.1
    motivo: str
    responsable: str
    fecha: datetime
    codigo_producto: str
    nombre_producto: str
    unidad_base: str
    cantidad_original: Decimal | None = None
    presentacion_nombre: str | None = None
    factor_conversion: Decimal | None = None
