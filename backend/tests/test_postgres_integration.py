import hashlib
import hmac
import json
import os
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
import razorpay
from flask_jwt_extended import create_access_token
from geoalchemy2.elements import WKTElement
from sqlalchemy import select, text

from parkingpro import create_app
from parkingpro.cli import seed_demo
from parkingpro.extensions import db
from parkingpro.models import (
    OperatorLot,
    ParkingLot,
    ParkingSpot,
    Payment,
    PaymentStatus,
    Reservation,
    ReservationStatus,
    Role,
    SpotType,
    User,
    Vehicle,
    WebhookEvent,
)
from parkingpro.services.reservations import sign_qr

DATABASE_URL = os.getenv("PARKINGPRO_TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(
    not DATABASE_URL, reason="PostgreSQL integration database is unavailable"
)


@pytest.fixture()
def postgres_app():
    app = create_app(
        "test",
        {
            "SQLALCHEMY_DATABASE_URI": DATABASE_URL,
            "RATELIMIT_ENABLED": False,
            "RAZORPAY_KEY_ID": "rzp_test_parkingpro",
            "RAZORPAY_KEY_SECRET": "integration-secret",  # noqa: S106 - test only
            "RAZORPAY_WEBHOOK_SECRET": "webhook-secret",  # noqa: S106 - test only
        },
    )
    with app.app_context():
        db.session.execute(
            text(
                "TRUNCATE audit_events, idempotency_records, webhook_events, payments, "
                "reservations, parking_spots, operator_lots, parking_lots, vehicles, "
                "device_push_tokens, "
                "refresh_sessions, users CASCADE"
            )
        )
        lot = ParkingLot(
            id=uuid.uuid4(),
            name="Concurrency Test Facility",
            address="MG Road, Bengaluru",
            location=WKTElement("POINT(77.6068 12.9756)", srid=4326),
            base_rate_paise=6000,
        )
        db.session.add(lot)
        db.session.flush()
        db.session.add(
            ParkingSpot(
                id=uuid.uuid4(),
                lot_id=lot.id,
                code="A-01",
                spot_type=SpotType.CAR,
            )
        )
        db.session.commit()
        app.config["TEST_LOT_ID"] = str(lot.id)
    return app


def register_and_login(client, suffix):
    email = f"driver-{suffix}@example.com"
    password = "correct-horse-battery"  # noqa: S105 - test-only credential
    assert (
        client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": password, "full_name": f"Driver {suffix}"},
        ).status_code
        == 201
    )
    login = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": password,
            "client_type": "mobile",
            "device_name": "pytest",
        },
    )
    assert login.status_code == 200
    return login.json


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def create_vehicle(client, session, registration):
    response = client.post(
        "/api/v1/vehicles",
        headers=auth(session["access_token"]),
        json={"registration_number": registration, "vehicle_type": "car"},
    )
    assert response.status_code == 201
    return response.json["id"]


def create_hold(client, session, lot_id, vehicle_id, start, key):
    return client.post(
        "/api/v1/reservations",
        headers={**auth(session["access_token"]), "Idempotency-Key": key},
        json={
            "lot_id": lot_id,
            "vehicle_id": vehicle_id,
            "starts_at": start.isoformat(),
            "ends_at": (start + timedelta(hours=1)).isoformat(),
            "spot_type": "car",
        },
    )


class FakeRazorpayUtility:
    def __init__(self):
        self.reject = True

    def verify_payment_signature(self, _data):
        if self.reject:
            raise razorpay.errors.SignatureVerificationError("invalid test signature")


class FakeRazorpayOrders:
    def create(self, _data):
        return {"id": "order_test_parkingpro"}


class FakeRazorpayPayments:
    def __init__(self):
        self.refunds = []

    def refund(self, payment_id, data):
        self.refunds.append((payment_id, data))
        return {"id": "refund_test_parkingpro"}


class FakeRazorpayClient:
    def __init__(self):
        self.order = FakeRazorpayOrders()
        self.utility = FakeRazorpayUtility()
        self.payment = FakeRazorpayPayments()


