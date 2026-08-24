"""Local-only entrypoint for the preserved ParkingPrro Vue showcase.

This intentionally keeps the v1 routes and SQLite behavior available for visual
history. It is excluded from the v2 Docker image and must never be deployed.
"""

from flask import Flask
from flask_jwt_extended import JWTManager

from config import Config
from models import db


def create_legacy_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    JWTManager(app)

    from routes.admin import admin_bp
    from routes.auth import auth_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    return app


if __name__ == "__main__":
    create_legacy_app().run(debug=True)
