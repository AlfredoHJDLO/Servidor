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

# --- Esquemas para el carrito preliminar ---

class CartItemCreate(BaseModel):
    """Esquema para añadir/actualizar un ítem en el carrito."""
    user_id: int = Field(..., example=1, description="ID del usuario (fijo por ahora).")
    paleta_id: int = Field(..., example=1, description="ID de la paleta a añadir/actualizar.")
    quantity: int = Field(..., gt=0, example=1, description="Cantidad de la paleta.")

class CartItemInDB(CartItemCreate):
    """Esquema para un ítem del carrito tal como se almacena/retorna de la DB."""
    id: int
    added_at: Optional[datetime.datetime] = None

    class Config:
        orm_mode = True

# Opcional: Si quieres un esquema para ver el carrito completo de un usuario
class UserCart(BaseModel):
    user_id: int
    items: List[CartItemInDB] # Lista de ítems en el carrito del usuario