def test_refresh_rotation_role_isolation_and_overlap_safety(postgres_app):
    first_client = postgres_app.test_client()
    second_client = postgres_app.test_client()
    first = register_and_login(first_client, "one")
    second = register_and_login(second_client, "two")

    forbidden = first_client.get(
        "/api/v1/operator/overview",
        headers=auth(first["access_token"]),
    )
    assert forbidden.status_code == 403

    rotated = first_client.post(
        "/api/v1/auth/refresh",
        json={"client_type": "mobile", "refresh_token": first["refresh_token"]},
    )
    assert rotated.status_code == 200
    reused = first_client.post(
        "/api/v1/auth/refresh",
        json={"client_type": "mobile", "refresh_token": first["refresh_token"]},
    )
    assert reused.status_code == 401

    vehicles = []
    for client, session, registration in (
        (first_client, rotated.json, "KA01AA0001"),
        (second_client, second, "KA01AA0002"),
    ):
        response = client.post(
            "/api/v1/vehicles",
            headers=auth(session["access_token"]),
            json={"registration_number": registration, "vehicle_type": "car"},
        )
        assert response.status_code == 201
        vehicles.append(response.json["id"])

    start = (datetime.now(UTC) + timedelta(days=1)).replace(
        hour=12,
        minute=0,
        second=0,
        microsecond=0,
    )
    request_body = {
        "lot_id": postgres_app.config["TEST_LOT_ID"],
        "vehicle_id": vehicles[0],
        "starts_at": start.isoformat(),
        "ends_at": (start + timedelta(hours=1)).isoformat(),
        "spot_type": "car",
    }
    idempotency = "integration-reservation-key-0001"
    created = first_client.post(
        "/api/v1/reservations",
        headers={**auth(rotated.json["access_token"]), "Idempotency-Key": idempotency},
        json=request_body,
    )
    assert created.status_code == 201
    repeated = first_client.post(
        "/api/v1/reservations",
        headers={**auth(rotated.json["access_token"]), "Idempotency-Key": idempotency},
        json=request_body,
    )
    assert repeated.status_code == 201
    assert repeated.json["id"] == created.json["id"]

    request_body["vehicle_id"] = vehicles[1]
    conflict = second_client.post(
        "/api/v1/reservations",
        headers={
            **auth(second["access_token"]),
            "Idempotency-Key": "idem-" + "reservation-" + "0002",
        },
        json=request_body,
    )
    assert conflict.status_code == 409
    assert conflict.json["error"]["code"] == "RESERVATION_CONFLICT"

    with postgres_app.app_context():
        reservation = db.session.get(Reservation, uuid.UUID(created.json["id"]))
        assert reservation is not None
        reservation.status = ReservationStatus.CONFIRMED
        reservation.hold_expires_at = None
        operator = User(
            id=uuid.uuid4(),
            email="operator@example.com",
            full_name="Test Operator",
            password_hash="not-used",  # noqa: S106 - token is issued directly
            role=Role.OPERATOR,
        )
        db.session.add(operator)
        db.session.flush()
        db.session.add(
            OperatorLot(
                operator_id=operator.id,
                lot_id=uuid.UUID(postgres_app.config["TEST_LOT_ID"]),
            )
        )
        db.session.commit()
        qr_payload = sign_qr(reservation)
        operator_token = create_access_token(
            identity=str(operator.id),
            additional_claims={"role": "operator"},
        )
        unassigned_operator = User(
            id=uuid.uuid4(),
            email="unassigned-operator@example.com",
            full_name="Unassigned Operator",
            password_hash="not-used",  # noqa: S106 - token is issued directly
            role=Role.OPERATOR,
        )
        db.session.add(unassigned_operator)
        db.session.commit()
        unassigned_token = create_access_token(
            identity=str(unassigned_operator.id),
            additional_claims={"role": "operator"},
        )
    operator_client = postgres_app.test_client()
    invalid_qr = operator_client.post(
        "/api/v1/operator/scan",
        headers=auth(operator_token),
        json={"qr_payload": "invalid-qr-payload-that-is-long-enough"},
    )
    assert invalid_qr.status_code == 422
    not_assigned = operator_client.post(
        "/api/v1/operator/scan",
        headers=auth(unassigned_token),
        json={"qr_payload": qr_payload},
    )
    assert not_assigned.status_code == 404
    scan = operator_client.post(
        "/api/v1/operator/scan",
        headers=auth(operator_token),
        json={"qr_payload": qr_payload},
    )
    assert scan.status_code == 200
    premature_checkout = operator_client.post(
        f"/api/v1/operator/reservations/{created.json['id']}/check-out",
        headers=auth(operator_token),
    )
    assert premature_checkout.status_code == 409
    checked_in = operator_client.post(
        f"/api/v1/operator/reservations/{created.json['id']}/check-in",
        headers=auth(operator_token),
    )
    assert checked_in.status_code == 200
    cancellation_after_checkin = first_client.post(
        f"/api/v1/reservations/{created.json['id']}/cancel",
        headers={
            **auth(rotated.json["access_token"]),
            "Idempotency-Key": "checked-in-cancel-key-0001",
        },
    )
    assert cancellation_after_checkin.status_code == 409
    replay = operator_client.post(
        "/api/v1/operator/scan",
        headers=auth(operator_token),
        json={"qr_payload": qr_payload},
    )
    assert replay.status_code == 409
    assert replay.json["error"]["code"] == "QR_REPLAY_REJECTED"
    checked_out = operator_client.post(
        f"/api/v1/operator/reservations/{created.json['id']}/check-out",
        headers=auth(operator_token),
    )
    assert checked_out.status_code == 200
    assert checked_out.json["status"] == "completed"
    with postgres_app.app_context():
        reservation = db.session.get(Reservation, uuid.UUID(created.json["id"]))
        assert reservation is not None
        completed_payload = sign_qr(reservation)
    completed_scan = operator_client.post(
        "/api/v1/operator/scan",
        headers=auth(operator_token),
        json={"qr_payload": completed_payload},
    )
    assert completed_scan.status_code == 409
    assert completed_scan.json["error"]["code"] == "INVALID_RESERVATION_STATE"
    with postgres_app.app_context():
        reservation = db.session.get(Reservation, uuid.UUID(created.json["id"]))
        assert reservation is not None
        reservation.status = ReservationStatus.CANCELLED
        reservation.qr_nonce = uuid.uuid4()
        db.session.commit()
        cancelled_payload = sign_qr(reservation)
    cancelled_scan = operator_client.post(
        "/api/v1/operator/scan",
        headers=auth(operator_token),
        json={"qr_payload": cancelled_payload},
    )
    assert cancelled_scan.status_code == 409
    assert cancelled_scan.json["error"]["code"] == "INVALID_RESERVATION_STATE"


