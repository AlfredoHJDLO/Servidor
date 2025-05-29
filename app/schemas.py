# app/schemas.py (Actualizado para el carrito preliminar)
from pydantic import BaseModel, Field
from typing import Optional, List
import datetime

class PaletaBase(BaseModel):
    nombre: str = Field(..., example="Paleta Fresa Delicia")
    descripcion: Optional[str] = Field(None, example="Una refrescante paleta de fresa natural.")
    ingredientes: Optional[str] = Field(None, example="Fresa, azúcar, agua")
    precio: float = Field(..., gt=0, example=25.00)
    imagen_url: Optional[str] = Field(None, example="/static/images/fresa.png")
    tiene_oferta: bool = Field(False, example=True)
    texto_oferta: Optional[str] = Field(None, example="3 x 2")

class PaletaCreate(PaletaBase):
    pass

class PaletaInDB(PaletaBase):
    id: int = Field(..., example=1)
    fecha_creacion: Optional[datetime.datetime] = None
    fecha_actualizacion: Optional[datetime.datetime] = None

    class Config:
        orm_mode = True


# --- Esquema para la respuesta del carrito de un usuario ---
class CartItemBase(BaseModel):
    user_id: int = Field(..., example=1, description="ID del usuario (fijo por ahora).")
    paleta_id: int = Field(..., example=1, description="ID de la paleta en el carrito.")
    quantity: int = Field(..., gt=0, example=1, description="Cantidad de la paleta en el carrito.")

class CartItemCreate(CartItemBase):
    pass

class PaletaOut(BaseModel):
    id: int
    nombre: str
    precio: float
    imagen_url: Optional[str]

    class Config:
        orm_mode = True

class CartItemInDB(BaseModel):
    id: int
    user_id: int
    quantity: int
    paleta: PaletaOut
    subtotal: float

    class Config:
        orm_mode = True
