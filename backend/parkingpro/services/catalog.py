from __future__ import annotations

import math
import re
import uuid
from datetime import UTC, datetime, time, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from geoalchemy2 import Geography, Geometry
from sqlalchemy import and_, cast, exists, func, not_, or_, select
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy.sql import Select
from sqlalchemy.sql.elements import ColumnElement

from parkingpro.errors import ApiProblem
from parkingpro.extensions import db
from parkingpro.models import (
    OperationalState,
    ParkingLot,
    ParkingSpot,
    Reservation,
    ReservationStatus,
    SpotType,
    User,
    Vehicle,
)

ACTIVE_RESERVATION_STATES = (
    ReservationStatus.HELD,
    ReservationStatus.CONFIRMED,
    ReservationStatus.CHECKED_IN,
)


def active_reservation_predicate() -> ColumnElement[bool]:
    """Treat an elapsed hold as inactive even before its cleanup job runs."""
    return or_(
        Reservation.status.in_((ReservationStatus.CONFIRMED, ReservationStatus.CHECKED_IN)),
        and_(
            Reservation.status == ReservationStatus.HELD,
            Reservation.hold_expires_at > datetime.now(UTC),
        ),
    )


def validate_booking_window(starts_at: datetime, ends_at: datetime) -> int:
    starts_at = starts_at.astimezone(UTC)
    ends_at = ends_at.astimezone(UTC)
    duration_minutes = int((ends_at - starts_at).total_seconds() / 60)
    if starts_at.second or starts_at.microsecond or starts_at.minute % 30:
        raise ApiProblem("INVALID_TIME_SLOT", "Bookings must begin on a 30-minute boundary.", 422)
    if ends_at.second or ends_at.microsecond or ends_at.minute % 30:
        raise ApiProblem("INVALID_TIME_SLOT", "Bookings must end on a 30-minute boundary.", 422)
    if duration_minutes < 30 or duration_minutes > 24 * 60 or duration_minutes % 30:
        raise ApiProblem(
            "INVALID_DURATION", "Bookings must last between 30 minutes and 24 hours.", 422
        )
    if starts_at < datetime.now(UTC).replace(second=0, microsecond=0):
        raise ApiProblem("INVALID_TIME_SLOT", "Bookings cannot start in the past.", 422)
    return duration_minutes


def quote_amount(rate_paise: int, duration_minutes: int) -> int:
    return math.ceil(rate_paise * duration_minutes / 60)


def lot_accepts_window(lot: ParkingLot, starts_at: datetime, ends_at: datetime) -> bool:
    """Return whether a UTC booking window fits one local operating interval."""
    if lot.opens_at == "00:00" and lot.closes_at == "23:59":
        return True
    zone = ZoneInfo(lot.timezone)
    local_start = starts_at.astimezone(zone)
    local_end = ends_at.astimezone(zone)

    def parse_clock(value: str) -> time:
        hour, minute = (int(part) for part in value.split(":"))
        return time(hour, minute)

    opens = parse_clock(lot.opens_at)
    closes = parse_clock(lot.closes_at)
    opening_date = local_start.date()
    if closes <= opens and local_start.time() <= closes:
        opening_date -= timedelta(days=1)
    opening = datetime.combine(opening_date, opens, zone)
    closing_date = opening_date + (timedelta(days=1) if closes <= opens else timedelta())
    closing = datetime.combine(closing_date, closes, zone)
    return local_start >= opening and local_end <= closing


def require_open_window(lot: ParkingLot, starts_at: datetime, ends_at: datetime) -> None:
    if not lot_accepts_window(lot, starts_at, ends_at):
        raise ApiProblem(
            "FACILITY_CLOSED",
            "The facility is closed for part of the selected time.",
            409,
        )


def _overlap_exists(starts_at: datetime, ends_at: datetime) -> ColumnElement[bool]:
    return exists(
        select(Reservation.id).where(
            Reservation.spot_id == ParkingSpot.id,
            active_reservation_predicate(),
            Reservation.starts_at < ends_at,
            Reservation.ends_at > starts_at,
        )
    )


def available_spots_query(
    lot_id: uuid.UUID | InstrumentedAttribute[uuid.UUID],
    starts_at: datetime | None = None,
    ends_at: datetime | None = None,
    spot_type: SpotType | None = None,
) -> Select[tuple[ParkingSpot]]:
    conditions = [
        ParkingSpot.lot_id == lot_id,
        ParkingSpot.state == OperationalState.ACTIVE,
    ]
    if spot_type:
        conditions.append(ParkingSpot.spot_type == spot_type)
    if starts_at and ends_at:
        conditions.append(not_(_overlap_exists(starts_at, ends_at)))
    return select(ParkingSpot).where(*conditions)


def lot_payload(
    lot: ParkingLot,
    *,
    distance_m: float | None = None,
    starts_at: datetime | None = None,
    ends_at: datetime | None = None,
    spot_type: SpotType | None = None,
) -> dict[str, Any]:
    geometry = cast(ParkingLot.location, Geometry(geometry_type="POINT", srid=4326))
    lon, lat = db.session.execute(
        select(func.ST_X(geometry), func.ST_Y(geometry)).where(ParkingLot.id == lot.id)
    ).one()
    total_conditions = [
        ParkingSpot.lot_id == lot.id,
        ParkingSpot.state == OperationalState.ACTIVE,
    ]
    if spot_type:
        total_conditions.append(ParkingSpot.spot_type == spot_type)
    total = db.session.scalar(select(func.count(ParkingSpot.id)).where(*total_conditions)) or 0
    available = (
        db.session.scalar(
            select(func.count()).select_from(
                available_spots_query(lot.id, starts_at, ends_at, spot_type).subquery()
            )
        )
        or 0
    )
    return {
        "id": lot.id,
        "name": lot.name,
        "address": lot.address,
        "latitude": float(lat),
        "longitude": float(lon),
        "distance_m": round(distance_m, 1) if distance_m is not None else None,
        "timezone": lot.timezone,
        "opens_at": lot.opens_at,
        "closes_at": lot.closes_at,
        "base_rate_paise": lot.base_rate_paise,
        "state": lot.state.value,
        "total_spots": total,
        "available_spots": available,
    }


