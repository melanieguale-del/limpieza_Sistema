"""Fábrica de la aplicación (application factory).

Este patrón permite crear la app con distintas configuraciones (desarrollo,
test, producción) sin duplicar código. Es el punto de entrada del proyecto.
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

# Extensiones. Se crean aquí y se inicializan dentro de create_app().
db = SQLAlchemy()          # ORM (SQLAlchemy) para hablar con la base de datos
migrate = Migrate()        # Migraciones (Alembic) para versionar el esquema
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Por favor inicia sesión para continuar."


def create_app(config_object="app.config.Config"):
    app = Flask(__name__)
    app.config.from_object(config_object)

    # Conectar las extensiones a la app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Registrar los blueprints (grupos de rutas)
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    # Cargador de usuario para Flask-Login
    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    return app
