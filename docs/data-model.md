# ParkingPro data model

**Status:** Implemented

All public identifiers are UUIDs. Times are stored in UTC and interpreted in the
facility timezone (`Asia/Kolkata` for demo data). Money is stored as integer paise.

## Entities

- `users`: email, password hash, role (`driver`, `operator`, `admin`), state, profile.
- `refresh_sessions`: hashed rotating token, user, device, expiry, revocation.
- `vehicles`: owner, normalized registration, label, type.
- `parking_lots`: name, address, PostGIS point, timezone, hours, base rate, state.
- `operator_lots`: operator-to-lot authorization assignment.
- `parking_spots`: lot, human code, type, operational state.
- `reservations`: driver, vehicle, spot, interval, quote, state, hold expiry, QR nonce.
- `payments`: reservation, provider identifiers, amount, state, timestamps.
- `webhook_events`: provider/event identity, payload hash, processing result.
- `idempotency_records`: actor, route, key, request hash, status, saved response.
- `audit_events`: actor, action, target, request ID, redacted metadata.

## State machines

```text
HELD ──payment captured──> CONFIRMED ──scan──> CHECKED_IN ──checkout──> COMPLETED
  ├──hold timeout────────> EXPIRED
  └──driver cancels──────> CANCELLED
CONFIRMED ──before start─> CANCELLED
```

```text
CREATED ──provider success──> AUTHORIZED ──capture──> CAPTURED ──refund──> REFUNDED
   └───────────────────────────────────────────────> FAILED
```

## Invariants

- Reservation intervals are half-open: `[starts_at, ends_at)`.
- Start/end use 30-minute boundaries; duration is 30 minutes through 24 hours.
- `HELD`, `CONFIRMED`, and `CHECKED_IN` intervals may not overlap for one spot.
- A PostgreSQL GiST exclusion constraint is the final double-booking defence.
- A hold expires ten minutes after creation unless payment confirms it.
- A checked-in/started reservation cannot be cancelled.
- One provider event ID and one payment ID can affect state at most once.
- QR data contains only reservation ID, nonce, issue/expiry time, and signature.
- Spot operational state is independent of reservation-derived occupancy.
