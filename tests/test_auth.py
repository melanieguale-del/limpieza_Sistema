"""Tests de autenticación: registro, login y logout."""


def test_pagina_inicio_ok(client):
    resp = client.get("/")
    assert resp.status_code == 200


def test_login_muestra_formulario(client):
    """El formulario de login debe abrirse correctamente."""
    resp = client.get("/login")
    assert resp.status_code == 200
    assert "Iniciar sesión".encode() in resp.data


def test_registro_crea_usuario(client):
    resp = client.post(
        "/register",
        data={
            "username": "nuevo",
            "email": "nuevo@test.com",
            "password": "clave123",
            "confirm": "clave123",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    from app.models import User
    assert User.query.filter_by(username="nuevo").first() is not None


def test_login_correcto(client, usuario):
    resp = client.post(
        "/login",
        data={"username": "salome", "password": "clave123"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert "Inventario de productos".encode() in resp.data


def test_login_incorrecto(client, usuario):
    resp = client.post(
        "/login",
        data={"username": "salome", "password": "malaclave"},
        follow_redirects=True,
    )
    assert "incorrectos".encode() in resp.data


def test_dashboard_requiere_login(client):
    """Sin sesión, /dashboard redirige al login."""
    resp = client.get("/dashboard")
    assert resp.status_code == 302
