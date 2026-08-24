from __future__ import annotations

import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from typing import cast

from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash, generate_password_hash

from parkingpro.errors import ApiProblem
from parkingpro.extensions import db
from parkingpro.models import AccountState, RefreshSession, Role, User


def normalize_email(value: str) -> str:
    return value.strip().lower()


def _hash_token(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def public_user(user: User) -> dict[str, object]:
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "phone": user.phone,
        "role": user.role.value,
    }


def register_driver(data: dict[str, object]) -> User:
    email = normalize_email(str(data["email"]))
    if db.session.scalar(db.select(User).where(User.email == email)):
        raise ApiProblem("EMAIL_IN_USE", "An account already exists for this email.", 409)
    user = User(
        email=email,
        password_hash=generate_password_hash(str(data["password"])),
        full_name=str(data["full_name"]).strip(),
        phone=str(data["phone"]).strip() if data.get("phone") else None,
        role=Role.DRIVER,
    )
    db.session.add(user)
    db.session.commit()
    return user


def authenticate(email: str, password: str) -> User:
    user = db.session.scalar(db.select(User).where(User.email == normalize_email(email)))
    if not user or not check_password_hash(user.password_hash, password):
        raise ApiProblem("INVALID_CREDENTIALS", "Email or password is incorrect.", 401)
    if user.state is not AccountState.ACTIVE:
        raise ApiProblem("ACCOUNT_DISABLED", "This account is disabled.", 403)
    return cast(User, user)


def issue_session(
    user: User, client_type: str, device_name: str
) -> tuple[dict[str, object], str | None]:
    raw_refresh = secrets.token_urlsafe(48)
    raw_csrf = secrets.token_urlsafe(32) if client_type == "web" else None
    session = RefreshSession(
        user_id=user.id,
        token_hash=_hash_token(raw_refresh),
        csrf_hash=_hash_token(raw_csrf) if raw_csrf else None,
        device_name=device_name,
        expires_at=datetime.now(UTC) + timedelta(days=30),
    )
    db.session.add(session)
    db.session.commit()
    access = create_access_token(identity=str(user.id), additional_claims={"role": user.role.value})
    payload: dict[str, object] = {
        "access_token": access,
        "refresh_token": raw_refresh if client_type == "mobile" else None,
        "csrf_token": raw_csrf,
        "expires_in": 900,
        "user": public_user(user),
    }
    return payload, raw_refresh if client_type == "web" else None


def rotate_session(
    raw_refresh: str, csrf_token: str | None, client_type: str
) -> tuple[dict[str, object], str | None]:
    session = db.session.scalar(
        db.select(RefreshSession).where(RefreshSession.token_hash == _hash_token(raw_refresh))
    )
    now = datetime.now(UTC)
    if not session or session.revoked_at or session.expires_at <= now:
        raise ApiProblem("INVALID_REFRESH_TOKEN", "The session has expired.", 401)
    if client_type == "web" and (not csrf_token or session.csrf_hash != _hash_token(csrf_token)):
        raise ApiProblem("INVALID_CSRF_TOKEN", "The session could not be refreshed.", 403)
    session.revoked_at = now
    db.session.flush()
    return issue_session(session.user, client_type, session.device_name)


def revoke_session(raw_refresh: str | None) -> None:
    if not raw_refresh:
        return
    session = db.session.scalar(
        db.select(RefreshSession).where(RefreshSession.token_hash == _hash_token(raw_refresh))
    )
    if session and not session.revoked_at:
        session.revoked_at = datetime.now(UTC)
        db.session.commit()
