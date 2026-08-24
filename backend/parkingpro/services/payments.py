from __future__ import annotations

import hashlib
import hmac
import json
import uuid
from datetime import UTC, datetime
from typing import Any

import razorpay
from flask import current_app
from sqlalchemy import select

from parkingpro.errors import ApiProblem
from parkingpro.extensions import db
from parkingpro.models import (
    Payment,
    PaymentStatus,
    Reservation,
    ReservationStatus,
    User,
    WebhookEvent,
)
from parkingpro.services.notifications import schedule_reminder
from parkingpro.services.reservations import (
    finish_idempotent,
    get_reservation,
    replay_idempotent,
    require_idempotency_key,
)


def _credentials() -> tuple[str, str]:
    key_id = current_app.config.get("RAZORPAY_KEY_ID", "")
    key_secret = current_app.config.get("RAZORPAY_KEY_SECRET", "")
    if not key_id or not key_secret:
        raise ApiProblem("PAYMENTS_UNAVAILABLE", "Test payments are not configured.", 503)
    return key_id, key_secret


def _client() -> razorpay.Client:
    return razorpay.Client(auth=_credentials())


def create_order(
    user: User, reservation_id: uuid.UUID, idempotency_key: str
) -> tuple[dict[str, Any], int]:
    key = require_idempotency_key(idempotency_key)
    request_data = {"reservation_id": str(reservation_id)}
    replay, status, record = replay_idempotent(
        user, f"POST:/api/v1/payments/{reservation_id}/order", key, request_data
    )
    if replay is not None:
        return replay, status or 200
    reservation = get_reservation(user, reservation_id)
    if reservation.status is not ReservationStatus.HELD:
        raise ApiProblem("INVALID_RESERVATION_STATE", "Only an active hold can be paid.", 409)

    payment = db.session.scalar(select(Payment).where(Payment.reservation_id == reservation.id))
    key_id, _ = _credentials()
    if not payment:
        payment = Payment(
            reservation_id=reservation.id,
            amount_paise=reservation.quoted_amount_paise,
            status=PaymentStatus.CREATED,
        )
        db.session.add(payment)
        db.session.flush()
    if not payment.provider_order_id:
        order = _client().order.create(
            {
                "amount": payment.amount_paise,
                "currency": "INR",
                "receipt": f"reservation-{reservation.id}",
                "notes": {"reservation_id": str(reservation.id)},
            }
        )
        payment.provider_order_id = str(order["id"])
    payload = {
        "order_id": payment.provider_order_id,
        "key_id": key_id,
        "amount_paise": payment.amount_paise,
        "currency": "INR",
        "reservation_id": reservation.id,
    }
    if record is None:
        raise RuntimeError("Idempotency record was not created")
    finish_idempotent(record, payload, 200)
    db.session.commit()
    return payload, 200


def verify_checkout(
    user: User,
    reservation_id: uuid.UUID,
    data: dict[str, str],
    idempotency_key: str,
) -> Reservation:
    replay, _, record = replay_idempotent(
        user,
        f"POST:/api/v1/payments/{reservation_id}/verify",
        idempotency_key,
        data,
    )
    if replay is not None:
        return get_reservation(user, reservation_id)
    reservation = get_reservation(user, reservation_id)
    payment = db.session.scalar(select(Payment).where(Payment.reservation_id == reservation.id))
    if not payment or payment.provider_order_id != data["razorpay_order_id"]:
        raise ApiProblem("PAYMENT_NOT_FOUND", "The payment order was not found.", 404)
    try:
        _client().utility.verify_payment_signature(data)
    except razorpay.errors.SignatureVerificationError as exc:
        raise ApiProblem("INVALID_PAYMENT_SIGNATURE", "Payment verification failed.", 422) from exc
    payment.provider_payment_id = data["razorpay_payment_id"]
    payment.status = PaymentStatus.CAPTURED
    reservation.status = ReservationStatus.CONFIRMED
    reservation.hold_expires_at = None
    if record is None:
        raise RuntimeError("Idempotency record was not created")
    finish_idempotent(
        record,
        {"id": str(reservation.id), "status": ReservationStatus.CONFIRMED.value},
        200,
    )
    db.session.commit()
    schedule_reminder(reservation)
    return reservation


def process_webhook(raw_body: bytes, signature: str | None, event_id: str | None) -> bool:
    secret = current_app.config.get("RAZORPAY_WEBHOOK_SECRET", "")
    if not secret or not signature:
        raise ApiProblem("INVALID_WEBHOOK_SIGNATURE", "Webhook signature verification failed.", 401)
    expected = hmac.new(secret.encode(), raw_body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, signature):
        raise ApiProblem("INVALID_WEBHOOK_SIGNATURE", "Webhook signature verification failed.", 401)
    try:
        payload = json.loads(raw_body)
    except json.JSONDecodeError as exc:
        raise ApiProblem("INVALID_WEBHOOK", "Webhook body is not valid JSON.", 422) from exc
    provider_event_id = event_id or _derived_event_id(payload)
    if db.session.scalar(
        select(WebhookEvent.id).where(
            WebhookEvent.provider == "razorpay",
            WebhookEvent.provider_event_id == provider_event_id,
        )
    ):
        return False
    event = WebhookEvent(
        provider="razorpay",
        provider_event_id=provider_event_id,
        payload_hash=hashlib.sha256(raw_body).hexdigest(),
        outcome="ignored",
    )
    db.session.add(event)
    event_name = payload.get("event", "")
    payment_entity = payload.get("payload", {}).get("payment", {}).get("entity", {})
    provider_payment_id = payment_entity.get("id")
    order_id = payment_entity.get("order_id")
    payment = (
        db.session.scalar(select(Payment).where(Payment.provider_order_id == order_id))
        if order_id
        else None
    )
    if payment and event_name in {"payment.captured", "order.paid"}:
        payment.provider_payment_id = provider_payment_id
        payment.status = PaymentStatus.CAPTURED
        payment.reservation.status = ReservationStatus.CONFIRMED
        payment.reservation.hold_expires_at = None
        event.outcome = "payment_captured"
    elif payment and event_name == "payment.failed":
        payment.status = PaymentStatus.FAILED
        event.outcome = "payment_failed"
    should_schedule = event.outcome == "payment_captured"
    db.session.commit()
    if should_schedule and payment:
        schedule_reminder(payment.reservation)
    return True


def _derived_event_id(payload: dict[str, Any]) -> str:
    event = str(payload.get("event", "unknown"))
    entity = payload.get("payload", {}).get("payment", {}).get("entity", {})
    identity = str(entity.get("id") or entity.get("order_id") or "missing")
    return hashlib.sha256(f"{event}:{identity}".encode()).hexdigest()


def refund_payment(reservation: Reservation) -> None:
    payment = db.session.scalar(select(Payment).where(Payment.reservation_id == reservation.id))
    if (
        not payment
        or payment.status is not PaymentStatus.CAPTURED
        or not payment.provider_payment_id
    ):
        return
    _client().payment.refund(
        payment.provider_payment_id,
        {"amount": payment.amount_paise, "notes": {"reservation_id": str(reservation.id)}},
    )
    payment.status = PaymentStatus.REFUNDED
    payment.refunded_at = datetime.now(UTC)