def test_operator_can_create_edit_and_manage_assigned_facility(postgres_app):
    with postgres_app.app_context():
        operator = User(
            id=uuid.uuid4(),
            email="facility-operator@example.com",
            full_name="Facility Operator",
            password_hash="not-used",  # noqa: S106 - token is issued directly
            role=Role.OPERATOR,
        )
        db.session.add(operator)
        db.session.commit()
        operator_id = operator.id
        operator_token = create_access_token(
            identity=str(operator_id),
            additional_claims={"role": "operator"},
        )

    client = postgres_app.test_client()
    ready = client.get("/health/ready")
    assert ready.status_code == 200
    assert ready.json == {"status": "ready"}
    created = client.post(
        "/api/v1/operator/lots",
        headers=auth(operator_token),
        json={
            "name": "Indiranagar Metro Parking",
            "address": "100 Feet Road, Bengaluru",
            "latitude": 12.9784,
            "longitude": 77.6408,
            "opens_at": "06:00",
            "closes_at": "23:00",
            "base_rate_paise": 7500,
            "capacity": 3,
        },
    )
    assert created.status_code == 201
    assert created.json["state"] == "active"
    assert created.json["total_spots"] == 3
    lot_id = created.json["id"]

    closed_start = (datetime.now(ZoneInfo("Asia/Kolkata")) + timedelta(days=2)).replace(
        hour=2, minute=0, second=0, microsecond=0
    )
    closed_quote = client.post(
        f"/api/v1/lots/{lot_id}/quote",
        json={
            "starts_at": closed_start.isoformat(),
            "ends_at": (closed_start + timedelta(hours=1)).isoformat(),
            "spot_type": "car",
        },
    )
    assert closed_quote.status_code == 409
    assert closed_quote.json["error"]["code"] == "FACILITY_CLOSED"

    updated = client.patch(
        f"/api/v1/operator/lots/{lot_id}",
        headers=auth(operator_token),
        json={
            "name": "Indiranagar Metro Mobility Hub",
            "opens_at": "05:30",
            "closes_at": "23:30",
            "base_rate_paise": 8000,
            "state": "out_of_service",
        },
    )
    assert updated.status_code == 200
    assert updated.json["name"] == "Indiranagar Metro Mobility Hub"
    assert updated.json["state"] == "out_of_service"
    assert updated.json["base_rate_paise"] == 8000

    spots = client.get(
        f"/api/v1/operator/lots/{lot_id}/spots",
        headers=auth(operator_token),
    )
    assert spots.status_code == 200
    assert len(spots.json) == 3
    spot_id = spots.json[0]["id"]
    disabled = client.patch(
        f"/api/v1/operator/spots/{spot_id}",
        headers=auth(operator_token),
        json={"state": "out_of_service"},
    )
    assert disabled.status_code == 200
    assert disabled.json["state"] == "out_of_service"

    with postgres_app.app_context():
        assignment = db.session.scalar(
            select(OperatorLot).where(
                OperatorLot.operator_id == operator_id,
                OperatorLot.lot_id == uuid.UUID(lot_id),
            )
        )
        assert assignment is not None


