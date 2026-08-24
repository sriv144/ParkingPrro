"""Initial ParkingPro PostgreSQL and PostGIS schema."""

from alembic import op

revision = "20260821_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist")
    op.execute("CREATE TYPE user_role AS ENUM ('DRIVER', 'OPERATOR', 'ADMIN')")
    op.execute("CREATE TYPE account_state AS ENUM ('ACTIVE', 'DISABLED')")
    op.execute("CREATE TYPE spot_type AS ENUM ('CAR', 'BIKE', 'EV', 'ACCESSIBLE')")
    op.execute("CREATE TYPE operational_state AS ENUM ('ACTIVE', 'OUT_OF_SERVICE')")
    op.execute(
        "CREATE TYPE reservation_status AS ENUM "
        "('HELD', 'CONFIRMED', 'CHECKED_IN', 'COMPLETED', 'CANCELLED', 'EXPIRED')"
    )
    op.execute(
        "CREATE TYPE payment_status AS ENUM "
        "('CREATED', 'AUTHORIZED', 'CAPTURED', 'FAILED', 'REFUNDED')"
    )
    op.execute(
        """
        CREATE TABLE users (
          id UUID PRIMARY KEY,
          email VARCHAR(320) NOT NULL UNIQUE,
          password_hash VARCHAR(512) NOT NULL,
          full_name VARCHAR(120) NOT NULL,
          phone VARCHAR(24),
          role user_role NOT NULL,
          state account_state NOT NULL,
          created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
          updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )
    op.execute(
        """
        CREATE TABLE refresh_sessions (
          id UUID PRIMARY KEY,
          user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
          token_hash VARCHAR(64) NOT NULL UNIQUE,
          csrf_hash VARCHAR(64),
          device_name VARCHAR(120) NOT NULL,
          expires_at TIMESTAMPTZ NOT NULL,
          revoked_at TIMESTAMPTZ,
          created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
          updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )
    op.execute("CREATE INDEX ix_refresh_sessions_user_id ON refresh_sessions(user_id)")
    op.execute(
        """
        CREATE TABLE vehicles (
          id UUID PRIMARY KEY,
          owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
          registration_number VARCHAR(20) NOT NULL,
          label VARCHAR(60),
          vehicle_type spot_type NOT NULL,
          created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
          updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
          UNIQUE(owner_id, registration_number)
        )
        """
    )
    op.execute("CREATE INDEX ix_vehicles_owner_id ON vehicles(owner_id)")
    op.execute(
        """
        CREATE TABLE parking_lots (
          id UUID PRIMARY KEY,
          name VARCHAR(160) NOT NULL,
          address VARCHAR(320) NOT NULL,
          location geography(POINT, 4326) NOT NULL,
          timezone VARCHAR(64) NOT NULL DEFAULT 'Asia/Kolkata',
          opens_at VARCHAR(5) NOT NULL DEFAULT '00:00',
          closes_at VARCHAR(5) NOT NULL DEFAULT '23:59',
          base_rate_paise INTEGER NOT NULL,
          state operational_state NOT NULL,
          created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
          updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
          CONSTRAINT ck_lot_positive_rate CHECK (base_rate_paise > 0)
        )
        """
    )
    op.execute("CREATE INDEX ix_parking_lots_location ON parking_lots USING gist(location)")
    op.execute(
        """
        CREATE TABLE operator_lots (
          operator_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
          lot_id UUID NOT NULL REFERENCES parking_lots(id) ON DELETE CASCADE,
          PRIMARY KEY(operator_id, lot_id)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE parking_spots (
          id UUID PRIMARY KEY,
          lot_id UUID NOT NULL REFERENCES parking_lots(id) ON DELETE CASCADE,
          code VARCHAR(24) NOT NULL,
          spot_type spot_type NOT NULL,
          state operational_state NOT NULL,
          created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
          updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
          UNIQUE(lot_id, code)
        )
        """
    )
    op.execute("CREATE INDEX ix_parking_spots_lot_id ON parking_spots(lot_id)")
    op.execute(
        """
        CREATE TABLE reservations (
          id UUID PRIMARY KEY,
          driver_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
          vehicle_id UUID NOT NULL REFERENCES vehicles(id) ON DELETE RESTRICT,
          spot_id UUID NOT NULL REFERENCES parking_spots(id) ON DELETE RESTRICT,
          starts_at TIMESTAMPTZ NOT NULL,
          ends_at TIMESTAMPTZ NOT NULL,
          quoted_amount_paise INTEGER NOT NULL,
          status reservation_status NOT NULL,
          hold_expires_at TIMESTAMPTZ,
          qr_nonce UUID NOT NULL,
          checked_in_at TIMESTAMPTZ,
          completed_at TIMESTAMPTZ,
          cancelled_at TIMESTAMPTZ,
          created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
          updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
          CONSTRAINT ck_reservation_positive_duration CHECK (ends_at > starts_at),
          CONSTRAINT ck_reservation_nonnegative_amount CHECK (quoted_amount_paise >= 0),
          CONSTRAINT ex_reservation_no_overlap EXCLUDE USING gist (
            spot_id WITH =,
            tstzrange(starts_at, ends_at, '[)') WITH &&
          ) WHERE (status IN ('HELD', 'CONFIRMED', 'CHECKED_IN'))
        )
        """
    )
    op.execute("CREATE INDEX ix_reservations_driver_id ON reservations(driver_id)")
    op.execute("CREATE INDEX ix_reservations_vehicle_id ON reservations(vehicle_id)")
    op.execute("CREATE INDEX ix_reservations_spot_id ON reservations(spot_id)")
    op.execute(
        """
        CREATE TABLE payments (
          id UUID PRIMARY KEY,
          reservation_id UUID NOT NULL UNIQUE REFERENCES reservations(id) ON DELETE RESTRICT,
          provider_order_id VARCHAR(120) UNIQUE,
          provider_payment_id VARCHAR(120) UNIQUE,
          amount_paise INTEGER NOT NULL,
          status payment_status NOT NULL,
          refunded_at TIMESTAMPTZ,
          created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
          updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )
    op.execute("CREATE INDEX ix_payments_reservation_id ON payments(reservation_id)")
    op.execute(
        """
        CREATE TABLE webhook_events (
          id UUID PRIMARY KEY,
          provider VARCHAR(40) NOT NULL,
          provider_event_id VARCHAR(160) NOT NULL,
          payload_hash VARCHAR(64) NOT NULL,
          outcome VARCHAR(80) NOT NULL,
          created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
          updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
          UNIQUE(provider, provider_event_id)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE idempotency_records (
          id UUID PRIMARY KEY,
          actor_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
          route VARCHAR(160) NOT NULL,
          key VARCHAR(120) NOT NULL,
          request_hash VARCHAR(64) NOT NULL,
          response_status INTEGER,
          response_body JSONB,
          created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
          updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
          UNIQUE(actor_id, route, key)
        )
        """
    )
    op.execute("CREATE INDEX ix_idempotency_records_actor_id ON idempotency_records(actor_id)")
    op.execute(
        """
        CREATE TABLE audit_events (
          id UUID PRIMARY KEY,
          actor_id UUID REFERENCES users(id) ON DELETE SET NULL,
          action VARCHAR(120) NOT NULL,
          target_type VARCHAR(80) NOT NULL,
          target_id UUID,
          request_id VARCHAR(36) NOT NULL,
          metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
          created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )
    op.execute("CREATE INDEX ix_audit_events_actor_id ON audit_events(actor_id)")


def downgrade() -> None:
    for table in (
        "audit_events",
        "idempotency_records",
        "webhook_events",
        "payments",
        "reservations",
        "parking_spots",
        "operator_lots",
        "parking_lots",
        "vehicles",
        "refresh_sessions",
        "users",
    ):
        op.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
    for enum_name in (
        "payment_status",
        "reservation_status",
        "operational_state",
        "spot_type",
        "account_state",
        "user_role",
    ):
        op.execute(f"DROP TYPE IF EXISTS {enum_name}")
