"""Modelos de datos (ORM SQLAlchemy).

Cada clase representa una tabla en la base de datos. SQLAlchemy traduce
estas clases a SQL automáticamente, así no escribimos SQL a mano.
"""
from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db


class User(UserMixin, db.Model):
    """Usuario del sistema. La contraseña NUNCA se guarda en texto plano:
    se almacena un hash seguro (Werkzeug / PBKDF2)."""
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    productos = db.relationship(
        "Producto", backref="registrado_por", lazy=True, cascade="all, delete-orphan"
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


class Producto(db.Model):
    """Producto de limpieza en el inventario. Demuestra un CRUD completo."""
    __tablename__ = "productos"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    marca = db.Column(db.String(100), nullable=True)
    categoria = db.Column(db.String(60), nullable=False, default="Otros")
    precio = db.Column(db.Float, nullable=False, default=0.0)
    stock = db.Column(db.Integer, nullable=False, default=0)
    descripcion = db.Column(db.Text, nullable=True)
    imagen_url = db.Column(db.String(400), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)

    ventas = db.relationship(
        "Venta", backref="producto", lazy=True, cascade="all, delete-orphan"
    )

    @property
    def stock_bajo(self) -> bool:
        """True si quedan pocas unidades (para alertas en el panel)."""
        return self.stock <= 5

    def __repr__(self):
        return f"<Producto {self.nombre}>"


class Venta(db.Model):
    """Registro de una venta: descuenta stock y guarda historial.
    El precio_unitario se guarda como una 'foto' del precio al momento de
    vender, para que si luego cambias el precio del producto, el historial
    de ventas pasadas no se altere."""
    __tablename__ = "ventas"

    id = db.Column(db.Integer, primary_key=True)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    producto_id = db.Column(db.Integer, db.ForeignKey("productos.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)

    @property
    def total(self) -> float:
        return self.cantidad * self.precio_unitario

    def __repr__(self):
        return f"<Venta {self.cantidad}x producto={self.producto_id}>"
