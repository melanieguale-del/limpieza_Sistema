"""Formularios (Flask-WTF).

Validan la entrada del usuario y generan tokens CSRF para proteger contra
ataques. El formulario de login vive en LoginForm.
"""
from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, TextAreaField, SelectField,
    FloatField, IntegerField, SubmitField,
)
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange, Optional, URL

# Categorías típicas de un negocio de productos de limpieza.
CATEGORIAS = [
    ("Desinfectantes", "Desinfectantes"),
    ("Detergentes", "Detergentes"),
    ("Limpiadores", "Limpiadores multiusos"),
    ("Papel e higiene", "Papel e higiene"),
    ("Accesorios", "Accesorios (escobas, trapeadores, etc.)"),
    ("Otros", "Otros"),
]


class RegisterForm(FlaskForm):
    username = StringField("Usuario", validators=[DataRequired(), Length(3, 80)])
    email = StringField("Correo", validators=[DataRequired(), Email()])
    password = PasswordField("Contraseña", validators=[DataRequired(), Length(min=6)])
    confirm = PasswordField(
        "Confirmar contraseña",
        validators=[DataRequired(), EqualTo("password", message="Las contraseñas no coinciden")],
    )
    submit = SubmitField("Registrarme")


class LoginForm(FlaskForm):
    username = StringField("Usuario", validators=[DataRequired()])
    password = PasswordField("Contraseña", validators=[DataRequired()])
    submit = SubmitField("Iniciar sesión")


class ProductoForm(FlaskForm):
    nombre = StringField("Nombre del producto", validators=[DataRequired(), Length(1, 150)])
    marca = StringField("Marca", validators=[Length(max=100)])
    categoria = SelectField("Categoría", choices=CATEGORIAS, validators=[DataRequired()])
    precio = FloatField("Precio (USD)", validators=[DataRequired(), NumberRange(min=0)])
    stock = IntegerField("Stock (unidades)", validators=[DataRequired(), NumberRange(min=0)])
    imagen_url = StringField(
        "URL de la imagen (opcional)",
        validators=[Optional(), URL(message="Debe ser un enlace válido (https://...)"), Length(max=400)],
    )
    descripcion = TextAreaField("Descripción")
    submit = SubmitField("Guardar")


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField("Contraseña actual", validators=[DataRequired()])
    new_password = PasswordField("Nueva contraseña", validators=[DataRequired(), Length(min=6)])
    confirm = PasswordField(
        "Confirmar nueva contraseña",
        validators=[DataRequired(), EqualTo("new_password", message="Las contraseñas no coinciden")],
    )
    submit = SubmitField("Actualizar contraseña")


class VentaForm(FlaskForm):
    cantidad = IntegerField("Cantidad vendida", validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField("Registrar venta")
