from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from zoneinfo import ZoneInfo

import pytest

from parkingpro.config import ProductionConfig
from parkingpro.errors import ApiProblem, _normalize_fields
from parkingpro.services.catalog import lot_accepts_window, quote_amount, validate_booking_window


def test_booking_window_accepts_half_hour_boundaries():
    start = (datetime.now(UTC) + timedelta(days=1)).replace(minute=0, second=0, microsecond=0)
    assert validate_booking_window(start, start + timedelta(minutes=30)) == 30
    assert validate_booking_window(start, start + timedelta(hours=24)) == 1440


def test_booking_window_rejects_invalid_granularity():
    start = (datetime.now(UTC) + timedelta(days=1)).replace(minute=15, second=0, microsecond=0)
    with pytest.raises(ApiProblem, match="30-minute"):
        validate_booking_window(start, start + timedelta(minutes=30))


def test_quote_uses_integer_paise():
    assert quote_amount(6000, 30) == 3000
    assert quote_amount(5001, 30) == 2501


def test_facility_hours_support_all_day_and_overnight_intervals():
    zone = ZoneInfo("Asia/Kolkata")
    overnight = SimpleNamespace(
        opens_at="18:00",
        closes_at="06:00",
        timezone="Asia/Kolkata",
    )
    start = datetime(2026, 8, 25, 23, 0, tzinfo=zone)
    assert lot_accepts_window(overnight, start, start + timedelta(hours=4))
    assert not lot_accepts_window(overnight, start, start + timedelta(hours=8))

    all_day = SimpleNamespace(
        opens_at="00:00",
        closes_at="23:59",
        timezone="Asia/Kolkata",
    )
    assert lot_accepts_window(all_day, start, start + timedelta(hours=24))


def test_validation_fields_are_flattened_for_client_forms():
    assert _normalize_fields({"json": {"email": ["Not a valid email."]}}) == {
        "json.email": ["Not a valid email."]
    }
    assert _normalize_fields("Invalid request.") == {"_schema": ["Invalid request."]}


def test_production_configuration_fails_closed():
    config = {  # noqa: S105 - deliberately incomplete test configuration
        "APP_ENV": "production",
        "SECRET_KEY": "",
        "JWT_SECRET_KEY": "",
        "QR_SIGNING_KEY": "",
        "SQLALCHEMY_DATABASE_URI": "",
        "REDIS_URL": "",
        "RAZORPAY_KEY_ID": "",
        "RAZORPAY_KEY_SECRET": "",
        "RAZORPAY_WEBHOOK_SECRET": "",
        "QSTASH_TOKEN": "",
        "QSTASH_CURRENT_SIGNING_KEY": "",
        "QSTASH_NEXT_SIGNING_KEY": "",
        "PUBLIC_API_URL": "",
        "CORS_ORIGINS": [],
        "TRUSTED_HOSTS": [],
    }
    with pytest.raises(RuntimeError, match="Missing required production configuration"):
        ProductionConfig.validate(config)

    configured = {key: "configured" for key in config}
    configured.update(APP_ENV="production", CORS_ORIGINS=["*"], TRUSTED_HOSTS=["api.example"])
    with pytest.raises(RuntimeError, match="explicit allowlist"):
        ProductionConfig.validate(configured)

    configured.update(
        CORS_ORIGINS=["https://operator.example"],
        SQLALCHEMY_DATABASE_URI="postgresql+psycopg://user@localhost/parkingpro",
        REDIS_URL="rediss://redis.example",
        PUBLIC_API_URL="https://api.example",
    )
    with pytest.raises(RuntimeError, match="cannot point to localhost"):
        ProductionConfig.validate(configured)
