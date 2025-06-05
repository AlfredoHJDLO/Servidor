from fastapi import APIRouter, Depends, HTTPException
from .auth import get_current_active_user, get_password_hash
from .database import engine, get_db
from . import models, schemas
from sqlalchemy.orm import Session

#users = APIRouter(dependencies=[Depends(get_current_active_user)])
users = APIRouter()

@users.get("/", response_model=list[schemas.UserResponse])
def read_users(db: Session = Depends(get_db), current_user: schemas.UserResponse = Depends(get_current_active_user)):
    """
    Endpoint para obtener la información de los usuarios.
    """
    users = db.query(models.User).all()
    if not users:
        return []
    return users

@users.get("/{user_id}", response_model=schemas.UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db), current_user: schemas.UserResponse = Depends(get_current_active_user)):
    """
    Endpoint para obtener la información de un usuario específico por ID.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

@users.post("/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Endpoint para crear un nuevo usuario.
    """
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    
    new_user = models.User(
        email=user.email,
        password= get_password_hash(user.password),  # Asegúrate de hashear la contraseña antes de guardarla
        is_admin=user.is_admin,
        username=user.username
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@users.put("/{user_id}", response_model=schemas.UserResponse)
def update_user(user_id: int, user_update: schemas.UserCreate, db: Session = Depends(get_db), current_user: schemas.UserResponse = Depends(get_current_active_user)):
    """
    Endpoint para actualizar la información de un usuario específico por ID.
    """
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Actualizar los campos del usuario
    db_user.username = user_update.username
    db_user.email = user_update.email
    if user_update.password:
        db_user.password = get_password_hash(user_update.password)  # Actualizar la contraseña
    db.commit()
    db.refresh(db_user)
    
    return db_user

@users.delete("/{user_id}", response_model=schemas.UserResponse)
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: schemas.UserResponse = Depends(get_current_active_user)):
    """
    Endpoint para eliminar un usuario específico por ID.
    """
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    db.delete(db_user)
    db.commit()
    
    return db_user