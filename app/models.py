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

    # Agregamos relación para ver qué items de carrito están asociados a esta paleta
    cart_items_preliminar = relationship("CartItemPreliminar", back_populates="paleta")

    def __repr__(self):
        return f"<Paleta(id={self.id}, nombre='{self.nombre}', precio={self.precio})>"

# --- Nuevo modelo para el carrito preliminar ---

class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    paleta_id = Column(Integer, ForeignKey("paletas.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    added_at = Column(TIMESTAMP, server_default=func.now())

    # Relación con la tabla Paleta
    paleta = relationship("Paleta", back_populates="cart_items")

    def __repr__(self):
        return f"<CartItem(id={self.id}, user_id={self.user_id}, paleta_id={self.paleta_id}, quantity={self.quantity})>"