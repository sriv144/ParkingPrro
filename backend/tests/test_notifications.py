import uuid
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

from parkingpro.services import notifications


class FakeMessageClient:
    def __init__(self, published):
        self.published = published

    def publish_json(self, **kwargs):
        self.published.append(kwargs)


class FakeQStash:
    published = []

    def __init__(self, token):  # noqa: S105 - deterministic test-only value
        assert token == "qstash-test-token"  # noqa: S105 - deterministic test-only value
        self.message = FakeMessageClient(self.published)


def test_reminder_scheduling_is_optional_and_uses_signed_job_provider(app, monkeypatch):
    reservation = SimpleNamespace(
        id=uuid.uuid4(),
        starts_at=datetime.now(UTC) + timedelta(hours=2),
    )
    with app.app_context():
        notifications.schedule_reminder(reservation)

        app.config.update(
            QSTASH_TOKEN="qstash-test-token",  # noqa: S106 - test-only value
            PUBLIC_API_URL="https://api.parkingpro.example",
        )
        FakeQStash.published.clear()
        monkeypatch.setattr(notifications, "QStash", FakeQStash)
        notifications.schedule_reminder(reservation)

    assert len(FakeQStash.published) == 1
    job = FakeQStash.published[0]
    assert job["url"].endswith("/api/v1/internal/jobs/send-reminder")
    assert job["body"] == {"reservation_id": str(reservation.id)}
    assert job["retries"] == 3


def test_reminder_is_not_scheduled_inside_thirty_minute_window(app, monkeypatch):
    reservation = SimpleNamespace(
        id=uuid.uuid4(),
        starts_at=datetime.now(UTC) + timedelta(minutes=20),
    )
    with app.app_context():
        app.config.update(
            QSTASH_TOKEN="qstash-test-token",  # noqa: S106 - test-only value
            PUBLIC_API_URL="https://api.parkingpro.example",
        )
        FakeQStash.published.clear()
        monkeypatch.setattr(notifications, "QStash", FakeQStash)
        notifications.schedule_reminder(reservation)
    assert FakeQStash.published == []
