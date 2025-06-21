# tests/conftest.py
import os
os.environ["TESTING_ENV"] = "True"

# Intento de limpieza explícita de MetaData (mantener por ahora)
try:
    from app.database import Base as AppBaseForClearing
    AppBaseForClearing.metadata.clear()
    print("DEBUG (conftest.py pre-import): app.database.Base.metadata cleared.")
except Exception as e:
    print(f"DEBUG (conftest.py pre-import): Could not clear metadata: {e}")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect # <--- AÑADE 'inspect'
from sqlalchemy.orm import sessionmaker, Session as SQLAlchemySession
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db

SQLALCHEMY_DATABASE_URL_TEST = "sqlite:///:memory:"

engine_test = create_engine(
    SQLALCHEMY_DATABASE_URL_TEST,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    print("\nDEBUG (setup_test_database): Starting session-scoped database setup.")
    print(f"DEBUG (setup_test_database): Using engine: {engine_test}")

    # Verifica si Base.metadata tiene tablas registradas ANTES de create_all
    # Esto es importante para saber si los modelos se cargaron en la metadata.
    if not Base.metadata.tables:
        print("CRITICAL ERROR (setup_test_database): Base.metadata.tables is EMPTY before create_all! Models are not registered.")
    else:
        print(f"DEBUG (setup_test_database): Tables in Base.metadata before create_all: {list(Base.metadata.tables.keys())}")

    try:
        print("DEBUG (setup_test_database): Attempting to drop_all tables...")
        Base.metadata.drop_all(bind=engine_test)
        print("DEBUG (setup_test_database): drop_all completed.")
        
        print("DEBUG (setup_test_database): Attempting to create_all tables...")
        Base.metadata.create_all(bind=engine_test)
        print("DEBUG (setup_test_database): create_all completed.")

        # Verifica DIRECTAMENTE en la BD si las tablas fueron creadas
        with engine_test.connect() as connection:
            inspector = inspect(connection)
            tables_in_db = inspector.get_table_names()
            print(f"DEBUG (setup_test_database): Tables found in DB via inspector AFTER create_all: {tables_in_db}")
            if not tables_in_db:
                print("CRITICAL ERROR (setup_test_database): No tables found in DB after create_all!")
            elif "paletas" not in tables_in_db:
                print("CRITICAL ERROR (setup_test_database): 'paletas' table specifically NOT FOUND in DB after create_all!")
            else:
                print("DEBUG (setup_test_database): 'paletas' table confirmed in DB by inspector.")

    except Exception as e:
        print(f"CRITICAL ERROR (setup_test_database): Exception during drop_all/create_all: {e}")
        raise # Vuelve a lanzar la excepción para que pytest la vea claramente

    # ----- Configuración de override de dependencia -----
    # (El código para override_get_db_test y app.dependency_overrides sigue igual)
    print(f"DEBUG (setup_test_database): Is get_db callable before override? {callable(get_db)}")
    
    def _override_get_db_for_test():
        try:
            db_test_session = TestingSessionLocal()
            yield db_test_session
        finally:
            db_test_session.close()

    original_dependency = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = _override_get_db_for_test
    print("DEBUG (setup_test_database): get_db dependency overridden for test session.")
    
    yield # Las pruebas de la sesión se ejecutan aquí
    
    print("DEBUG (setup_test_database): Test session finished. Restoring/clearing get_db override.")
    if original_dependency:
        app.dependency_overrides[get_db] = original_dependency
    else:
        if get_db in app.dependency_overrides and app.dependency_overrides[get_db] == _override_get_db_for_test:
            del app.dependency_overrides[get_db]
    print("DEBUG (setup_test_database): get_db dependency restored/cleared.")


# tests/conftest.py
# ... (todas las importaciones y configuraciones previas, incluyendo engine_test, TestingSessionLocal, etc.) ...

# La fixture setup_test_database debería estar como en la respuesta anterior, 
# asegurando que create_all se ejecute correctamente.

@pytest.fixture(scope="function")
def db_session(setup_test_database) -> SQLAlchemySession: # Sigue dependiendo de setup_test_database
    # print("DEBUG (db_session): Creating new DB session for a test function.") # Descomenta para depurar si es necesario
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        # print("DEBUG (db_session): Cleaning data from tables after test function.") # Descomenta para depurar
        # La comprobación 'table.exists()' era incorrecta y causaba un AttributeError.
        # Simplemente intentaremos borrar de todas las tablas conocidas por Base.metadata.
        # Si create_all funcionó, las tablas existirán.
        # Si una tabla específica no tuviera filas, el DELETE no hace nada.
        for table_obj in reversed(Base.metadata.sorted_tables): # table_obj es un objeto sqlalchemy.Table
            db.execute(table_obj.delete()) # Genera "DELETE FROM <nombre_tabla>"
        db.commit()
        db.close()
        # print("DEBUG (db_session): DB session closed for a test function.")    # print("DEBUG (db_session): DB session closed for a test function.")

@pytest.fixture(scope="function")
def client(db_session) -> TestClient:
    return TestClient(app)

@pytest.fixture(scope="function")
def create_paleta_fixture(db_session):
    from app import models
    def _create_paleta(nombre="Paleta Test", precio=10.0, descripcion="Test Desc", ingredientes="Test Ing", imagen_url="test.jpg", tiene_oferta=False, texto_oferta=None):
        paleta = models.Paleta(
            nombre=nombre,
            descripcion=descripcion,
            ingredientes=ingredientes,
            precio=precio,
            imagen_url=imagen_url,
            tiene_oferta=tiene_oferta,
            texto_oferta=texto_oferta
        )
        db_session.add(paleta)
        db_session.commit()
        db_session.refresh(paleta)
        return paleta
    return _create_paleta