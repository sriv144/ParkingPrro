from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any
from zoneinfo import ZoneInfo

from flask import g
from geoalchemy2.elements import WKTElement
from sqlalchemy import func, select

from parkingpro.errors import ApiProblem
from parkingpro.extensions import db
from parkingpro.models import (
    AuditEvent,
    OperationalState,
    OperatorLot,
    ParkingLot,
    ParkingSpot,
    Payment,
    PaymentStatus,
    Reservation,
    ReservationStatus,
    SpotType,
    User,
)
from parkingpro.services.catalog import active_reservation_predicate, lot_payload
from parkingpro.services.reservations import reservation_payload, validate_scan


def assigned_lot_ids(operator: User) -> set[uuid.UUID]:
    return set(
        db.session.scalars(
            select(OperatorLot.lot_id).where(OperatorLot.operator_id == operator.id)
        ).all()
    )


def require_assigned_lot(operator: User, lot_id: uuid.UUID) -> ParkingLot:
    if lot_id not in assigned_lot_ids(operator):
        raise ApiProblem("RESOURCE_NOT_FOUND", "The parking facility was not found.", 404)
    lot = db.session.get(ParkingLot, lot_id)
    if not lot:
        raise ApiProblem("RESOURCE_NOT_FOUND", "The parking facility was not found.", 404)
    return lot


def overview(operator: User) -> dict[str, Any]:
    lot_ids = assigned_lot_ids(operator)
    if not lot_ids:
        return {
            "occupied_spots": 0,
            "total_spots": 0,
            "occupancy_percent": 0.0,
            "active_reservations": 0,
            "revenue_today_paise": 0,
            "completed_today": 0,
        }
    total = (
        db.session.scalar(
            select(func.count(ParkingSpot.id)).where(
                ParkingSpot.lot_id.in_(lot_ids),
                ParkingSpot.state == OperationalState.ACTIVE,
            )
        )
        or 0
    )
    occupied = (
        db.session.scalar(
            select(func.count(Reservation.id))
            .join(ParkingSpot)
            .where(
                ParkingSpot.lot_id.in_(lot_ids),
                Reservation.status == ReservationStatus.CHECKED_IN,
            )
        )
        or 0
    )
    active = (
        db.session.scalar(
            select(func.count(Reservation.id))
            .join(ParkingSpot)
            .where(
                ParkingSpot.lot_id.in_(lot_ids),
                active_reservation_predicate(),
            )
        )
        or 0
    )
    today = (
        datetime.now(ZoneInfo("Asia/Kolkata"))
        .replace(hour=0, minute=0, second=0, microsecond=0)
        .astimezone(UTC)
    )
    revenue = (
        db.session.scalar(
            select(func.coalesce(func.sum(Payment.amount_paise), 0))
            .join(Reservation, Payment.reservation_id == Reservation.id)
            .join(ParkingSpot, Reservation.spot_id == ParkingSpot.id)
            .where(
                ParkingSpot.lot_id.in_(lot_ids),
                Payment.status == PaymentStatus.CAPTURED,
                Payment.created_at >= today,
            )
        )
        or 0
    )
    completed = (
        db.session.scalar(
            select(func.count(Reservation.id))
            .join(ParkingSpot)
            .where(
                ParkingSpot.lot_id.in_(lot_ids),
                Reservation.status == ReservationStatus.COMPLETED,
                Reservation.completed_at >= today,
            )
        )
        or 0
    )
    return {
        "occupied_spots": occupied,
        "total_spots": total,
        "occupancy_percent": round((occupied / total * 100) if total else 0, 1),
        "active_reservations": active,
        "revenue_today_paise": revenue,
        "completed_today": completed,
    }


def list_operator_lots(operator: User) -> list[dict[str, Any]]:
    lot_ids = assigned_lot_ids(operator)
    lots = db.session.scalars(
        select(ParkingLot).where(ParkingLot.id.in_(lot_ids)).order_by(ParkingLot.name)
    ).all()
    return [lot_payload(lot) for lot in lots]


def create_operator_lot(operator: User, data: dict[str, Any]) -> ParkingLot:
    lot = ParkingLot(
        name=data["name"].strip(),
        address=data["address"].strip(),
        location=WKTElement(f"POINT({data['longitude']} {data['latitude']})", srid=4326),
        opens_at=data["opens_at"],
        closes_at=data["closes_at"],
        base_rate_paise=data["base_rate_paise"],
    )
    db.session.add(lot)
    db.session.flush()
    db.session.add(OperatorLot(operator_id=operator.id, lot_id=lot.id))
    for number in range(1, data["capacity"] + 1):
        db.session.add(
            ParkingSpot(
                lot_id=lot.id,
                code=f"A-{number:03d}",
                spot_type=SpotType.EV if number % 10 == 0 else SpotType.CAR,
            )
        )
    audit(operator, "operator.lot.created", "parking_lot", lot.id, {"capacity": data["capacity"]})
    db.session.commit()
    return lot


