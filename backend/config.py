import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # SQLite database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'parking.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Redis (caching & Celery broker)
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

    # JWT configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'change-me-in-prod')

    # Default admin credentials
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'password')
