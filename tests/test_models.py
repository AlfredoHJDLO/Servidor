# tests/test_models.py
import pytest
from app import models #
from decimal import Decimal

def test_cart_item_subtotal(db_session): # Necesita db_session si crea Paleta
    # Crear una paleta mock o una paleta real en la BD de prueba
    paleta_test = models.Paleta(
        nombre="Paleta de Prueba Subtotal",
        precio=Decimal("25.50"),
        descripcion="Test",
        ingredientes="Test"
    )
    db_session.add(paleta_test)
    db_session.commit()
    db_session.refresh(paleta_test)

    cart_item = models.CartItem(
        user_id=1,
        paleta_id=paleta_test.id,
        quantity=3,
        paleta=paleta_test # Importante asignar el objeto paleta
    )
    db_session.add(cart_item)
    db_session.commit()
    db_session.refresh(cart_item)

    # El precio es Decimal("25.50"), quantity es 3
    # subtotal esperado es 25.50 * 3 = 76.50
    assert cart_item.subtotal == 76.50
    assert isinstance(cart_item.subtotal, float)

def test_paleta_representation(db_session, create_paleta_fixture):
    paleta = create_paleta_fixture(nombre="Fresa Deluxe", precio=Decimal("30.00"))
    assert repr(paleta) == f"<Paleta(id={paleta.id}, nombre='Fresa Deluxe', precio=30.00)>"

def test_cart_item_representation(db_session, create_paleta_fixture):
    paleta = create_paleta_fixture()
    cart_item = models.CartItem(user_id=10, paleta_id=paleta.id, quantity=5, paleta=paleta)
    db_session.add(cart_item)
    db_session.commit()
    db_session.refresh(cart_item)
    assert repr(cart_item) == f"<CartItem(id={cart_item.id}, user_id=10, paleta_id={paleta.id}, quantity=5)>"