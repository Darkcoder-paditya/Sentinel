from flask import Flask
from .health import health_bp
from .auth import auth_bp
from .mail import mail_bp
from .vault import vault_bp


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(mail_bp, url_prefix="/api")
    app.register_blueprint(vault_bp, url_prefix="/api")
