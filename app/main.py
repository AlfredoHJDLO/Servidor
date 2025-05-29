# app/main.py (Actualizado para el carrito preliminar)
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from . import models, schemas
from .database import engine, get_db

# Crea las tablas en la base de datos si no existen
# Esto creará la tabla 'cart_items_preliminar' también
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Paletas Ternurin",
    description="API para gestionar el catálogo de paletas personalizadas y un carrito básico."
)

# --- Configuración CORS (mantener igual) ---
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Montar Directorio de Archivos Estáticos (mantener igual) ---
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- Endpoint para obtener todas las paletas (mantener igual) ---
@app.get(
    "/paletas/",
    response_model=List[schemas.PaletaInDB],
    summary="Obtener todas las paletas",
    description="Devuelve una lista de todas las paletas disponibles en el catálogo."
)
def read_paletas(db: Session = Depends(get_db)):
    paletas = db.query(models.Paleta).all()
    if not paletas:
        return []
    return paletas

# --- Endpoint para obtener una paleta por ID (mantener igual) ---
@app.get(
    "/paletas/{paleta_id}",
    response_model=schemas.PaletaInDB,
    summary="Obtener una paleta por ID",
    description="Devuelve la información detallada de una paleta específica."
)
def read_paleta(paleta_id: int, db: Session = Depends(get_db)):
    paleta = db.query(models.Paleta).filter(models.Paleta.id == paleta_id).first()
    if paleta is None:
        raise HTTPException(status_code=404, detail="Paleta no encontrada")
    return paleta


# --- Endpoint para crear una nueva paleta (mantener igual) ---
@app.post("/paletas/", response_model=schemas.PaletaInDB, status_code=status.HTTP_201_CREATED)
def create_paleta(paleta_data: schemas.PaletaCreate, db: Session = Depends(get_db)):
    # Verificar si ya existe una paleta con el mismo nombre
    existing_paleta = db.query(models.Paleta).filter(models.Paleta.nombre == paleta_data.nombre).first()
    if existing_paleta:
        raise HTTPException(status_code=400, detail="Ya existe una paleta con este nombre.")

    # Crear la nueva paleta
    new_paleta = models.Paleta(**paleta_data.model_dump())
    db.add(new_paleta)
    db.commit()
    db.refresh(new_paleta)
    return new_paleta

# --- NUEVOS ENDPOINTS PARA EL CARRITO PRELIMINAR ---
"""
@app.post(
    "/cart/add",
    response_model=schemas.CartItemInDB,
    status_code=status.HTTP_200_OK, # Puede ser 200 OK si actualiza, o 201 Created si es nuevo
    summary="Añadir o actualizar un ítem en el carrito",
    description="Añade una paleta al carrito del usuario. Si ya existe, actualiza la cantidad."
)
def add_to_cart(item_data: schemas.CartItemCreate, db: Session = Depends(get_db)):
    # 1. Verificar si la paleta existe
    paleta = db.query(models.Paleta).filter(models.Paleta.id == item_data.paleta_id).first()
    if not paleta:
        raise HTTPException(status_code=404, detail="Paleta no encontrada.")

    # 2. Buscar si el ítem ya está en el carrito para este usuario
    cart_item = db.query(models.CartItem).filter(
        models.CartItem.user_id == item_data.user_id,
        models.CartItem.paleta_id == item_data.paleta_id
    ).first()

    if cart_item:
        # Si ya existe, actualiza la cantidad
        cart_item.quantity = item_data.quantity
        db.add(cart_item)
        db.commit()
        db.refresh(cart_item)
        return cart_item
    else:
        # Si no existe, crea un nuevo ítem en el carrito
        new_cart_item = models.CartItem(
            user_id=item_data.user_id,
            paleta_id=item_data.paleta_id,
            quantity=item_data.quantity
        )
        db.add(new_cart_item)
        db.commit()
        db.refresh(new_cart_item)
        return new_cart_item
"""
@app.post("/cart/add", response_model=schemas.CartItemInDB)
def add_to_cart(item_data: schemas.CartItemCreate, db: Session = Depends(get_db)):
    paleta = db.query(models.Paleta).filter(models.Paleta.id == item_data.paleta_id).first()
    if not paleta:
        raise HTTPException(status_code=404, detail="Paleta no encontrada.")

    cart_item = db.query(models.CartItem).filter(
        models.CartItem.user_id == item_data.user_id,
        models.CartItem.paleta_id == item_data.paleta_id
    ).first()

    if cart_item:
        cart_item.quantity += item_data.quantity
    else:
        cart_item = models.CartItem(**item_data.model_dump())

    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)
    return cart_item


@app.get(
    "/cart/{user_id}",
    response_model=List[schemas.CartItemInDB],
    summary="Obtener ítems del carrito de un usuario",
    description="Devuelve todos los ítems en el carrito de un usuario específico."
)
def get_user_cart(user_id: int, db: Session = Depends(get_db)):
    cart_items = db.query(models.CartItem).filter(models.CartItem.user_id == user_id).all()
    return cart_items

@app.delete(
    "/cart/remove/{cart_item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un ítem del carrito",
    description="Elimina un ítem específico del carrito por su ID."
)
def remove_from_cart(cart_item_id: int, db: Session = Depends(get_db)):
    cart_item = db.query(models.CartItem).filter(models.CartItem.id == cart_item_id).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Ítem del carrito no encontrado.")
    db.delete(cart_item)
    db.commit()
    return JSONResponse(status_code=204, content={"message": "Ítem eliminado del carrito exitosamente."})

@app.patch("/cart/decrease", summary="Disminuir una unidad de una paleta del carrito")
def decrease_from_cart(user_id: int, paleta_id: int, db: Session = Depends(get_db)):
    cart_item = db.query(models.CartItem).filter(
        models.CartItem.user_id == user_id,
        models.CartItem.paleta_id == paleta_id
    ).first()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Ítem no encontrado en el carrito.")

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        db.commit()
        db.refresh(cart_item)
        return {"message": "Cantidad actualizada", "item": cart_item}
    else:
        db.delete(cart_item)
        db.commit()
        return {"message": "Ítem eliminado porque la cantidad llegó a cero."}
    
# (Puedes dejar el endpoint de orders/ si quieres mantenerlo para futuras implementaciones de checkout)
# @app.post(
#     "/orders/",
#     response_model=schemas.OrderInDB,
#     status_code=status.HTTP_201_CREATED,
#     summary="Crear una nueva orden de compra",
#     description="Registra una nueva orden con los ítems especificados."
# )
# async def create_order(order_data: schemas.OrderCreate, db: Session = Depends(get_db)):
#     # ... (código anterior para create_order) ...
#     pass # O borrar si no lo vas a usar por ahora.