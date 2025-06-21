# tests/test_cart_endpoints.py
from fastapi import status
from app import models, schemas #

USER_ID_TEST = 1 # ID de usuario para las pruebas del carrito

def test_add_item_to_cart_nueva_paleta(client, create_paleta_fixture):
    paleta = create_paleta_fixture(nombre="Paleta Uva", precio=12.0)
    response = client.post(
        "/cart/add",
        json={"user_id": USER_ID_TEST, "paleta_id": paleta.id, "quantity": 2},
    )
    assert response.status_code == status.HTTP_200_OK # Endpoint POST /cart/add devuelve 200 OK
    data = response.json()
    assert data["user_id"] == USER_ID_TEST
    assert data["quantity"] == 2
    assert data["subtotal"] == 24.0 # 12.0 * 2

def test_add_item_to_cart_paleta_no_existente(client):
    response = client.post(
        "/cart/add",
        json={"user_id": USER_ID_TEST, "paleta_id": 999, "quantity": 1}, # paleta_id 999 no existe
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Paleta no encontrada."

def test_add_item_to_cart_actualizar_cantidad(client, db_session, create_paleta_fixture):
    paleta = create_paleta_fixture(nombre="Paleta Sandia", precio=15.0)

    # Añadir item inicialmente
    client.post("/cart/add", json={"user_id": USER_ID_TEST, "paleta_id": paleta.id, "quantity": 1})

    # Volver a añadir la misma paleta (debería incrementar cantidad)
    response = client.post(
        "/cart/add",
        json={"user_id": USER_ID_TEST, "paleta_id": paleta.id, "quantity": 3},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["quantity"] == 4 # 1 (inicial) + 3 (nuevo) = 4
    assert data["subtotal"] == 60.0 # 15.0 * 4

def test_get_user_cart_vacio(client):
    response = client.get(f"/cart/{USER_ID_TEST}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []

def test_get_user_cart_con_items(client, db_session, create_paleta_fixture):
    paleta1 = create_paleta_fixture(nombre="P1", precio=10.0)
    paleta2 = create_paleta_fixture(nombre="P2", precio=20.0)

    client.post("/cart/add", json={"user_id": USER_ID_TEST, "paleta_id": paleta1.id, "quantity": 2})
    client.post("/cart/add", json={"user_id": USER_ID_TEST, "paleta_id": paleta2.id, "quantity": 1})

    response = client.get(f"/cart/{USER_ID_TEST}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    # Puedes añadir más aserciones para verificar el contenido del carrito

def test_remove_from_cart_existente(client, db_session, create_paleta_fixture):
    paleta = create_paleta_fixture(nombre="Paleta a Eliminar", precio=5.0)
    add_response = client.post("/cart/add", json={"user_id": USER_ID_TEST, "paleta_id": paleta.id, "quantity": 1})
    cart_item_id = add_response.json()["id"]

    response = client.delete(f"/cart/remove/{cart_item_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT #

    # Verificar que el item ya no está en el carrito
    cart_response = client.get(f"/cart/{USER_ID_TEST}")
    assert cart_response.json() == []

def test_remove_from_cart_no_existente(client):
    response = client.delete("/cart/remove/999") # ID de cart_item que no existe
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Ítem del carrito no encontrado."

def test_decrease_from_cart_mayor_a_uno(client, db_session, create_paleta_fixture):
    paleta = create_paleta_fixture(precio=10.0)
    client.post("/cart/add", json={"user_id": USER_ID_TEST, "paleta_id": paleta.id, "quantity": 3})

    response = client.patch(f"/cart/decrease?user_id={USER_ID_TEST}&paleta_id={paleta.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["message"] == "Cantidad actualizada"
    assert data["item"]["quantity"] == 2

def test_decrease_from_cart_a_cero(client, db_session, create_paleta_fixture):
    paleta = create_paleta_fixture(precio=10.0)
    client.post("/cart/add", json={"user_id": USER_ID_TEST, "paleta_id": paleta.id, "quantity": 1})

    response = client.patch(f"/cart/decrease?user_id={USER_ID_TEST}&paleta_id={paleta.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["message"] == "Ítem eliminado porque la cantidad llegó a cero."

    # Verificar que el item ya no está en el carrito
    cart_response = client.get(f"/cart/{USER_ID_TEST}")
    assert cart_response.json() == []


def test_decrease_from_cart_item_no_existente(client, create_paleta_fixture):
    paleta_existente = create_paleta_fixture() # Para asegurar que la paleta existe
    paleta_no_en_carrito_id = paleta_existente.id + 100 # Un ID de paleta que no estará en el carrito

    response = client.patch(f"/cart/decrease?user_id={USER_ID_TEST}&paleta_id={paleta_no_en_carrito_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Ítem no encontrado en el carrito."