def test_demo_seed_is_idempotent_and_covers_supported_spot_types(postgres_app):
    runner = postgres_app.test_cli_runner()
    first = runner.invoke(seed_demo)
    assert first.exit_code == 0
    assert "created 5 synthetic Bengaluru facilities" in first.output
    second = runner.invoke(seed_demo)
    assert second.exit_code == 0
    assert "created 0 synthetic Bengaluru facilities" in second.output

    with postgres_app.app_context():
        demo_lots = db.session.scalars(
            select(ParkingLot).where(
                ParkingLot.name.in_(
                    [
                        "Marina Central",
                        "Indiranagar Metro Parking",
                        "Orion East Gate",
                        "UB City Parking",
                        "Manyata Tech Park",
                    ]
                )
            )
        ).all()
        assert len(demo_lots) == 5
        demo_lot_ids = [lot.id for lot in demo_lots]
        spot_types = set(
            db.session.scalars(
                select(ParkingSpot.spot_type).where(ParkingSpot.lot_id.in_(demo_lot_ids))
            )
        )
        assert spot_types == {
            SpotType.CAR,
            SpotType.BIKE,
            SpotType.EV,
            SpotType.ACCESSIBLE,
        }


def test_fifty_competing_requests_create_exactly_one_hold(postgres_app):
    identities = []
    with postgres_app.app_context():
        for index in range(50):
            user = User(
                id=uuid.uuid4(),
                email=f"parallel-{index}@example.com",
                full_name=f"Parallel Driver {index}",
                password_hash="not-used-in-this-test",  # noqa: S106 - never authenticates
                role=Role.DRIVER,
            )
            vehicle = Vehicle(
                id=uuid.uuid4(),
                owner_id=user.id,
                registration_number=f"KA01P{index:04d}",
                vehicle_type=SpotType.CAR,
            )
            db.session.add_all((user, vehicle))
            identities.append((str(user.id), str(vehicle.id)))
        db.session.commit()
        tokens = [
            create_access_token(identity=user_id, additional_claims={"role": "driver"})
            for user_id, _ in identities
        ]

    start = (datetime.now(UTC) + timedelta(days=1)).replace(
        hour=15,
        minute=0,
        second=0,
        microsecond=0,
    )

    def attempt(index):
        client = postgres_app.test_client()
        return client.post(
            "/api/v1/reservations",
            headers={
                **auth(tokens[index]),
                "Idempotency-Key": f"parallel-reservation-key-{index:04d}",
            },
            json={
                "lot_id": postgres_app.config["TEST_LOT_ID"],
                "vehicle_id": identities[index][1],
                "starts_at": start.isoformat(),
                "ends_at": (start + timedelta(hours=1)).isoformat(),
                "spot_type": "car",
            },
        ).status_code

    with ThreadPoolExecutor(max_workers=20) as executor:
        statuses = list(executor.map(attempt, range(50)))
    assert statuses.count(201) == 1
    assert statuses.count(409) == 49


