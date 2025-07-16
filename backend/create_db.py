from werkzeug.security import generate_password_hash
from app import create_app
from models import db, Admin
from config import Config

app = create_app()
with app.app_context():
    db.create_all()
    # Seed default admin if none exists
    if not Admin.query.first():
        username = Config.ADMIN_USERNAME
        password = Config.ADMIN_PASSWORD
        admin = Admin(username=username,
                      password_hash=generate_password_hash(password))
        db.session.add(admin)
        db.session.commit()
        print(f"Created admin user: '{username}' with default password.")
    else:
        print("Admin user already exists.")
