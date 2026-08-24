from __future__ import annotations

import uuid
from collections.abc import Callable
from functools import wraps
from typing import Any, ParamSpec, TypeVar

from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from parkingpro.errors import ApiProblem
from parkingpro.extensions import db
from parkingpro.models import AccountState, Role, User

P = ParamSpec("P")
R = TypeVar("R")


def current_user() -> User:
    identity = get_jwt_identity()
    try:
        user_id = uuid.UUID(identity)
    except (TypeError, ValueError) as exc:
        raise ApiProblem(
            "AUTHENTICATION_REQUIRED", "A valid access token is required.", 401
        ) from exc
    user = db.session.get(User, user_id)
    if not user or user.state is not AccountState.ACTIVE:
        raise ApiProblem("AUTHENTICATION_REQUIRED", "The account is unavailable.", 401)
    return user


def roles_required(*roles: Role) -> Callable[[Callable[P, R]], Callable[P, R]]:
    allowed = set(roles)

    def decorator(function: Callable[P, R]) -> Callable[P, R]:
        @wraps(function)
        def wrapped(*args: P.args, **kwargs: P.kwargs) -> R:
            verify_jwt_in_request()
            if current_user().role not in allowed:
                raise ApiProblem("FORBIDDEN", "You do not have access to this operation.", 403)
            return function(*args, **kwargs)

        return wrapped

    return decorator


def owned_or_404(
    model: type[Any], resource_id: uuid.UUID, owner_column: Any, owner_id: uuid.UUID
) -> Any:
    resource = db.session.scalar(
        db.select(model).where(model.id == resource_id, owner_column == owner_id)
    )
    if not resource:
        raise ApiProblem("RESOURCE_NOT_FOUND", "The requested resource was not found.", 404)
    return resource
