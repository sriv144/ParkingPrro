# ParkingPro API contract

**Status:** Implemented

Base path: `/api/v1`. JSON keys use `snake_case`; timestamps are RFC 3339 UTC;
money fields end in `_paise`. Collection endpoints use cursor pagination.

## Errors

```json
{
  "error": {
    "code": "RESERVATION_CONFLICT",
    "message": "This spot is no longer available.",
    "request_id": "4db0bb75-1f1a-4478-b5cb-bef4403d0b81",
    "fields": {}
  }
}
```

Stable codes include `VALIDATION_ERROR`, `AUTHENTICATION_REQUIRED`,
`PERMISSION_DENIED`, `RESOURCE_NOT_FOUND`, `RATE_LIMITED`,
`IDEMPOTENCY_CONFLICT`, `RESERVATION_CONFLICT`, `INVALID_STATE_TRANSITION`,
`INVALID_PROVIDER_SIGNATURE`, and `SERVICE_UNAVAILABLE`.

## Authentication

```text
POST /auth/register      POST /auth/login       POST /auth/refresh
POST /auth/logout        GET  /auth/me
```

Access tokens live for 15 minutes. Refresh tokens rotate on every use, are stored
hashed server-side, and expire after 30 days. Browser access tokens remain in
memory; mobile refresh tokens use platform secure storage.

## Driver resources

```text
GET    /lots                    GET    /lots/{lot_id}
POST   /lots/{lot_id}/quote
GET    /vehicles                POST   /vehicles
PATCH  /vehicles/{vehicle_id}   DELETE /vehicles/{vehicle_id}
POST   /reservations            GET    /reservations
GET    /reservations/{id}       POST   /reservations/{id}/cancel
POST   /payments/{reservation_id}/order
```

`GET /lots` accepts `latitude`, `longitude`, `radius_m`, `starts_at`, `ends_at`,
`vehicle_type`, `spot_type`, and `cursor`. Default radius is 10 km; maximum result
count is 50.

Quote responses include a server-generated `quote_id`, availability, duration,
rate breakdown, tax-inclusive total, and a five-minute quote expiry.

Reservation and payment creation require `Idempotency-Key`. Reuse with the same
request returns the saved response; reuse with a different body returns 409.

## Operator resources

```text
GET    /operator/overview
GET    /operator/lots           POST  /operator/lots
PATCH  /operator/lots/{lot_id}
GET    /operator/reservations
POST   /operator/scan
POST   /operator/reservations/{id}/check-in
POST   /operator/reservations/{id}/check-out
```

Every query is scoped through `operator_lots`; client-side route protection is UX
only. Checkout returns the final duration, amount, and resulting occupancy.

## Providers and operations

```text
POST /webhooks/razorpay
POST /internal/jobs/expire-reservation
POST /internal/jobs/send-reminder
GET  /health/live
GET  /health/ready
GET  /openapi.json
```

Provider endpoints verify signatures over the raw request body before JSON is
trusted. Readiness checks database connectivity without exposing credentials.
