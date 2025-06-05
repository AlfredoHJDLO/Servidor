# app/main.py (Actualizado para el carrito preliminar)
from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from .auth import get_current_active_user
from . import models, schemas
from .database import engine, get_db
from .users import users
from .auth import auth
# Crea las tablas en la base de datos si no existen
# Esto creará la tabla 'cart_items_preliminar' también
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Paletas Ternurin",
    description="API para gestionar el catálogo de paletas personalizadas y un carrito básico."
)

app.include_router(users, tags=["users"])
app.include_router(auth, tags=["auth"])

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

def verify_admin(user: models.User = Depends(get_current_active_user)):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="No autorizado")
    return user


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
def create_paleta(paleta_data: schemas.PaletaCreate, db: Session = Depends(get_db), admin: models.User = Depends(verify_admin)):
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

# *--- Endpoint para actualizar una paleta (mantener igual) ---
@app.put("/paletas/{paleta_id}", response_model=schemas.PaletaResponse)
def update_paleta(paleta_id: int, paleta_data: schemas.PaletaCreate, db: Session = Depends(get_db), admin: models.User = Depends(verify_admin)):
    # Buscar la paleta por ID
    paleta = db.query(models.Paleta).filter(models.Paleta.id == paleta_id).first()
    if not paleta:
        raise HTTPException(status_code=404, detail="Paleta no encontrada")

    # Actualizar los campos de la paleta
    for key, value in paleta_data.model_dump().items():
        setattr(paleta, key, value)

    db.commit()
    db.refresh(paleta)
    return paleta

# *--- Endpoint para eliminar una paleta (mantener igual) ---
@app.delete("/paletas/{paleta_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_paleta(paleta_id: int, db: Session = Depends(get_db), admin: models.User = Depends(verify_admin)):
    # Buscar la paleta por ID
    paleta = db.query(models.Paleta).filter(models.Paleta.id == paleta_id).first()
    if not paleta:
        raise HTTPException(status_code=404, detail="Paleta no encontrada")

    # Eliminar la paleta
    db.delete(paleta)
    db.commit()
    return JSONResponse(status_code=204, content={"message": "Paleta eliminada exitosamente."})

# * --- NUEVOS ENDPOINTS PARA EL CARRITO PRELIMINAR ---

@app.post("/cart/add", response_model=schemas.CartItemInDB)
def add_to_cart(item_data: schemas.CartItemCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    if item_data.paleta_id:
        # Paleta fija, obtener datos desde DB
        paleta = db.query(models.Paleta).filter(models.Paleta.id == item_data.paleta_id).first()
        if not paleta:
            raise HTTPException(status_code=404, detail="Paleta no encontrada.")
        
        nombre = paleta.nombre
        descripcion = paleta.descripcion
        ingredientes = paleta.ingredientes
        precio = float(paleta.precio)
        imagen_url = paleta.imagen_url
        tiene_oferta = paleta.tiene_oferta
        texto_oferta = paleta.texto_oferta
    else:
        # Paleta personalizada, datos vienen en item_data
        nombre = item_data.nombre
        descripcion = item_data.descripcion
        ingredientes = item_data.ingredientes
        precio = float(item_data.precio)
        imagen_url = item_data.imagen_url
        tiene_oferta = item_data.tiene_oferta or False
        texto_oferta = item_data.texto_oferta

    # Buscar si el ítem ya está en el carrito para este usuario y paleta (o personalizado)
    cart_item = db.query(models.CartItem).filter(
        models.CartItem.user_id == item_data.user_id,
        models.CartItem.paleta_id == item_data.paleta_id
    ).first()

    if cart_item:
        # Actualiza la cantidad y datos por si cambian
        cart_item.quantity += item_data.quantity
        cart_item.nombre = nombre
        cart_item.descripcion = descripcion
        cart_item.ingredientes = ingredientes
        cart_item.precio = precio
        cart_item.imagen_url = imagen_url
        cart_item.tiene_oferta = tiene_oferta
        cart_item.texto_oferta = texto_oferta
        db.add(cart_item)
        db.commit()
        db.refresh(cart_item)
    else:
        # Crear nuevo item carrito
        cart_item = models.CartItem(
            user_id=item_data.user_id,
            paleta_id=item_data.paleta_id,
            quantity=item_data.quantity,
            nombre=nombre,
            descripcion=descripcion,
            ingredientes=ingredientes,
            precio=precio,
            imagen_url=imagen_url,
            tiene_oferta=tiene_oferta,
            texto_oferta=texto_oferta
        )
        db.add(cart_item)
        db.commit()
        db.refresh(cart_item)

    # Calcular subtotal para la respuesta
    result = cart_item.__dict__.copy()
    result["subtotal"] = cart_item.quantity * cart_item.precio

    return result


@app.get(
    "/cart/{user_id}",
    response_model=List[schemas.CartItemInDB],
    summary="Obtener ítems del carrito de un usuario",
    description="Devuelve todos los ítems en el carrito de un usuario específico."
)
def get_user_cart(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    cart_items = db.query(models.CartItem).filter(models.CartItem.user_id == user_id).all()
    return cart_items

@app.delete(
    "/cart/remove/{cart_item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un ítem del carrito",
    description="Elimina un ítem específico del carrito por su ID."
)
def remove_from_cart(cart_item_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    cart_item = db.query(models.CartItem).filter(models.CartItem.id == cart_item_id).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Ítem del carrito no encontrado.")
    db.delete(cart_item)
    db.commit()
    return JSONResponse(status_code=204, content={"message": "Ítem eliminado del carrito exitosamente."})

@app.patch("/cart/decrease", summary="Disminuir una unidad de una paleta del carrito")
def decrease_from_cart(user_id: int, paleta_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
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

@app.delete("/cart/clear/{user_id}", summary="Limpiar el carrito de un usuario")
def clear_cart(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    cart_items = db.query(models.CartItem).filter(models.CartItem.user_id == user_id).all()
    if not cart_items:
        raise HTTPException(status_code=404, detail="Carrito vacío o no encontrado.")
    
    for item in cart_items:
        db.delete(item)
    
    db.commit()
    return JSONResponse(status_code=204, content={"message": "Carrito limpiado exitosamente."})

# * --- ENDPOINTS PARA PEDIDOS ---
# Lista pedidos (opcional filtro)
@app.get("/orders/all", response_model=List[schemas.OrderInDB])
def list_orders(attended: Optional[bool] = Query(None), db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    query = db.query(models.Order)
    if attended is not None:
        query = query.filter(models.Order.attended == attended)
    orders = query.all()
    return orders

# Opcionalmente (para el usuario). Detalle de un pedido.
@app.get("/orders/user/{order_id}", response_model=schemas.OrderInDB)
def get_order(order_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_active_user)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return order

# 3. Pedidos de un usuario
@app.get("/orders/user/{user_id}", response_model=List[schemas.OrderInDB])
def get_orders_by_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    orders = db.query(models.Order).filter(models.Order.user_id == user_id).all()
    return orders


"""
función o endpoint que permite al administrador (o quien tenga permiso) marcar un pedido como “atendido”, 
es decir, que ya fue procesado, entregado o cerrado.
"""
@app.patch("/orders/{order_id}/attend", response_model=schemas.OrderInDB)
def mark_order_attended(order_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado.")
    order.attended = True
    db.commit()
    db.refresh(order)
    return order


# Crear pedido (opcional: llamar cuando el usuario confirma compra)
@app.post("/orders", response_model=schemas.OrderInDB)
def create_order(user_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_active_user)):
    # Crear pedido
    new_order = models.Order(user_id=user_id)
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    # Obtener ítems del carrito para ese usuario
    cart_items = db.query(models.CartItem).filter(models.CartItem.user_id == user_id).all()

    if not cart_items:
        raise HTTPException(status_code=400, detail="El carrito está vacío.")

    # Copiar ítems del carrito al pedido
    for c_item in cart_items:
        order_item = models.OrderItem(
            order_id=new_order.id,
            paleta_id=c_item.paleta_id,
            quantity=c_item.quantity,
            nombre=c_item.nombre,
            descripcion=c_item.descripcion,
            ingredientes=c_item.ingredientes,
            precio=c_item.precio,
            imagen_url=c_item.imagen_url
        )
        db.add(order_item)

    # Limpiar carrito
    for c_item in cart_items:
        db.delete(c_item)

    db.commit()
    db.refresh(new_order)

    return new_order

