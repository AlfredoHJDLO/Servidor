# app/models.py (Actualizado para el carrito preliminar)
from sqlalchemy import Column, Integer, String, DECIMAL, Boolean, Text, TIMESTAMP, ForeignKey, DateTime, Float
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

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False)
    username = Column(String(255), nullable=True)
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    attended = Column(Boolean, default=False)  # <-- campo para marcar atendido

    user = relationship("User", back_populates="orders")
    # Opcional: relacionar con detalles del pedido (items)
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    
class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    paleta_id = Column(Integer, nullable=True)  # puede ser NULL si es paleta personalizada
    quantity = Column(Integer, nullable=False)
    nombre = Column(String(255), nullable=False)
    descripcion = Column(String(255), nullable=True)
    ingredientes = Column(String(255), nullable=True)
    precio = Column(Float, nullable=False)
    imagen_url = Column(String(255), nullable=True)

    order = relationship("Order", back_populates="items")
