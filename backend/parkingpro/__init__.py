from __future__ import annotations

import json
import logging
import time
import uuid
from datetime import UTC, datetime
from typing import Any

import sentry_sdk
from flask import Flask, g, request
from sentry_sdk.integrations.flask import FlaskIntegration
from werkzeug.middleware.proxy_fix import ProxyFix

from parkingpro.api import register_blueprints
from parkingpro.config import CONFIG_BY_NAME, BaseConfig
from parkingpro.errors import register_error_handlers
from parkingpro.extensions import api, cors, db, jwt, limiter, migrate


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key in ("request_id", "method", "path", "status", "duration_ms"):
            if hasattr(record, key):
                payload[key] = getattr(record, key)
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str, separators=(",", ":"))


def create_app(config_name: str | None = None, overrides: dict[str, Any] | None = None) -> Flask:
    app = Flask(__name__)
    selected = config_name or BaseConfig.environment_name()
    if selected not in CONFIG_BY_NAME:
        raise RuntimeError(f"Unsupported APP_ENV: {selected}")
    app.config.from_object(CONFIG_BY_NAME[selected])
    if overrides:
        app.config.update(overrides)

    CONFIG_BY_NAME[selected].validate(app.config)
    _configure_logging(app)
    _configure_sentry(app)

    if app.config["BEHIND_PROXY"]:
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)  # type: ignore[method-assign]

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    api.init_app(app)
    limiter.init_app(app)
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}},
        allow_headers=["Authorization", "Content-Type", "Idempotency-Key", "X-CSRF-Token"],
        methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        supports_credentials=True,
    )

    register_blueprints(api)
    register_error_handlers(app)
    _register_request_hooks(app)
    _register_security_headers(app)
    _register_cli(app)
    return app


def _configure_logging(app: Flask) -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(logging.DEBUG if app.config["DEBUG"] else logging.INFO)


def _configure_sentry(app: Flask) -> None:
    if dsn := app.config.get("SENTRY_DSN"):
        sentry_sdk.init(
            dsn=dsn,
            environment=app.config["APP_ENV"],
            release=app.config.get("SENTRY_RELEASE") or None,
            integrations=[FlaskIntegration()],
            traces_sample_rate=0.0,
            send_default_pii=False,
        )


def _register_request_hooks(app: Flask) -> None:
    @app.before_request
    def attach_request_id() -> None:
        g.request_id = str(uuid.uuid4())
        g.request_started_at = time.perf_counter()

    @app.after_request
    def add_request_id(response):  # type: ignore[no-untyped-def]
        response.headers["X-Request-ID"] = g.get("request_id", "")
        app.logger.info(
            "request_completed",
            extra={
                "request_id": g.get("request_id", ""),
                "method": request.method,
                "path": request.path,
                "status": response.status_code,
                "duration_ms": round(
                    (time.perf_counter() - g.get("request_started_at", time.perf_counter())) * 1000,
                    2,
                ),
            },
        )
        return response


def _register_security_headers(app: Flask) -> None:
    @app.after_request
    def add_security_headers(response):  # type: ignore[no-untyped-def]
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault(
            "Permissions-Policy", "camera=(), microphone=(), geolocation=()"
        )
        response.headers.setdefault("Cache-Control", "no-store")
        return response


def _register_cli(app: Flask) -> None:
    from parkingpro.cli import create_operator, seed_demo

    app.cli.add_command(create_operator)
    app.cli.add_command(seed_demo)
