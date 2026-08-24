from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum
from typing import Any

from geoalchemy2 import Geography
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, ExcludeConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from parkingpro.extensions import Base


class Role(StrEnum):
    DRIVER = "driver"
    OPERATOR = "operator"
    ADMIN = "admin"


class AccountState(StrEnum):
    ACTIVE = "active"
    DISABLED = "disabled"


class SpotType(StrEnum):
    CAR = "car"
    BIKE = "bike"
    EV = "ev"
    ACCESSIBLE = "accessible"


class OperationalState(StrEnum):
    ACTIVE = "active"
    OUT_OF_SERVICE = "out_of_service"


class ReservationStatus(StrEnum):
    HELD = "held"
    CONFIRMED = "confirmed"
    CHECKED_IN = "checked_in"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class PaymentStatus(StrEnum):
    CREATED = "created"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    FAILED = "failed"
    REFUNDED = "refunded"


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class User(TimestampMixin, Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(512), nullable=False)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(24))
    role: Mapped[Role] = mapped_column(
        Enum(Role, name="user_role"), default=Role.DRIVER, nullable=False
    )
    state: Mapped[AccountState] = mapped_column(
        Enum(AccountState, name="account_state"), default=AccountState.ACTIVE, nullable=False
    )
    vehicles: Mapped[list[Vehicle]] = relationship(
        back_populates="owner", cascade="all, delete-orphan"
    )
    reservations: Mapped[list[Reservation]] = relationship(back_populates="driver")


class RefreshSession(TimestampMixin, Base):
    __tablename__ = "refresh_sessions"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    csrf_hash: Mapped[str | None] = mapped_column(String(64))
    device_name: Mapped[str] = mapped_column(String(120), default="unknown", nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    user: Mapped[User] = relationship()


class DevicePushToken(TimestampMixin, Base):
    __tablename__ = "device_push_tokens"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    platform: Mapped[str] = mapped_column(String(24), nullable=False)
    active: Mapped[bool] = mapped_column(default=True, nullable=False)
    user: Mapped[User] = relationship()


class Vehicle(TimestampMixin, Base):
    __tablename__ = "vehicles"
    __table_args__ = (UniqueConstraint("owner_id", "registration_number"),)
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    owner_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    registration_number: Mapped[str] = mapped_column(String(20), nullable=False)
    label: Mapped[str | None] = mapped_column(String(60))
    vehicle_type: Mapped[SpotType] = mapped_column(Enum(SpotType, name="spot_type"), nullable=False)
    owner: Mapped[User] = relationship(back_populates="vehicles")


class ParkingLot(TimestampMixin, Base):
    __tablename__ = "parking_lots"
    __table_args__ = (
        CheckConstraint("base_rate_paise > 0", name="ck_lot_positive_rate"),
        Index("ix_parking_lots_location", "location", postgresql_using="gist"),
    )
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    address: Mapped[str] = mapped_column(String(320), nullable=False)
    location: Mapped[Any] = mapped_column(
        Geography(geometry_type="POINT", srid=4326, spatial_index=False), nullable=False
    )
    timezone: Mapped[str] = mapped_column(String(64), default="Asia/Kolkata", nullable=False)
    opens_at: Mapped[str] = mapped_column(String(5), default="00:00", nullable=False)
    closes_at: Mapped[str] = mapped_column(String(5), default="23:59", nullable=False)
    base_rate_paise: Mapped[int] = mapped_column(nullable=False)
    state: Mapped[OperationalState] = mapped_column(
        Enum(OperationalState, name="operational_state"),
        default=OperationalState.ACTIVE,
        nullable=False,
    )
    spots: Mapped[list[ParkingSpot]] = relationship(
        back_populates="lot", cascade="all, delete-orphan"
    )


class OperatorLot(Base):
    __tablename__ = "operator_lots"
    operator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    lot_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("parking_lots.id", ondelete="CASCADE"), primary_key=True
    )


