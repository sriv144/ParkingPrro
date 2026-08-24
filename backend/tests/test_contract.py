import importlib
import uuid

from parkingpro.models import Reservation
from parkingpro.services.reservations import parse_qr, sign_qr


def test_health_and_openapi_are_exposed(client):
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json["service"] == "parkingpro-api"

    spec = client.get("/openapi.json")
    assert spec.status_code == 200
    assert "/api/v1/reservations" in spec.json["paths"]
    assert "/api/v1/operator/scan" in spec.json["paths"]


def test_registration_rejects_privileged_fields(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "driver@example.com",
            "password": "correct-horse-battery",
            "full_name": "Demo Driver",
            "role": "admin",
            "is_admin": True,
        },
    )
    assert response.status_code == 422
    assert response.json["error"]["code"] == "VALIDATION_ERROR"
    assert "json.role" in response.json["error"]["fields"]
    assert "json.is_admin" in response.json["error"]["fields"]
    assert response.headers["X-Request-ID"] == response.json["error"]["request_id"]


def test_invalid_webhook_signature_is_rejected_without_side_effects(client):
    response = client.post(
        "/api/v1/webhooks/razorpay",
        data=b'{"event":"payment.captured"}',
        headers={"X-Razorpay-Signature": "invalid"},
        content_type="application/json",
    )
    assert response.status_code == 401
    assert response.json["error"]["code"] == "INVALID_WEBHOOK_SIGNATURE"


def test_unsigned_qstash_callback_is_rejected(client):
    response = client.post(
        "/api/v1/internal/jobs/expire-reservation",
        json={"reservation_id": str(uuid.uuid4())},
    )
    assert response.status_code == 401
    assert response.json["error"]["code"] == "INVALID_JOB_SIGNATURE"


def test_signed_qstash_callback_is_verified_and_retry_safe(app, monkeypatch):
    internal_api = importlib.import_module("parkingpro.api.internal")
    calls = []

    class FakeReceiver:
        def __init__(self, current_signing_key, next_signing_key):
            calls.append((current_signing_key, next_signing_key))

        def verify(self, *, body, signature, url):
            calls.append((body, signature, url))

    reservation_id = uuid.uuid4()
    app.config.update(
        QSTASH_CURRENT_SIGNING_KEY="current-test-key",
        QSTASH_NEXT_SIGNING_KEY="next-test-key",
    )
    monkeypatch.setattr(internal_api, "Receiver", FakeReceiver)
    monkeypatch.setattr(internal_api, "expire_reservation", lambda value: False)
    client = app.test_client()
    for _ in range(2):
        response = client.post(
            "/api/v1/internal/jobs/expire-reservation",
            json={"reservation_id": str(reservation_id)},
            headers={"Upstash-Signature": "signed-test-callback"},
        )
        assert response.status_code == 200
        assert response.json["message"] == "no-op"
    assert len(calls) == 4
    assert calls[0] == ("current-test-key", "next-test-key")
    assert calls[1][1] == "signed-test-callback"


def test_qr_payload_round_trip_contains_only_identifiers(app):
    reservation = Reservation(id=uuid.uuid4(), qr_nonce=uuid.uuid4())
    with app.app_context():
        payload = sign_qr(reservation)
        reservation_id, nonce = parse_qr(payload)
    assert reservation_id == reservation.id
    assert nonce == reservation.qr_nonce
    assert "@" not in payload
