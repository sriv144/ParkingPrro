from __future__ import annotations

import hashlib
import json
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from flask import current_app
from itsdangerous import BadSignature, URLSafeSerializer
from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError

from parkingpro.errors import ApiProblem
from parkingpro.extensions import db
from parkingpro.models import (
    IdempotencyRecord,
    ParkingSpot,
    Reservation,
    ReservationStatus,
    SpotType,
    User,
    Vehicle,
)
from parkingpro.services.catalog import (
    available_spots_query,
    get_lot,
    quote_amount,
    require_open_window,
    validate_booking_window,
)


def _serializer() -> URLSafeSerializer:
    return URLSafeSerializer(current_app.config["QR_SIGNING_KEY"], salt="parkingpro-qr-v1")


def sign_qr(reservation: Reservation) -> str:
    return _serializer().dumps(
        {"rid": str(reservation.id), "nonce": str(reservation.qr_nonce), "v": 1}
    )


def parse_qr(value: str) -> tuple[uuid.UUID, uuid.UUID]:
    try:
        payload = _serializer().loads(value)
        return uuid.UUID(payload["rid"]), uuid.UUID(payload["nonce"])
    except (BadSignature, KeyError, TypeError, ValueError) as exc:
        raise ApiProblem("INVALID_QR_PASS", "This parking pass is invalid.", 422) from exc


def reservation_payload(reservation: Reservation, *, include_qr: bool = True) -> dict[str, Any]:
    return {
        "id": reservation.id,
        "lot_id": reservation.spot.lot_id,
        "lot_name": reservation.spot.lot.name,
        "spot_code": reservation.spot.code,
        "vehicle_id": reservation.vehicle_id,
        "registration_number": reservation.vehicle.registration_number,
        "starts_at": reservation.starts_at,
        "ends_at": reservation.ends_at,
        "quoted_amount_paise": reservation.quoted_amount_paise,
        "status": reservation.status.value,
        "hold_expires_at": reservation.hold_expires_at,
        "qr_payload": (
            sign_qr(reservation)
            if include_qr
            and reservation.status in (ReservationStatus.CONFIRMED, ReservationStatus.CHECKED_IN)
            else None
        ),
    }


