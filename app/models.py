# app/models.py (Actualizado para el carrito preliminar)
from sqlalchemy import Column, Integer, String, DECIMAL, Boolean, Text, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

# Primero define CartItem para asegurar que Paleta pueda referenciarlo
class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    paleta_id = Column(Integer, ForeignKey("paletas.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    added_at = Column(TIMESTAMP, server_default=func.now())

    # Relación con la tabla Paleta
    # Asegúrate que el 'back_populates' en Paleta apunte a 'cart_items' y no a 'cart_items_preliminar'
    paleta = relationship("Paleta", back_populates="cart_items") 

    def __repr__(self):
        return f"<CartItem(id={self.id}, user_id={self.user_id}, paleta_id={self.paleta_id}, quantity={self.quantity})>"

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

    # **¡CORREGIDO AQUÍ!** # Ahora la relación apunta correctamente a "CartItem" (el nombre de tu clase real)
    # Y el back_populates coincide con el nombre de la relación en CartItem
    cart_items = relationship("CartItem", back_populates="paleta") 

    def __repr__(self):
        return f"<Paleta(id={self.id}, nombre='{self.nombre}', precio={self.precio})>"