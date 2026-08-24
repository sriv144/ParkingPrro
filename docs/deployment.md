# ParkingPro deployment

**Status:** Implemented

## Environments

- Local: Docker Compose API/PostgreSQL/Redis plus local web/mobile clients.
- CI: ephemeral PostgreSQL/PostGIS and Redis services with deterministic seed data.
- Preview: Render free API/static site, Neon PostgreSQL, Upstash Redis/QStash,
  Razorpay test mode, Mapbox public token, Sentry, Expo EAS internal Android build.

## Secret ownership

Secrets live only in GitHub environments and provider secret stores. Client bundles
may contain only explicitly public Mapbox/Razorpay identifiers. Flask/JWT/QR,
database, Redis, QStash, Razorpay secret, and Sentry upload credentials are server or
CI secrets and never committed.

## Delivery sequence

1. Pull request runs all quality/security gates.
2. Main-branch workflow builds immutable web/API artifacts.
3. An additive Alembic migration runs in a protected, serialized GitHub environment.
4. GitHub calls Render deploy hooks, polls readiness for up to five minutes, and then
   verifies the public web and API surfaces.
5. Smoke tests exercise live, ready, login, lot search, and operator authorization.
6. Android internal builds are manual/tag-triggered to preserve free EAS quota.

The Render Blueprint is stored at `infrastructure/render/render.yaml`; select that
custom path when creating the Blueprint. The API defaults to port 5000 locally and
binds Render's injected `PORT` in hosted environments. The initial-deploy hook applies
migrations and creates deterministic demo data once; subsequent migrations remain a
protected GitHub-environment step before deploy hooks are called.

## Rollback

- Re-deploy the previous immutable API/web revision.
- Database changes follow expand/contract: release code never depends on destructive
  column removal in the same release. Correct data problems with forward migrations.
- Revoke affected refresh sessions/provider keys if an incident involves credentials.

## Free-tier behaviour

The API may sleep after 15 idle minutes. Clients retry health with capped exponential
backoff and show a dedicated service-starting state. The README must not claim an SLA.
