from __future__ import annotations

import hmac

from flask import current_app, request
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint

from parkingpro.errors import ApiProblem
from parkingpro.extensions import limiter
from parkingpro.schemas import (
    AuthResponseSchema,
    LoginSchema,
    MessageSchema,
    PublicRegisterSchema,
    PushTokenSchema,
    RefreshSchema,
    UserSchema,
)
from parkingpro.services.auth import (
    authenticate,
    issue_session,
    public_user,
    register_driver,
    revoke_session,
    rotate_session,
)
from parkingpro.services.notifications import deactivate_push_token, register_push_token
from parkingpro.services.security import current_user

blueprint = Blueprint("auth", __name__, url_prefix="/api/v1/auth", description="Authentication")


def _set_web_session_cookies(response, refresh_token: str, csrf_token: str):  # type: ignore[no-untyped-def]
    cookie_options = {
        "max_age": 30 * 24 * 60 * 60,
        "secure": current_app.config["SESSION_COOKIE_SECURE"],
        "samesite": "Lax",
        "path": "/api/v1/auth",
    }
    response.set_cookie("parkingpro_refresh", refresh_token, httponly=True, **cookie_options)
    response.set_cookie("parkingpro_csrf", csrf_token, httponly=False, **cookie_options)
    return response


def _require_cookie_csrf() -> str:
    header = request.headers.get("X-CSRF-Token", "")
    cookie = request.cookies.get("parkingpro_csrf", "")
    if not header or not cookie or not hmac.compare_digest(header, cookie):
        raise ApiProblem("INVALID_CSRF_TOKEN", "The session could not be changed.", 403)
    return header


@blueprint.post("/register")
@blueprint.arguments(PublicRegisterSchema)
@blueprint.response(201, UserSchema)
@limiter.limit("5 per minute")
def register(data):  # type: ignore[no-untyped-def]
    return public_user(register_driver(data))


@blueprint.post("/login")
@blueprint.arguments(LoginSchema)
@blueprint.response(200, AuthResponseSchema)
@limiter.limit("10 per minute")
def login(data):  # type: ignore[no-untyped-def]
    user = authenticate(data["email"], data["password"])
    payload, web_refresh = issue_session(user, data["client_type"], data["device_name"])
    if not web_refresh:
        return payload
    response = current_app.make_response(payload)
    return _set_web_session_cookies(response, web_refresh, str(payload["csrf_token"]))


@blueprint.post("/refresh")
@blueprint.arguments(RefreshSchema)
@blueprint.response(200, AuthResponseSchema)
@limiter.limit("20 per minute")
def refresh(data):  # type: ignore[no-untyped-def]
    client_type = data["client_type"]
    raw_refresh = (
        data.get("refresh_token")
        if client_type == "mobile"
        else request.cookies.get("parkingpro_refresh")
    )
    if not raw_refresh:
        raise ApiProblem("INVALID_REFRESH_TOKEN", "The session has expired.", 401)
    csrf_token = _require_cookie_csrf() if client_type == "web" else None
    payload, web_refresh = rotate_session(raw_refresh, csrf_token, client_type)
    if not web_refresh:
        return payload
    response = current_app.make_response(payload)
    return _set_web_session_cookies(response, web_refresh, str(payload["csrf_token"]))


@blueprint.post("/logout")
@blueprint.arguments(RefreshSchema)
@blueprint.response(200, MessageSchema)
def logout(data):  # type: ignore[no-untyped-def]
    if data["client_type"] == "web":
        _require_cookie_csrf()
    raw_refresh = (
        data.get("refresh_token")
        if data["client_type"] == "mobile"
        else request.cookies.get("parkingpro_refresh")
    )
    revoke_session(raw_refresh)
    response = current_app.make_response({"message": "Signed out."})
    response.delete_cookie("parkingpro_refresh", path="/api/v1/auth")
    response.delete_cookie("parkingpro_csrf", path="/api/v1/auth")
    return response


@blueprint.get("/me")
@blueprint.response(200, UserSchema)
@jwt_required()
def me():
    return public_user(current_user())


@blueprint.post("/push-token")
@blueprint.arguments(PushTokenSchema)
@blueprint.response(200, MessageSchema)
@jwt_required()
@limiter.limit("10 per minute")
def push_token(data):  # type: ignore[no-untyped-def]
    register_push_token(current_user(), data["token"], data["platform"])
    return {"message": "Push token registered."}


@blueprint.delete("/push-token")
@blueprint.arguments(PushTokenSchema)
@blueprint.response(200, MessageSchema)
@jwt_required()
def remove_push_token(data):  # type: ignore[no-untyped-def]
    deactivate_push_token(current_user(), data["token"])
    return {"message": "Push token removed."}