def test_ownership_search_filters_stale_hold_recovery_and_key_reuse(postgres_app):
    first_client = postgres_app.test_client()
    second_client = postgres_app.test_client()
    first = register_and_login(first_client, "ownership-one")
    second = register_and_login(second_client, "ownership-two")
    first_vehicle = create_vehicle(first_client, first, "KA01ST0001")
    second_vehicle = create_vehicle(second_client, second, "KA01ST0002")
    start = (datetime.now(UTC) + timedelta(days=2)).replace(
        hour=10, minute=0, second=0, microsecond=0
    )

    held = create_hold(
        first_client,
        first,
        postgres_app.config["TEST_LOT_ID"],
        first_vehicle,
        start,
        "stale-hold-owner-key-0001",
    )
    assert held.status_code == 201
    hidden = second_client.get(
        f"/api/v1/reservations/{held.json['id']}",
        headers=auth(second["access_token"]),
    )
    assert hidden.status_code == 404

    search_query = {
        "latitude": 12.9756,
        "longitude": 77.6068,
        "radius_m": 1000,
        "starts_at": start.isoformat(),
        "ends_at": (start + timedelta(hours=1)).isoformat(),
        "spot_type": "car",
    }
    unavailable = first_client.get("/api/v1/lots", query_string=search_query)
    assert unavailable.status_code == 200
    assert unavailable.json == []

    wrong_spot_type = first_client.get(
        "/api/v1/lots", query_string={**search_query, "spot_type": "bike"}
    )
    assert wrong_spot_type.status_code == 200
    assert wrong_spot_type.json == []
    outside_radius = first_client.get(
        "/api/v1/lots",
        query_string={**search_query, "latitude": 13.5, "longitude": 78.5},
    )
    assert outside_radius.status_code == 200
    assert outside_radius.json == []

    with postgres_app.app_context():
        stale = db.session.get(Reservation, uuid.UUID(held.json["id"]))
        assert stale is not None
        stale.hold_expires_at = datetime.now(UTC) - timedelta(seconds=1)
        db.session.commit()

    available = first_client.get("/api/v1/lots", query_string=search_query)
    assert available.status_code == 200
    assert available.json[0]["available_spots"] == 1
    recovered = create_hold(
        second_client,
        second,
        postgres_app.config["TEST_LOT_ID"],
        second_vehicle,
        start,
        "stale-hold-recovery-key-0002",
    )
    assert recovered.status_code == 201
    with postgres_app.app_context():
        stale = db.session.get(Reservation, uuid.UUID(held.json["id"]))
        assert stale is not None
        assert stale.status is ReservationStatus.EXPIRED

    changed_payload = {
        "lot_id": postgres_app.config["TEST_LOT_ID"],
        "vehicle_id": second_vehicle,
        "starts_at": (start + timedelta(hours=2)).isoformat(),
        "ends_at": (start + timedelta(hours=3)).isoformat(),
        "spot_type": "car",
    }
    key_reuse = second_client.post(
        "/api/v1/reservations",
        headers={
            **auth(second["access_token"]),
            "Idempotency-Key": "stale-hold-recovery-key-0002",
        },
        json=changed_payload,
    )
    assert key_reuse.status_code == 409
    assert key_reuse.json["error"]["code"] == "IDEMPOTENCY_KEY_REUSED"