class ParkingSpot(TimestampMixin, Base):
    __tablename__ = "parking_spots"
    __table_args__ = (UniqueConstraint("lot_id", "code"),)
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    lot_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("parking_lots.id", ondelete="CASCADE"), index=True
    )
    code: Mapped[str] = mapped_column(String(24), nullable=False)
    spot_type: Mapped[SpotType] = mapped_column(Enum(SpotType, name="spot_type"), nullable=False)
    state: Mapped[OperationalState] = mapped_column(
        Enum(OperationalState, name="operational_state", create_type=False),
        default=OperationalState.ACTIVE,
        nullable=False,
    )
    lot: Mapped[ParkingLot] = relationship(back_populates="spots")
    reservations: Mapped[list[Reservation]] = relationship(back_populates="spot")


class Reservation(TimestampMixin, Base):
    __tablename__ = "reservations"
    __table_args__ = (
        CheckConstraint("ends_at > starts_at", name="ck_reservation_positive_duration"),
        CheckConstraint("quoted_amount_paise >= 0", name="ck_reservation_nonnegative_amount"),
        ExcludeConstraint(
            ("spot_id", "="),
            (func.tstzrange(text("starts_at"), text("ends_at"), "[)"), "&&"),
            where=text("status IN ('HELD', 'CONFIRMED', 'CHECKED_IN')"),
            using="gist",
            name="ex_reservation_no_overlap",
        ),
    )
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    driver_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), index=True
    )
    vehicle_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("vehicles.id", ondelete="RESTRICT"), index=True
    )
    spot_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("parking_spots.id", ondelete="RESTRICT"), index=True
    )
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    quoted_amount_paise: Mapped[int] = mapped_column(nullable=False)
    status: Mapped[ReservationStatus] = mapped_column(
        Enum(ReservationStatus, name="reservation_status"),
        default=ReservationStatus.HELD,
        nullable=False,
    )
    hold_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    qr_nonce: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid4, nullable=False)
    checked_in_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    driver: Mapped[User] = relationship(back_populates="reservations")
    vehicle: Mapped[Vehicle] = relationship()
    spot: Mapped[ParkingSpot] = relationship(back_populates="reservations")


class Payment(TimestampMixin, Base):
    __tablename__ = "payments"
    __table_args__ = (UniqueConstraint("reservation_id"),)
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    reservation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("reservations.id", ondelete="RESTRICT"), index=True
    )
    provider_order_id: Mapped[str | None] = mapped_column(String(120), unique=True)
    provider_payment_id: Mapped[str | None] = mapped_column(String(120), unique=True)
    amount_paise: Mapped[int] = mapped_column(nullable=False)
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus, name="payment_status"), default=PaymentStatus.CREATED, nullable=False
    )
    refunded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    reservation: Mapped[Reservation] = relationship()


class WebhookEvent(TimestampMixin, Base):
    __tablename__ = "webhook_events"
    __table_args__ = (UniqueConstraint("provider", "provider_event_id"),)
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    provider: Mapped[str] = mapped_column(String(40), nullable=False)
    provider_event_id: Mapped[str] = mapped_column(String(160), nullable=False)
    payload_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    outcome: Mapped[str] = mapped_column(String(80), nullable=False)


class IdempotencyRecord(TimestampMixin, Base):
    __tablename__ = "idempotency_records"
    __table_args__ = (UniqueConstraint("actor_id", "route", "key"),)
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    actor_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    route: Mapped[str] = mapped_column(String(160), nullable=False)
    key: Mapped[str] = mapped_column(String(120), nullable=False)
    request_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    response_status: Mapped[int | None]
    response_body: Mapped[dict[str, Any] | None] = mapped_column(JSONB)


class AuditEvent(Base):
    __tablename__ = "audit_events"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    actor_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    action: Mapped[str] = mapped_column(String(120), nullable=False)
    target_type: Mapped[str] = mapped_column(String(80), nullable=False)
    target_id: Mapped[uuid.UUID | None]
    request_id: Mapped[str] = mapped_column(String(36), nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
