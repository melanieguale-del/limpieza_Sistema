"""Punto de entrada para el servidor de producción (Gunicorn en Azure).

Azure App Service ejecuta: gunicorn --bind=0.0.0.0 wsgi:app
"""
from app import create_app, db

app = create_app()


@app.cli.command("init-db")
def init_db():
    """Crea las tablas. Útil la primera vez: flask init-db"""
    with app.app_context():
        db.create_all()
    print("Base de datos inicializada.")


if __name__ == "__main__":
    app.run(debug=True)
