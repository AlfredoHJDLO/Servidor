# app/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv() # Cargar variables de entorno desde .env

# URL de conexión a tu base de datos MySQL (cargada desde .env)
# Ejemplo: mysql+mysqlclient://user:password@host/dbname
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

if SQLALCHEMY_DATABASE_URL is None:
    raise ValueError("DATABASE_URL environment variable not set. Please create a .env file or set the variable.")

# Crea el motor de la base de datos
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Crea una clase SessionLocal para cada solicitud de base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos declarativos de SQLAlchemy
Base = declarative_base()

# Dependencia para obtener una sesión de base de datos por solicitud
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()