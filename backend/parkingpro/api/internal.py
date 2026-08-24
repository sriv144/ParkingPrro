import json
import uuid

from flask import current_app, request
from flask_smorest import Blueprint
from qstash import Receiver

from parkingpro.errors import ApiProblem
from parkingpro.schemas import MessageSchema
from parkingpro.services.notifications import send_reservation_reminder
from parkingpro.services.reservations import expire_reservation

blueprint = Blueprint(
    "internal",
    __name__,
    url_prefix="/api/v1/internal/jobs",
    description="Signed background jobs",
)


def verify_qstash(raw_body: bytes) -> None:
    current_key = current_app.config.get("QSTASH_CURRENT_SIGNING_KEY", "")
    next_key = current_app.config.get("QSTASH_NEXT_SIGNING_KEY", "")
    signature = request.headers.get("Upstash-Signature", "")
    if not current_key or not next_key or not signature:
        raise ApiProblem("INVALID_JOB_SIGNATURE", "Job signature verification failed.", 401)
    try:
        Receiver(current_signing_key=current_key, next_signing_key=next_key).verify(
            body=raw_body.decode(),
            signature=signature,
            url=request.url,
        )
    except Exception as exc:
        raise ApiProblem(
            "INVALID_JOB_SIGNATURE", "Job signature verification failed.", 401
        ) from exc


@blueprint.post("/expire-reservation")
@blueprint.response(200, MessageSchema)
def expire_hold():
    raw_body = request.get_data(cache=True)
    verify_qstash(raw_body)
    try:
        reservation_id = uuid.UUID(json.loads(raw_body)["reservation_id"])
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        raise ApiProblem("INVALID_JOB_PAYLOAD", "Job payload is invalid.", 422) from exc
    changed = expire_reservation(reservation_id)
    return {"message": "expired" if changed else "no-op"}


@blueprint.post("/send-reminder")
@blueprint.response(200, MessageSchema)
def send_reminder():
    raw_body = request.get_data(cache=True)
    verify_qstash(raw_body)
    try:
        reservation_id = uuid.UUID(json.loads(raw_body)["reservation_id"])
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        raise ApiProblem("INVALID_JOB_PAYLOAD", "Job payload is invalid.", 422) from exc
    sent = send_reservation_reminder(reservation_id)
    return {"message": "sent" if sent else "no-op"}
