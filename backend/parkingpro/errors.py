from __future__ import annotations

from dataclasses import dataclass, field
from http import HTTPStatus

from flask import Flask, Response, g, jsonify
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import HTTPException


@dataclass
class ApiProblem(Exception):
    code: str
    message: str
    status: int = HTTPStatus.BAD_REQUEST
    fields: dict[str, list[str]] = field(default_factory=dict)


def problem_response(problem: ApiProblem) -> tuple[Response, int]:
    return (
        jsonify(
            error={
                "code": problem.code,
                "message": problem.message,
                "request_id": g.get("request_id", ""),
                "fields": problem.fields,
            }
        ),
        problem.status,
    )


def _normalize_fields(messages: object) -> dict[str, list[str]]:
    if isinstance(messages, dict):
        normalized: dict[str, list[str]] = {}
        for key, value in messages.items():
            if isinstance(value, dict):
                for nested_key, nested_value in value.items():
                    values = nested_value if isinstance(nested_value, list) else [nested_value]
                    normalized[f"{key}.{nested_key}"] = [str(item) for item in values]
            else:
                values = value if isinstance(value, list) else [value]
                normalized[str(key)] = [str(item) for item in values]
        return normalized
    values = messages if isinstance(messages, list) else [messages]
    return {"_schema": [str(item) for item in values]}


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(ApiProblem)
    def handle_problem(error: ApiProblem):  # type: ignore[no-untyped-def]
        return problem_response(error)

    @app.errorhandler(ValidationError)
    def handle_validation(error: ValidationError):  # type: ignore[no-untyped-def]
        fields = _normalize_fields(error.messages)
        return problem_response(
            ApiProblem("VALIDATION_ERROR", "Request validation failed.", 422, fields)
        )

    @app.errorhandler(IntegrityError)
    def handle_integrity(_error: IntegrityError):  # type: ignore[no-untyped-def]
        return problem_response(
            ApiProblem(
                "RESOURCE_CONFLICT", "The requested change conflicts with existing data.", 409
            )
        )

    @app.errorhandler(HTTPException)
    def handle_http(error: HTTPException):  # type: ignore[no-untyped-def]
        data = getattr(error, "data", {})
        messages = data.get("messages", {}) if isinstance(data, dict) else {}
        if error.code == 422:
            return problem_response(
                ApiProblem(
                    "VALIDATION_ERROR",
                    "Request validation failed.",
                    422,
                    _normalize_fields(messages),
                )
            )
        code = "RESOURCE_NOT_FOUND" if error.code == 404 else "HTTP_ERROR"
        return problem_response(
            ApiProblem(code, error.description or "Request failed.", error.code or 500)
        )

    @app.errorhandler(Exception)
    def handle_unexpected(error: Exception):  # type: ignore[no-untyped-def]
        app.logger.exception("Unhandled API error", exc_info=error)
        return problem_response(ApiProblem("INTERNAL_ERROR", "An unexpected error occurred.", 500))
