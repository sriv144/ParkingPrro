# ParkingPro security baseline

**Status:** Implemented

## Trust boundaries

- Browser/mobile input and all API responses are untrusted at rendering boundaries.
- Access tokens prove identity, never permission; authorization is checked per route
  and resource on the server.
- Razorpay and QStash requests are untrusted until raw-body signatures verify.
- Redis is a cache/rate-limit dependency, never the system of record.
- PostgreSQL constraints remain authoritative under concurrency.

## Required controls

- Public registration accepts only driver fields and rejects role/admin properties.
- Operator/admin creation is a protected CLI operation with no default credentials.
- Production refuses placeholder Flask/JWT/QR secrets and permissive CORS.
- Passwords use Werkzeug's current adaptive password hashing.
- Access tokens are short lived; rotating refresh tokens are hashed and revocable.
- Browser access tokens remain in memory; no auth token is stored in Web Storage.
- Mobile refresh tokens use SecureStore and are removed on logout/revocation.
- All mutation schemas reject unknown fields; ownership/role checks run server-side.
- Auth endpoints and expensive searches have Redis-backed rate limits.
- Request bodies are limited; logs redact authorization, tokens, email, phone, and QR.
- Security headers are set in Flask/Render static-site configuration.
- Razorpay/QStash events are signed, deduplicated, bounded, and never logged raw.
- Dependency, secret, SAST, and container scans run in CI; reachable critical/high
  findings block, except a time-bounded documented upstream exception below.

## Temporary upstream dependency exception

As of 2026-08-24, Expo SDK 57's `xcode` build helper constrains `uuid` to v7 despite
GHSA-w5hq-g745-h8pq being fixed in 11.1.1. npm workspace overrides do not replace
that incompatible transitive range. ParkingPro does not invoke UUID v3/v5/v6 with
caller-supplied buffers; this package executes only while developers or EAS bundle
trusted repository assets. CI allowlists exactly this advisory ID and its known Expo
dependency paths, including npm's propagated
`@maplibre/maplibre-react-native → expo` effect, while failing on any new advisory or
unreviewed package. It does not apply npm's suggested breaking downgrade to Expo 53.

Remove this exception as soon as Expo/Metro publishes a compatible patched
dependency. It does not waive critical/high findings in the Flask API, shipped
browser bundle, container runtime, or dependencies with reachable untrusted input.

## Known v1 issue being retired

The legacy `/register` route accepts `is_admin`, then issues an admin role claim. V2
must not reuse this shape. The first backend security test asserts that `role` and
`is_admin` are rejected and no privileged account is created.
