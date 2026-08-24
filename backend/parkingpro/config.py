from __future__ import annotations

import os
from datetime import timedelta
from typing import Any


def _csv(name: str, default: str = "") -> list[str]:
    return [value.strip() for value in os.getenv(name, default).split(",") if value.strip()]


class BaseConfig:
    APP_ENV = os.getenv("APP_ENV", "development").lower()
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "postgresql+psycopg://parkingpro:parkingpro@localhost:5432/parkingpro"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "pool_recycle": 300}
    SECRET_KEY = os.getenv("SECRET_KEY", "")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")
    QR_SIGNING_KEY = os.getenv("QR_SIGNING_KEY", "")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    RATELIMIT_STORAGE_URI = REDIS_URL
    RATELIMIT_HEADERS_ENABLED = True
    CORS_ORIGINS = _csv("CORS_ORIGINS", "http://localhost:5173")
    TRUSTED_HOSTS = _csv("TRUSTED_HOSTS", "localhost,127.0.0.1")
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024
    MAX_FORM_MEMORY_SIZE = 64 * 1024
    MAX_FORM_PARTS = 50
    BEHIND_PROXY = False
    API_TITLE = "ParkingPro API"
    API_VERSION = "2.0.0"
    OPENAPI_VERSION = "3.1.0"
    OPENAPI_URL_PREFIX = "/"
    OPENAPI_JSON_PATH = "openapi.json"
    OPENAPI_SWAGGER_UI_PATH = None
    RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "")
    RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "")
    RAZORPAY_WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET", "")
    QSTASH_TOKEN = os.getenv("QSTASH_TOKEN", "")
    QSTASH_CURRENT_SIGNING_KEY = os.getenv("QSTASH_CURRENT_SIGNING_KEY", "")
    QSTASH_NEXT_SIGNING_KEY = os.getenv("QSTASH_NEXT_SIGNING_KEY", "")
    SENTRY_DSN = os.getenv("SENTRY_DSN", "")
    SENTRY_RELEASE = os.getenv("SENTRY_RELEASE", os.getenv("RENDER_GIT_COMMIT", ""))
    PUBLIC_API_URL = os.getenv("PUBLIC_API_URL", "http://localhost:5000")

    @staticmethod
    def environment_name() -> str:
        return os.getenv("APP_ENV", "development").lower()

    @classmethod
    def validate(cls, config: dict[str, Any]) -> None:
        if config["APP_ENV"] != "production":
            return
        required = [
            "SECRET_KEY",
            "JWT_SECRET_KEY",
            "QR_SIGNING_KEY",
            "SQLALCHEMY_DATABASE_URI",
            "REDIS_URL",
            "RAZORPAY_KEY_ID",
            "RAZORPAY_KEY_SECRET",
            "RAZORPAY_WEBHOOK_SECRET",
            "QSTASH_TOKEN",
            "QSTASH_CURRENT_SIGNING_KEY",
            "QSTASH_NEXT_SIGNING_KEY",
            "PUBLIC_API_URL",
        ]
        missing = [name for name in required if not config.get(name)]
        if missing:
            raise RuntimeError(f"Missing required production configuration: {', '.join(missing)}")
        if any(origin == "*" for origin in config["CORS_ORIGINS"]):
            raise RuntimeError("Production CORS_ORIGINS must be an explicit allowlist")
        if not config["CORS_ORIGINS"] or not config["TRUSTED_HOSTS"]:
            raise RuntimeError("Production origins and trusted hosts must be explicit allowlists")
        if any(
            marker in str(config[name])
            for name in ("SQLALCHEMY_DATABASE_URI", "REDIS_URL", "PUBLIC_API_URL")
            for marker in ("localhost", "127.0.0.1")
        ):
            raise RuntimeError("Production service URLs cannot point to localhost")


class DevelopmentConfig(BaseConfig):
    APP_ENV = "development"
    DEBUG = True
    SECRET_KEY = os.getenv("SECRET_KEY", "parkingpro-development-session-only")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "parkingpro-development-jwt-only")
    QR_SIGNING_KEY = os.getenv("QR_SIGNING_KEY", "parkingpro-development-qr-only")


class TestConfig(BaseConfig):
    APP_ENV = "test"
    TESTING = True
    SECRET_KEY = "test-session-" * 3  # noqa: S105 - deterministic test-only value
    JWT_SECRET_KEY = "test-jwt-" * 4  # noqa: S105 - deterministic test-only value
    QR_SIGNING_KEY = "test-qr-" * 4  # noqa: S105 - deterministic test-only value
    RATELIMIT_ENABLED = False


class ProductionConfig(BaseConfig):
    APP_ENV = "production"
    SESSION_COOKIE_SECURE = True
    BEHIND_PROXY = True


CONFIG_BY_NAME = {
    "development": DevelopmentConfig,
    "test": TestConfig,
    "production": ProductionConfig,
}
