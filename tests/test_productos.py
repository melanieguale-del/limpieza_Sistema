"""Tests del CRUD de productos de limpieza."""


def _login(client):
    client.post("/login", data={"username": "salome", "password": "clave123"})


def test_crear_producto(client, usuario):
    _login(client)
    resp = client.post(
        "/productos/nuevo",
        data={
            "nombre": "Cloro Clorox 1L",
            "marca": "Clorox",
            "categoria": "Desinfectantes",
            "precio": "2.50",
            "stock": "20",
            "descripcion": "Desinfectante multiusos",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert "Cloro Clorox 1L".encode() in resp.data


def test_editar_producto(client, usuario):
    from app import db
    from app.models import Producto
    _login(client)
    p = Producto(nombre="Detergente", categoria="Detergentes",
                 precio=3.0, stock=10, user_id=usuario.id)
    db.session.add(p)
    db.session.commit()

    resp = client.post(
        f"/productos/{p.id}/editar",
        data={"nombre": "Detergente Deja", "marca": "Deja",
              "categoria": "Detergentes", "precio": "3.75", "stock": "8",
              "descripcion": ""},
        follow_redirects=True,
    )
    assert "Detergente Deja".encode() in resp.data
    assert db.session.get(Producto, p.id).precio == 3.75


def test_eliminar_producto(client, usuario):
    from app import db
    from app.models import Producto
    _login(client)
    p = Producto(nombre="Jabón", categoria="Otros", precio=1.0,
                 stock=5, user_id=usuario.id)
    db.session.add(p)
    db.session.commit()
    pid = p.id

    client.post(f"/productos/{pid}/eliminar", follow_redirects=True)
    assert db.session.get(Producto, pid) is None


def test_alerta_stock_bajo(client, usuario):
    """Un producto con 5 o menos unidades debe marcarse como stock bajo."""
    from app.models import Producto
    p = Producto(nombre="Test", categoria="Otros", precio=1.0,
                 stock=3, user_id=usuario.id)
    assert p.stock_bajo is True