def update_operator_lot(operator: User, lot_id: uuid.UUID, data: dict[str, Any]) -> ParkingLot:
    lot = require_assigned_lot(operator, lot_id)
    before = {
        "name": lot.name,
        "address": lot.address,
        "opens_at": lot.opens_at,
        "closes_at": lot.closes_at,
        "base_rate_paise": lot.base_rate_paise,
        "state": lot.state.value,
    }
    for name in ("name", "address", "opens_at", "closes_at", "base_rate_paise"):
        if name in data:
            setattr(lot, name, data[name])
    if "state" in data:
        lot.state = OperationalState(data["state"])
    audit(
        operator,
        "operator.lot.updated",
        "parking_lot",
        lot.id,
        {"before": before, "changed": list(data)},
    )
    db.session.commit()
    return lot


def spot_payload(spot: ParkingSpot) -> dict[str, Any]:
    return {
        "id": spot.id,
        "lot_id": spot.lot_id,
        "code": spot.code,
        "spot_type": spot.spot_type.value,
        "state": spot.state.value,
    }


def list_operator_spots(operator: User, lot_id: uuid.UUID) -> list[dict[str, Any]]:
    require_assigned_lot(operator, lot_id)
    spots = db.session.scalars(
        select(ParkingSpot).where(ParkingSpot.lot_id == lot_id).order_by(ParkingSpot.code)
    ).all()
    return [spot_payload(spot) for spot in spots]


def update_operator_spot(
    operator: User, spot_id: uuid.UUID, state: OperationalState
) -> ParkingSpot:
    spot = db.session.get(ParkingSpot, spot_id)
    if not spot or spot.lot_id not in assigned_lot_ids(operator):
        raise ApiProblem("RESOURCE_NOT_FOUND", "The parking spot was not found.", 404)
    if state is OperationalState.OUT_OF_SERVICE and db.session.scalar(
        select(Reservation.id).where(
            Reservation.spot_id == spot.id,
            active_reservation_predicate(),
        )
    ):
        raise ApiProblem("SPOT_IN_USE", "An active reservation is assigned to this spot.", 409)
    spot.state = state
    audit(operator, "operator.spot.updated", "parking_spot", spot.id, {"state": state.value})
    db.session.commit()
    return spot


def list_operator_reservations(operator: User) -> list[dict[str, Any]]:
    lot_ids = assigned_lot_ids(operator)
    reservations = db.session.scalars(
        select(Reservation)
        .join(ParkingSpot)
        .where(ParkingSpot.lot_id.in_(lot_ids))
        .order_by(Reservation.starts_at.desc())
        .limit(250)
    ).all()
    return [reservation_payload(item, include_qr=False) for item in reservations]


def scan_pass(operator: User, qr_payload: str) -> Reservation:
    return validate_scan(qr_payload, assigned_lot_ids(operator))


def transition_reservation(
    operator: User, reservation_id: uuid.UUID, target: ReservationStatus
) -> Reservation:
    reservation = db.session.get(Reservation, reservation_id)
    lot_ids = assigned_lot_ids(operator)
    if not reservation or reservation.spot.lot_id not in lot_ids:
        raise ApiProblem("RESOURCE_NOT_FOUND", "The reservation was not found.", 404)
    if reservation.status is target:
        return reservation
    if target is ReservationStatus.CHECKED_IN and reservation.status is ReservationStatus.CONFIRMED:
        reservation.status = target
        reservation.checked_in_at = datetime.now(UTC)
        reservation.qr_nonce = uuid.uuid4()
        action = "reservation.checked_in"
    elif (
        target is ReservationStatus.COMPLETED and reservation.status is ReservationStatus.CHECKED_IN
    ):
        reservation.status = target
        reservation.completed_at = datetime.now(UTC)
        reservation.qr_nonce = uuid.uuid4()
        action = "reservation.checked_out"
    else:
        raise ApiProblem("INVALID_RESERVATION_STATE", "This transition is not allowed.", 409)
    audit(operator, action, "reservation", reservation.id, {"status": reservation.status.value})
    db.session.commit()
    return reservation


def audit(
    actor: User,
    action: str,
    target_type: str,
    target_id: uuid.UUID,
    metadata: dict[str, Any],
) -> None:
    db.session.add(
        AuditEvent(
            actor_id=actor.id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            request_id=g.get("request_id", ""),
            metadata_json=metadata,
        )
    )
