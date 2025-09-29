import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Global extensions
jwt = JWTManager()
db = SQLAlchemy()


def create_app() -> Flask:
    load_dotenv()

    app = Flask(__name__)

    # Configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///intra_mail.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")

    # Extensions
    db.init_app(app)
    jwt.init_app(app)

    # CORS
    allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
    CORS(app, resources={r"/api/*": {"origins": allowed_origins}}, supports_credentials=True)

    # Register blueprints
    from .routes import register_blueprints
    register_blueprints(app)

    with app.app_context():
        from .models.user import User
        from .models.mail import Mail
        from .models.vault import VaultItem
        db.create_all()
        _ensure_admin_user()

    return app


def _ensure_admin_user() -> None:
    from .models.user import User
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    if not admin_email or not admin_password:
        return

    existing = User.query.filter_by(email=admin_email).first()
    if existing is None:
        User.create_admin(email=admin_email, password=admin_password)
