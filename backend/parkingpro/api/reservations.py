import uuid

from flask import request
from flask_jwt_extended import verify_jwt_in_request
from flask_smorest import Blueprint

from parkingpro.schemas import ReservationCreateSchema, ReservationSchema
from parkingpro.services.reservations import (
    cancel_reservation,
    create_hold,
    get_reservation,
    list_reservations,
    reservation_payload,
)
from parkingpro.services.security import current_user

blueprint = Blueprint(
    "reservations",
    __name__,
    url_prefix="/api/v1/reservations",
    description="Driver reservations",
)


@blueprint.post("")
@blueprint.arguments(ReservationCreateSchema)
@blueprint.response(201, ReservationSchema)
def reserve(data):  # type: ignore[no-untyped-def]
    verify_jwt_in_request()
    payload, status = create_hold(
        current_user(),
        data,
        request.headers.get("Idempotency-Key", ""),
    )
    return payload, status


@blueprint.get("")
@blueprint.response(200, ReservationSchema(many=True))
def reservations():
    verify_jwt_in_request()
    return list_reservations(current_user())


@blueprint.get("/<uuid:reservation_id>")
@blueprint.response(200, ReservationSchema)
def reservation(reservation_id: uuid.UUID):
    verify_jwt_in_request()
    return reservation_payload(get_reservation(current_user(), reservation_id))


@blueprint.post("/<uuid:reservation_id>/cancel")
@blueprint.response(200, ReservationSchema)
def cancel(reservation_id: uuid.UUID):
    verify_jwt_in_request()
    return reservation_payload(
        cancel_reservation(
            current_user(),
            reservation_id,
            request.headers.get("Idempotency-Key", ""),
        )
    )
