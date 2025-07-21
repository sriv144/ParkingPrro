from flask import Flask
from config import Config
from models import db
from flask_jwt_extended import JWTManager

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    # Initialize JWT
    jwt = JWTManager(app)

    # Register blueprints
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    return app

if __name__ == '__main__':
    create_app().run(debug=True)
