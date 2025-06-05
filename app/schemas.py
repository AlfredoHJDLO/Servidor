# app/schemas.py (Actualizado para el carrito preliminar)
from pydantic import BaseModel, Field, EmailStr
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

class PaletaResponse(PaletaBase):
    id: int
    class Config:
        orm_mode = True

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

class CartItemCreate(BaseModel):
    user_id: int
    quantity: int

    # Opcional si es una paleta fija
    paleta_id: Optional[int] = None

    # Requerido si es personalizada
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    ingredientes: Optional[str] = None
    precio: Optional[float] = None
    imagen_url: Optional[str] = None
    tiene_oferta: Optional[bool] = False
    texto_oferta: Optional[str] = None

    class Config:
        orm_mode = True

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
    paleta_id: Optional[int]
    quantity: int
    nombre: str
    descripcion: Optional[str]
    ingredientes: Optional[str]
    precio: float
    imagen_url: Optional[str]
    tiene_oferta: Optional[bool]
    texto_oferta: Optional[str]
    subtotal: float

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, example="usuario123")
    email: EmailStr
    password: str = Field(..., min_length=6, example="password123")
    is_admin: bool = Field(True, example=True)
    class Config:
        orm_mode = True

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