def search_lots(data: dict[str, Any]) -> list[dict[str, Any]]:
    starts_at, ends_at = data.get("starts_at"), data.get("ends_at")
    if starts_at and ends_at:
        validate_booking_window(starts_at, ends_at)
    spot_type = SpotType(data["spot_type"]) if data.get("spot_type") else None
    origin = func.ST_SetSRID(func.ST_MakePoint(data["longitude"], data["latitude"]), 4326)
    origin_geography = cast(origin, Geography)
    distance = func.ST_Distance(ParkingLot.location, origin_geography)
    query = (
        select(ParkingLot, distance.label("distance_m"))
        .where(
            ParkingLot.state == OperationalState.ACTIVE,
            func.ST_DWithin(ParkingLot.location, origin_geography, data["radius_m"]),
            exists(
                available_spots_query(ParkingLot.id, starts_at, ends_at, spot_type).correlate(
                    ParkingLot
                )
            ),
        )
        .order_by(distance)
        .limit(100)
    )
    return [
        lot_payload(
            lot,
            distance_m=float(distance_m),
            starts_at=starts_at,
            ends_at=ends_at,
            spot_type=spot_type,
        )
        for lot, distance_m in db.session.execute(query)
        if not starts_at or not ends_at or lot_accepts_window(lot, starts_at, ends_at)
    ]


def get_lot(lot_id: uuid.UUID) -> ParkingLot:
    lot = db.session.get(ParkingLot, lot_id)
    if not lot or lot.state is not OperationalState.ACTIVE:
        raise ApiProblem("RESOURCE_NOT_FOUND", "The parking facility was not found.", 404)
    return lot


def create_quote(lot_id: uuid.UUID, data: dict[str, Any]) -> dict[str, Any]:
    lot = get_lot(lot_id)
    duration = validate_booking_window(data["starts_at"], data["ends_at"])
    require_open_window(lot, data["starts_at"], data["ends_at"])
    spot_type = SpotType(data["spot_type"])
    available = (
        db.session.scalar(
            select(func.count()).select_from(
                available_spots_query(
                    lot.id, data["starts_at"], data["ends_at"], spot_type
                ).subquery()
            )
        )
        or 0
    )
    if available == 0:
        raise ApiProblem("NO_AVAILABILITY", "No eligible spots are available for this time.", 409)
    return {
        "lot_id": lot.id,
        "starts_at": data["starts_at"],
        "ends_at": data["ends_at"],
        "duration_minutes": duration,
        "amount_paise": quote_amount(lot.base_rate_paise, duration),
        "currency": "INR",
        "available_spots": available,
    }


def normalize_registration(value: str) -> str:
    normalized = re.sub(r"[^A-Z0-9]", "", value.upper())
    if len(normalized) < 4:
        raise ApiProblem("INVALID_REGISTRATION", "Enter a valid vehicle registration number.", 422)
    return normalized


def vehicle_payload(vehicle: Vehicle) -> dict[str, Any]:
    return {
        "id": vehicle.id,
        "registration_number": vehicle.registration_number,
        "label": vehicle.label,
        "vehicle_type": vehicle.vehicle_type.value,
    }


def list_vehicles(user: User) -> list[dict[str, Any]]:
    vehicles = db.session.scalars(
        select(Vehicle).where(Vehicle.owner_id == user.id).order_by(Vehicle.created_at)
    ).all()
    return [vehicle_payload(vehicle) for vehicle in vehicles]


def create_vehicle(user: User, data: dict[str, Any]) -> Vehicle:
    vehicle = Vehicle(
        owner_id=user.id,
        registration_number=normalize_registration(data["registration_number"]),
        label=data.get("label"),
        vehicle_type=SpotType(data["vehicle_type"]),
    )
    db.session.add(vehicle)
    db.session.commit()
    return vehicle


def update_vehicle(user: User, vehicle_id: uuid.UUID, data: dict[str, Any]) -> Vehicle:
    vehicle = db.session.scalar(
        select(Vehicle).where(Vehicle.id == vehicle_id, Vehicle.owner_id == user.id)
    )
    if not vehicle:
        raise ApiProblem("RESOURCE_NOT_FOUND", "The vehicle was not found.", 404)
    if "registration_number" in data:
        vehicle.registration_number = normalize_registration(data["registration_number"])
    if "label" in data:
        vehicle.label = data["label"]
    if "vehicle_type" in data:
        vehicle.vehicle_type = SpotType(data["vehicle_type"])
    db.session.commit()
    return vehicle


def delete_vehicle(user: User, vehicle_id: uuid.UUID) -> None:
    vehicle = db.session.scalar(
        select(Vehicle).where(Vehicle.id == vehicle_id, Vehicle.owner_id == user.id)
    )
    if not vehicle:
        raise ApiProblem("RESOURCE_NOT_FOUND", "The vehicle was not found.", 404)
    if db.session.scalar(
        select(Reservation.id).where(
            Reservation.vehicle_id == vehicle.id,
            active_reservation_predicate(),
        )
    ):
        raise ApiProblem("VEHICLE_IN_USE", "This vehicle has an active reservation.", 409)
    db.session.delete(vehicle)
    db.session.commit()
