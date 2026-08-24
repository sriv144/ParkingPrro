from __future__ import annotations

import uuid
from datetime import UTC, datetime

import httpx
from flask import current_app
from qstash import QStash
from sqlalchemy import select

from parkingpro.extensions import db
from parkingpro.models import DevicePushToken, Reservation, ReservationStatus, User


def register_push_token(user: User, token: str, platform: str) -> DevicePushToken:
    existing = db.session.scalar(select(DevicePushToken).where(DevicePushToken.token == token))
    if existing:
        existing.user_id = user.id
        existing.platform = platform
        existing.active = True
        device = existing
    else:
        device = DevicePushToken(
            user_id=user.id,
            token=token,
            platform=platform,
            active=True,
        )
        db.session.add(device)
    db.session.commit()
    return device


def deactivate_push_token(user: User, token: str) -> None:
    device = db.session.scalar(
        select(DevicePushToken).where(
            DevicePushToken.user_id == user.id,
            DevicePushToken.token == token,
        )
    )
    if device:
        device.active = False
        db.session.commit()


def schedule_reminder(reservation: Reservation) -> None:
    token = current_app.config.get("QSTASH_TOKEN")
    public_url = current_app.config.get("PUBLIC_API_URL")
    if not token or not public_url:
        current_app.logger.info("reminder_skipped reservation_id=%s", reservation.id)
        return
    delay_seconds = int((reservation.starts_at - datetime.now(UTC)).total_seconds() - 30 * 60)
    if delay_seconds <= 0:
        return
    try:
        QStash(token).message.publish_json(
            url=f"{public_url}/api/v1/internal/jobs/send-reminder",
            body={"reservation_id": str(reservation.id)},
            delay=f"{delay_seconds}s",
            retries=3,
        )
    except Exception:
        current_app.logger.exception(
            "reminder_publish_failed",
            extra={"reservation_id": str(reservation.id)},
        )


def send_reservation_reminder(reservation_id: uuid.UUID) -> int:
    reservation = db.session.get(Reservation, reservation_id)
    if not reservation or reservation.status is not ReservationStatus.CONFIRMED:
        return 0
    tokens = db.session.scalars(
        select(DevicePushToken).where(
            DevicePushToken.user_id == reservation.driver_id,
            DevicePushToken.active.is_(True),
        )
    ).all()
    if not tokens:
        return 0
    messages = [
        {
            "to": token.token,
            "title": "Parking starts in 30 minutes",
            "body": f"{reservation.spot.lot.name} · Spot {reservation.spot.code}",
            "data": {"reservation_id": str(reservation.id)},
            "sound": "default",
        }
        for token in tokens
    ]
    response = httpx.post(
        "https://exp.host/--/api/v2/push/send",
        json=messages,
        headers={"Accept": "application/json", "Content-Type": "application/json"},
        timeout=10,
    )
    response.raise_for_status()
    return len(messages)
