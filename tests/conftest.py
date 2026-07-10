"""Configuración compartida de los tests (fixtures de pytest)."""
import pytest

from app import create_app, db
from app.models import User


@pytest.fixture
def app():
    app = create_app("app.config.TestConfig")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def usuario(app):
    """Crea un usuario de prueba con contraseña conocida."""
    user = User(username="salome", email="salome@test.com")
    user.set_password("clave123")
    db.session.add(user)
    db.session.commit()
    return user
