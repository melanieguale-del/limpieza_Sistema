"""Rutas principales: inicio, panel (dashboard), inventario de productos,
exportación a CSV y perfil de usuario."""
import csv
import io

from flask import (
    Blueprint, render_template, redirect, url_for, flash, abort, request, Response
)
from flask_login import login_required, current_user

from app import db
from app.models import Producto, Venta
from app.forms import ProductoForm, ChangePasswordForm, VentaForm, CATEGORIAS

main_bp = Blueprint("main", __name__)

ORDENES = {
    "nombre": Producto.nombre.asc(),
    "precio_asc": Producto.precio.asc(),
    "precio_desc": Producto.precio.desc(),
    "stock_asc": Producto.stock.asc(),
    "stock_desc": Producto.stock.desc(),
}
POR_PAGINA = 8


@main_bp.route("/")
def index():
    return render_template("index.html")


@main_bp.route("/dashboard")
@login_required
def dashboard():
    """Inventario del usuario. Permite buscar, filtrar por categoría,
    ordenar por columna y navega por páginas."""
    q = request.args.get("q", "").strip()
    categoria = request.args.get("categoria", "").strip()
    orden = request.args.get("orden", "nombre")
    page = request.args.get("page", 1, type=int)

    base = Producto.query.filter_by(user_id=current_user.id)

    consulta = base
    if q:
        like = f"%{q}%"
        consulta = consulta.filter(
            db.or_(Producto.nombre.ilike(like), Producto.categoria.ilike(like))
        )
    if categoria:
        consulta = consulta.filter(Producto.categoria == categoria)

    consulta = consulta.order_by(ORDENES.get(orden, Producto.nombre.asc()))

    paginacion = consulta.paginate(page=page, per_page=POR_PAGINA, error_out=False)
    productos = paginacion.items

    todos = base.all()
    total_productos = len(todos)
    valor_total = sum(p.precio * p.stock for p in todos)
    stock_bajo_count = sum(1 for p in todos if p.stock_bajo)

    return render_template(
        "dashboard.html",
        productos=productos,
        paginacion=paginacion,
        q=q,
        categoria=categoria,
        orden=orden,
        categorias=CATEGORIAS,
        total_productos=total_productos,
        valor_total=valor_total,
        stock_bajo_count=stock_bajo_count,
        venta_form=VentaForm(),
    )


@main_bp.route("/productos/nuevo", methods=["GET", "POST"])
@login_required
def producto_nuevo():
    form = ProductoForm()
    if form.validate_on_submit():
        producto = Producto(
            nombre=form.nombre.data,
            marca=form.marca.data,
            categoria=form.categoria.data,
            precio=form.precio.data,
            stock=form.stock.data,
            imagen_url=form.imagen_url.data or None,
            descripcion=form.descripcion.data,
            user_id=current_user.id,
        )
        db.session.add(producto)
        db.session.commit()
        flash("Producto agregado al inventario.", "success")
        return redirect(url_for("main.dashboard"))
    return render_template("producto_form.html", form=form, titulo="Nuevo producto")


@main_bp.route("/productos/<int:producto_id>/editar", methods=["GET", "POST"])
@login_required
def producto_editar(producto_id):
    producto = db.session.get(Producto, producto_id)
    if producto is None or producto.user_id != current_user.id:
        abort(404)
    form = ProductoForm(obj=producto)
    if form.validate_on_submit():
        producto.nombre = form.nombre.data
        producto.marca = form.marca.data
        producto.categoria = form.categoria.data
        producto.precio = form.precio.data
        producto.stock = form.stock.data
        producto.imagen_url = form.imagen_url.data or None
        producto.descripcion = form.descripcion.data
        db.session.commit()
        flash("Producto actualizado.", "success")
        return redirect(url_for("main.dashboard"))
    return render_template("producto_form.html", form=form, titulo="Editar producto")


@main_bp.route("/productos/<int:producto_id>/eliminar", methods=["POST"])
@login_required
def producto_eliminar(producto_id):
    producto = db.session.get(Producto, producto_id)
    if producto is None or producto.user_id != current_user.id:
        abort(404)
    db.session.delete(producto)
    db.session.commit()
    flash("Producto eliminado del inventario.", "success")
    return redirect(url_for("main.dashboard"))


@main_bp.route("/productos/<int:producto_id>/vender", methods=["POST"])
@login_required
def producto_vender(producto_id):
    producto = db.session.get(Producto, producto_id)
    if producto is None or producto.user_id != current_user.id:
        abort(404)

    form = VentaForm()
    if form.validate_on_submit():
        cantidad = form.cantidad.data
        if cantidad > producto.stock:
            flash(f"No hay suficiente stock. Solo quedan {producto.stock} unidades de {producto.nombre}.", "error")
        else:
            venta = Venta(
                cantidad=cantidad,
                precio_unitario=producto.precio,
                producto_id=producto.id,
                user_id=current_user.id,
            )
            producto.stock -= cantidad
            db.session.add(venta)
            db.session.commit()
            flash(f"Venta registrada: {cantidad} x {producto.nombre} (${venta.total:.2f}).", "success")
    else:
        flash("Ingresa una cantidad válida para registrar la venta.", "error")
    return redirect(url_for("main.dashboard"))


@main_bp.route("/ventas")
@login_required
def historial_ventas():
    """Historial de ventas del usuario, más recientes primero."""
    page = request.args.get("page", 1, type=int)
    consulta = Venta.query.filter_by(user_id=current_user.id).order_by(Venta.fecha.desc())
    paginacion = consulta.paginate(page=page, per_page=POR_PAGINA, error_out=False)
    ventas = paginacion.items

    todas = Venta.query.filter_by(user_id=current_user.id).all()
    total_vendido = sum(v.total for v in todas)
    unidades_vendidas = sum(v.cantidad for v in todas)

    return render_template(
        "historial_ventas.html",
        ventas=ventas,
        paginacion=paginacion,
        total_vendido=total_vendido,
        unidades_vendidas=unidades_vendidas,
    )


@main_bp.route("/inventario/exportar")
@login_required
def exportar_csv():
    """Genera un CSV descargable con todo el inventario del usuario."""
    productos = Producto.query.filter_by(user_id=current_user.id).order_by(Producto.nombre.asc()).all()

    salida = io.StringIO()
    writer = csv.writer(salida)
    writer.writerow(["Nombre", "Marca", "Categoría", "Precio", "Stock", "Descripción"])
    for p in productos:
        writer.writerow([p.nombre, p.marca or "", p.categoria, f"{p.precio:.2f}", p.stock, p.descripcion or ""])

    return Response(
        salida.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=inventario_limpiastock.csv"},
    )


@main_bp.route("/perfil", methods=["GET", "POST"])
@login_required
def perfil():
    """Permite al usuario cambiar su contraseña."""
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash("La contraseña actual no es correcta.", "error")
        else:
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash("Contraseña actualizada correctamente.", "success")
            return redirect(url_for("main.perfil"))
    return render_template("perfil.html", form=form)