def test_payment_signature_idempotency_cancellation_and_refund(postgres_app, monkeypatch):
    client = postgres_app.test_client()
    session = register_and_login(client, "payment")
    vehicle_id = create_vehicle(client, session, "KA01PY0001")
    start = (datetime.now(UTC) + timedelta(days=3)).replace(
        hour=11, minute=0, second=0, microsecond=0
    )
    held = create_hold(
        client,
        session,
        postgres_app.config["TEST_LOT_ID"],
        vehicle_id,
        start,
        "payment-hold-key-0001",
    )
    assert held.status_code == 201

    fake_client = FakeRazorpayClient()
    monkeypatch.setattr("parkingpro.services.payments._client", lambda: fake_client)
    order = client.post(
        f"/api/v1/payments/{held.json['id']}/order",
        headers={
            **auth(session["access_token"]),
            "Idempotency-Key": "payment-order-key-0001",
        },
    )
    assert order.status_code == 200
    assert order.json["order_id"] == "order_test_parkingpro"
    verify_body = {
        "razorpay_order_id": order.json["order_id"],
        "razorpay_payment_id": "pay_test_parkingpro",
        "razorpay_signature": "invalid",
    }
    invalid = client.post(
        f"/api/v1/payments/{held.json['id']}/verify",
        headers={
            **auth(session["access_token"]),
            "Idempotency-Key": "payment-verify-invalid-key-0001",
        },
        json=verify_body,
    )
    assert invalid.status_code == 422
    assert invalid.json["error"]["code"] == "INVALID_PAYMENT_SIGNATURE"
    with postgres_app.app_context():
        payment = db.session.scalar(
            select(Payment).where(Payment.reservation_id == uuid.UUID(held.json["id"]))
        )
        reservation = db.session.get(Reservation, uuid.UUID(held.json["id"]))
        assert payment is not None and payment.status is PaymentStatus.CREATED
        assert reservation is not None and reservation.status is ReservationStatus.HELD

    fake_client.utility.reject = False
    verified = client.post(
        f"/api/v1/payments/{held.json['id']}/verify",
        headers={
            **auth(session["access_token"]),
            "Idempotency-Key": "payment-verify-valid-key-0002",
        },
        json=verify_body,
    )
    assert verified.status_code == 200
    assert verified.json["status"] == "confirmed"
    repeated = client.post(
        f"/api/v1/payments/{held.json['id']}/verify",
        headers={
            **auth(session["access_token"]),
            "Idempotency-Key": "payment-verify-valid-key-0002",
        },
        json=verify_body,
    )
    assert repeated.status_code == 200
    assert repeated.json["status"] == "confirmed"
    changed_verify = client.post(
        f"/api/v1/payments/{held.json['id']}/verify",
        headers={
            **auth(session["access_token"]),
            "Idempotency-Key": "payment-verify-valid-key-0002",
        },
        json={**verify_body, "razorpay_payment_id": "pay_changed"},
    )
    assert changed_verify.status_code == 409
    assert changed_verify.json["error"]["code"] == "IDEMPOTENCY_KEY_REUSED"

    cancelled = client.post(
        f"/api/v1/reservations/{held.json['id']}/cancel",
        headers={
            **auth(session["access_token"]),
            "Idempotency-Key": "payment-cancel-key-0001",
        },
    )
    assert cancelled.status_code == 200
    assert cancelled.json["status"] == "cancelled"
    repeated_cancel = client.post(
        f"/api/v1/reservations/{held.json['id']}/cancel",
        headers={
            **auth(session["access_token"]),
            "Idempotency-Key": "payment-cancel-key-0001",
        },
    )
    assert repeated_cancel.status_code == 200
    assert len(fake_client.payment.refunds) == 1
    with postgres_app.app_context():
        payment = db.session.scalar(
            select(Payment).where(Payment.reservation_id == uuid.UUID(held.json["id"]))
        )
        assert payment is not None and payment.status is PaymentStatus.REFUNDED


def test_razorpay_webhook_is_signed_and_deduplicated(postgres_app, monkeypatch):
    client = postgres_app.test_client()
    session = register_and_login(client, "webhook")
    vehicle_id = create_vehicle(client, session, "KA01WH0001")
    start = (datetime.now(UTC) + timedelta(days=4)).replace(
        hour=12, minute=0, second=0, microsecond=0
    )
    held = create_hold(
        client,
        session,
        postgres_app.config["TEST_LOT_ID"],
        vehicle_id,
        start,
        "webhook-hold-key-0001",
    )
    assert held.status_code == 201
    fake_client = FakeRazorpayClient()
    monkeypatch.setattr("parkingpro.services.payments._client", lambda: fake_client)
    order = client.post(
        f"/api/v1/payments/{held.json['id']}/order",
        headers={
            **auth(session["access_token"]),
            "Idempotency-Key": "webhook-order-key-0001",
        },
    )
    assert order.status_code == 200

    payload = {
        "event": "payment.captured",
        "payload": {
            "payment": {
                "entity": {
                    "id": "pay_webhook_parkingpro",
                    "order_id": order.json["order_id"],
                }
            }
        },
    }
    raw_body = json.dumps(payload, separators=(",", ":")).encode()
    signature = hmac.new(b"webhook-secret", raw_body, hashlib.sha256).hexdigest()
    headers = {
        "Content-Type": "application/json",
        "X-Razorpay-Signature": signature,
        "X-Razorpay-Event-Id": "event_test_parkingpro",
    }
    first = client.post("/api/v1/webhooks/razorpay", headers=headers, data=raw_body)
    duplicate = client.post("/api/v1/webhooks/razorpay", headers=headers, data=raw_body)
    assert first.status_code == 200 and first.json["message"] == "processed"
    assert duplicate.status_code == 200 and duplicate.json["message"] == "duplicate"
    with postgres_app.app_context():
        events = db.session.scalars(select(WebhookEvent)).all()
        payment = db.session.scalar(
            select(Payment).where(Payment.reservation_id == uuid.UUID(held.json["id"]))
        )
        reservation = db.session.get(Reservation, uuid.UUID(held.json["id"]))
        assert len(events) == 1
        assert payment is not None and payment.status is PaymentStatus.CAPTURED
        assert reservation is not None and reservation.status is ReservationStatus.CONFIRMED
