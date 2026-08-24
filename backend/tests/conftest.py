import pytest

from parkingpro import create_app


@pytest.fixture()
def app():
    return create_app(
        "test",
        {
            "SQLALCHEMY_DATABASE_URI": "postgresql+psycopg://unused:unused@localhost/unused",
            "RAZORPAY_WEBHOOK_SECRET": "test-webhook-secret",
        },
    )


@pytest.fixture()
def client(app):
    return app.test_client()
