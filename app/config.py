"""Configuración de la aplicación.

Lee valores desde variables de entorno para que funcione igual en local
(SQLite) y en producción en Azure (PostgreSQL). Nunca se ponen credenciales
en el código: se leen del entorno.
"""
import os

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


def _normalizar_url(url: str) -> str:
    """Azure y algunos proveedores entregan 'postgres://'.
    SQLAlchemy necesita 'postgresql://'. Aquí lo normalizamos.
    """
    if url and url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


class Config:
    """Configuración base (desarrollo)."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "clave-secreta-solo-para-desarrollo")

    # En Azure se define DATABASE_URL apuntando al PostgreSQL Flexible Server.
    # En local, si no existe, se usa un SQLite para poder probar sin nada extra.
    SQLALCHEMY_DATABASE_URI = _normalizar_url(
        os.environ.get("DATABASE_URL")
        or "sqlite:///" + os.path.join(BASE_DIR, "gestor.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestConfig(Config):
    """Configuración para los tests: base de datos en memoria, rápida y aislada."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
