import uuid

from flask import request
from flask_jwt_extended import verify_jwt_in_request
from flask_smorest import Blueprint

from parkingpro.schemas import (
    MessageSchema,
    PaymentOrderSchema,
    PaymentVerifySchema,
    ReservationSchema,
)
from parkingpro.services.payments import create_order, process_webhook, verify_checkout
from parkingpro.services.reservations import require_idempotency_key, reservation_payload
from parkingpro.services.security import current_user

blueprint = Blueprint("payments", __name__, url_prefix="/api/v1", description="Test payments")


@blueprint.post("/payments/<uuid:reservation_id>/order")
@blueprint.response(200, PaymentOrderSchema)
def order(reservation_id: uuid.UUID):
    verify_jwt_in_request()
    return create_order(
        current_user(),
        reservation_id,
        request.headers.get("Idempotency-Key", ""),
    )


@blueprint.post("/payments/<uuid:reservation_id>/verify")
@blueprint.arguments(PaymentVerifySchema)
@blueprint.response(200, ReservationSchema)
def verify(data, reservation_id: uuid.UUID):  # type: ignore[no-untyped-def]
    verify_jwt_in_request()
    return reservation_payload(
        verify_checkout(
            current_user(),
            reservation_id,
            data,
            require_idempotency_key(request.headers.get("Idempotency-Key")),
        )
    )


@blueprint.post("/webhooks/razorpay")
@blueprint.response(200, MessageSchema)
def razorpay_webhook():
    processed = process_webhook(
        request.get_data(cache=True),
        request.headers.get("X-Razorpay-Signature"),
        request.headers.get("X-Razorpay-Event-Id"),
    )
    return {"message": "processed" if processed else "duplicate"}