def _request_hash(data: dict[str, Any]) -> str:
    encoded = json.dumps(data, sort_keys=True, default=str, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def require_idempotency_key(value: str | None) -> str:
    if not value or len(value) < 16 or len(value) > 120:
        raise ApiProblem(
            "IDEMPOTENCY_KEY_REQUIRED",
            "Provide a unique Idempotency-Key between 16 and 120 characters.",
            400,
        )
    return value


def replay_idempotent(
    user: User, route: str, key: str, data: dict[str, Any]
) -> tuple[dict[str, Any] | None, int | None, IdempotencyRecord | None]:
    request_hash = _request_hash(data)
    existing = db.session.scalar(
        select(IdempotencyRecord).where(
            IdempotencyRecord.actor_id == user.id,
            IdempotencyRecord.route == route,
            IdempotencyRecord.key == key,
        )
    )
    if existing:
        if existing.request_hash != request_hash:
            raise ApiProblem(
                "IDEMPOTENCY_KEY_REUSED",
                "This Idempotency-Key was already used with a different request.",
                409,
            )
        if existing.response_body is None or existing.response_status is None:
            raise ApiProblem(
                "REQUEST_IN_PROGRESS", "The original request is still processing.", 409
            )
        return existing.response_body, existing.response_status, existing
    record = IdempotencyRecord(
        actor_id=user.id,
        route=route,
        key=key,
        request_hash=request_hash,
    )
    db.session.add(record)
    db.session.flush()
    return None, None, record


def finish_idempotent(record: IdempotencyRecord, payload: dict[str, Any], status: int) -> None:
    record.response_body = json.loads(json.dumps(payload, default=str))
    record.response_status = status


def create_hold(
    user: User, data: dict[str, Any], idempotency_key: str
) -> tuple[dict[str, Any], int]:
    key = require_idempotency_key(idempotency_key)
    replay, status, record = replay_idempotent(user, "POST:/api/v1/reservations", key, data)
    if replay is not None:
        try:
            reservation_id = uuid.UUID(str(replay["id"]))
        except (KeyError, ValueError) as exc:
            raise ApiProblem(
                "IDEMPOTENCY_RECORD_INVALID", "The saved response is invalid.", 500
            ) from exc
        reservation = db.session.get(Reservation, reservation_id)
        if not reservation:
            raise ApiProblem(
                "IDEMPOTENCY_RECORD_INVALID", "The saved response is unavailable.", 500
            )
        return reservation_payload(reservation, include_qr=False), status or 201

    duration = validate_booking_window(data["starts_at"], data["ends_at"])
    lot = get_lot(data["lot_id"])
    require_open_window(lot, data["starts_at"], data["ends_at"])
    vehicle = db.session.scalar(
        select(Vehicle).where(Vehicle.id == data["vehicle_id"], Vehicle.owner_id == user.id)
    )
    if not vehicle:
        raise ApiProblem("RESOURCE_NOT_FOUND", "The selected vehicle was not found.", 404)
    requested_type = SpotType(data["spot_type"])
    if vehicle.vehicle_type is SpotType.BIKE and requested_type is not SpotType.BIKE:
        raise ApiProblem("VEHICLE_SPOT_MISMATCH", "Select a motorcycle spot for this vehicle.", 422)

    # QStash is an accelerator, not a correctness boundary. Clear stale rows in
    # the booking transaction before the exclusion constraint is evaluated.
    db.session.execute(
        update(Reservation)
        .where(
            Reservation.status == ReservationStatus.HELD,
            Reservation.hold_expires_at <= datetime.now(UTC),
        )
        .values(status=ReservationStatus.EXPIRED, updated_at=func.now())
        .execution_options(synchronize_session=False)
    )
    db.session.flush()

    spot = db.session.scalar(
        available_spots_query(lot.id, data["starts_at"], data["ends_at"], requested_type)
        .order_by(ParkingSpot.code)
        .with_for_update(skip_locked=True)
        .limit(1)
    )
    if not spot:
        raise ApiProblem("RESERVATION_CONFLICT", "This spot is no longer available.", 409)

    reservation = Reservation(
        driver_id=user.id,
        vehicle_id=vehicle.id,
        spot_id=spot.id,
        starts_at=data["starts_at"],
        ends_at=data["ends_at"],
        quoted_amount_paise=quote_amount(lot.base_rate_paise, duration),
        status=ReservationStatus.HELD,
        hold_expires_at=datetime.now(UTC) + timedelta(minutes=10),
    )
    db.session.add(reservation)
    try:
        db.session.flush()
        payload = reservation_payload(reservation, include_qr=False)
        if record is None:
            raise RuntimeError("Idempotency record was not created")
        finish_idempotent(record, payload, 201)
        db.session.commit()
    except IntegrityError as exc:
        db.session.rollback()
        raise ApiProblem("RESERVATION_CONFLICT", "This spot is no longer available.", 409) from exc
    schedule_hold_expiry(reservation)
    return payload, 201


def schedule_hold_expiry(reservation: Reservation) -> None:
    token = current_app.config.get("QSTASH_TOKEN")
    public_url = current_app.config.get("PUBLIC_API_URL")
    if not token or not public_url:
        current_app.logger.info("qstash_skipped reservation_id=%s", reservation.id)
        return
    from qstash import QStash

    try:
        QStash(token).message.publish_json(
            url=f"{public_url}/api/v1/internal/jobs/expire-reservation",
            body={"reservation_id": str(reservation.id)},
            delay="10m",
            retries=3,
        )
    except Exception:
        current_app.logger.exception(
            "qstash_publish_failed",
            extra={"reservation_id": str(reservation.id)},
        )


def list_reservations(user: User) -> list[dict[str, Any]]:
    reservations = db.session.scalars(
        select(Reservation)
        .where(Reservation.driver_id == user.id)
        .order_by(Reservation.starts_at.desc())
        .limit(100)
    ).all()
    return [reservation_payload(item) for item in reservations]


def get_reservation(user: User, reservation_id: uuid.UUID) -> Reservation:
    reservation = db.session.scalar(
        select(Reservation).where(
            Reservation.id == reservation_id,
            Reservation.driver_id == user.id,
        )
    )
    if not reservation:
        raise ApiProblem("RESOURCE_NOT_FOUND", "The reservation was not found.", 404)
    expire_if_needed(reservation)
    return reservation


def expire_if_needed(reservation: Reservation) -> bool:
    if (
        reservation.status is ReservationStatus.HELD
        and reservation.hold_expires_at
        and reservation.hold_expires_at <= datetime.now(UTC)
    ):
        reservation.status = ReservationStatus.EXPIRED
        db.session.commit()
        return True
    return False


def expire_reservation(reservation_id: uuid.UUID) -> bool:
    reservation = db.session.get(Reservation, reservation_id)
    return bool(reservation and expire_if_needed(reservation))


def cancel_reservation(user: User, reservation_id: uuid.UUID, idempotency_key: str) -> Reservation:
    key = require_idempotency_key(idempotency_key)
    replay, _, record = replay_idempotent(
        user,
        f"POST:/api/v1/reservations/{reservation_id}/cancel",
        key,
        {"reservation_id": str(reservation_id)},
    )
    if replay is not None:
        return get_reservation(user, reservation_id)
    reservation = get_reservation(user, reservation_id)
    if reservation.status not in (ReservationStatus.HELD, ReservationStatus.CONFIRMED):
        raise ApiProblem(
            "CANCELLATION_NOT_ALLOWED", "This reservation can no longer be cancelled.", 409
        )
    if datetime.now(UTC) >= reservation.starts_at:
        raise ApiProblem(
            "CANCELLATION_NOT_ALLOWED", "Started reservations cannot be cancelled.", 409
        )
    if reservation.status is ReservationStatus.CONFIRMED:
        from parkingpro.services.payments import refund_payment

        refund_payment(reservation)
    reservation.status = ReservationStatus.CANCELLED
    reservation.cancelled_at = datetime.now(UTC)
    reservation.qr_nonce = uuid.uuid4()
    if record is None:
        raise RuntimeError("Idempotency record was not created")
    finish_idempotent(record, {"id": str(reservation.id), "status": "cancelled"}, 200)
    db.session.commit()
    return reservation


def validate_scan(qr_payload: str, allowed_lot_ids: set[uuid.UUID]) -> Reservation:
    reservation_id, nonce = parse_qr(qr_payload)
    reservation = db.session.get(Reservation, reservation_id)
    if not reservation or reservation.spot.lot_id not in allowed_lot_ids:
        raise ApiProblem("RESOURCE_NOT_FOUND", "This pass is not for an assigned facility.", 404)
    if reservation.qr_nonce != nonce:
        raise ApiProblem("QR_REPLAY_REJECTED", "This parking pass has already been used.", 409)
    if reservation.status is not ReservationStatus.CONFIRMED:
        raise ApiProblem("INVALID_RESERVATION_STATE", "This pass is not ready for check-in.", 409)
    return reservation
