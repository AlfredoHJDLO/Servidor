# app/models.py (Actualizado para el carrito preliminar)
from sqlalchemy import Column, Integer, String, DECIMAL, Boolean, Text, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Paleta(Base):
    __tablename__ = "paletas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=True)
    ingredientes = Column(Text, nullable=True)
    precio = Column(DECIMAL(10, 2), nullable=False)
    imagen_url = Column(String(255), nullable=True)
    tiene_oferta = Column(Boolean, default=False)
    texto_oferta = Column(String(100), nullable=True)
    fecha_creacion = Column(TIMESTAMP, server_default=func.now())
    fecha_actualizacion = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


    def __repr__(self):
        return f"<Paleta(id={self.id}, nombre='{self.nombre}', precio={self.precio})>"

# --- Nuevo modelo para el carrito preliminar ---

class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    paleta_id = Column(Integer, nullable=True)  # Puede ser null para personalizadas
    quantity = Column(Integer, nullable=False)
    added_at = Column(TIMESTAMP, server_default=func.now())

    # Datos de la paleta copiados (personalizada o fija)
    nombre = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=True)
    ingredientes = Column(Text, nullable=True)
    precio = Column(DECIMAL(10, 2), nullable=False)
    imagen_url = Column(String(255), nullable=True)
    tiene_oferta = Column(Boolean, default=False)
    texto_oferta = Column(String(100), nullable=True)

    @property
    def subtotal(self):
        return float(self.quantity) * float(self.precio)
