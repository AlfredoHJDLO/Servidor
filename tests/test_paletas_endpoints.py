# tests/test_paletas_endpoints.py
from fastapi import status
from app import schemas #

def test_create_paleta(client):
    response = client.post(
        "/paletas/",
        json={
            "nombre": "Paleta de Mango Test",
            "descripcion": "Deliciosa paleta de mango.",
            "ingredientes": "Mango, agua, azúcar",
            "precio": 20.0,
            "imagen_url": "/static/images/mango.png",
            "tiene_oferta": False
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["nombre"] == "Paleta de Mango Test"
    assert data["precio"] == 20.0
    assert "id" in data

def test_create_paleta_nombre_duplicado(client, create_paleta_fixture):
    create_paleta_fixture(nombre="Paleta Existente", precio=15.0)
    response = client.post(
        "/paletas/",
        json={
            "nombre": "Paleta Existente", # Nombre duplicado
            "descripcion": "Otra paleta.",
            "ingredientes": "Varios",
            "precio": 22.0,
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Ya existe una paleta con este nombre."

def test_read_paletas_vacio(client):
    response = client.get("/paletas/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []

def test_read_paletas_con_datos(client, create_paleta_fixture):
    paleta1 = create_paleta_fixture(nombre="Paleta Fresa", precio=18.0)
    paleta2 = create_paleta_fixture(nombre="Paleta Chocolate", precio=22.0)

    response = client.get("/paletas/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    assert data[0]["nombre"] == paleta1.nombre
    assert data[1]["nombre"] == paleta2.nombre

def test_read_paleta_existente(client, create_paleta_fixture):
    paleta = create_paleta_fixture(nombre="Paleta Limón", precio=17.0)
    response = client.get(f"/paletas/{paleta.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["nombre"] == "Paleta Limón"
    assert data["id"] == paleta.id

def test_read_paleta_no_existente(client):
    response = client.get("/paletas/9999") # ID que no existe
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Paleta no encontrada"

# Prueba para validar schema de entrada (ejemplo precio negativo)
def test_create_paleta_precio_invalido(client):
    response = client.post(
        "/paletas/",
        json={
            "nombre": "Paleta Precio Malo",
            "precio": -5.0, # Precio inválido según schema (gt=0)
            "descripcion": "Test",
            "ingredientes": "Test"
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY9