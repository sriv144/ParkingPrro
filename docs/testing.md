# ParkingPro testing strategy

**Status:** Implemented

## Layers

- Domain unit tests: pricing, time normalization, state machines, QR signing.
- Flask integration tests: auth, authorization, validation, idempotency, providers.
- PostgreSQL tests: migrations, PostGIS search, exclusion constraint, concurrency.
- Contract tests: OpenAPI generation and TypeScript-client drift.
- React tests: Vitest and Testing Library for forms, states, and permissions UX.
- Web E2E: Playwright using role/label locators and isolated seeded data.
- Android E2E: Maestro against an EAS development/internal build.
- Delivery tests: Docker health, non-root process, migration, deploy smoke test.

## Mandatory scenarios

- Privileged fields in registration are rejected.
- A driver cannot access another driver's reservation or any operator route.
- Refresh rotation invalidates the previous token.
- Fifty concurrent attempts for one spot/interval create exactly one hold.
- Same idempotency key/body returns the original response; changed body returns 409.
- Invalid/duplicate Razorpay and QStash deliveries cannot duplicate state changes.
- Hold expiration releases availability.
- Invalid, cancelled, completed, or replayed QR passes cannot mutate state.
- Cancellation/refund rules and invalid transitions are enforced.
- Active pass remains readable offline; mutations explain that a network is required.
- Free-tier cold start, empty, validation, provider failure, and retry states render.

## CI gates

Lint, format check, type check, tests, OpenAPI drift, production builds, dependency
audit, secret scan, SAST, container scan, and smoke tests must pass before deployment.

## Local verification record — 2026-08-24

- Alembic revisions `20260821_0001` and `20260821_0002` applied to a real
  PostgreSQL 17/PostGIS 3.5 container.
- All 21 Flask tests passed with 81% branch-aware coverage. The seven
  PostgreSQL integration tests include 50 concurrent contenders, eligible-only
  search and ownership filters, stale-hold recovery, facility CRUD, deterministic
  all-spot-type seeding, payment verification and refund, webhook deduplication,
  and invalid/replayed/cancelled/completed QR states.
- Ruff and strict mypy passed.
- Vitest passed, and Playwright completed inventory mutation, manual QR scan,
  check-in, checkout, and reporting in one operator lifecycle test.
- Prettier, ESLint, all TypeScript workspace checks, the Vite production build,
  Expo Doctor (21/21), Android Hermes export, npm advisory allowlist, Compose
  validation, and deterministic OpenAPI generation passed.
- The Maestro smoke flow covers service wake-up, demo login, map selection,
  facility choices, quote, and reservation hold through the Razorpay boundary.
  The release checklist still requires the vendor-owned Razorpay test sheet and
  resulting offline QR to be exercised on the signed EAS APK.
- The final API and operator images built successfully after pinning Setuptools to
  Razorpay's supported `<81` range. Alembic ran from the API image, Gunicorn
  returned 200 from live, ready, and OpenAPI endpoints, and the operator image
  served both its health route and SPA fallback with the expected CSP.
- The final API image also passed readiness while binding an injected `PORT=10000`
  (mapped to local port 5100), matching Render's runtime contract; the checked-in
  Blueprint passed Render's current official JSON Schema.
- Runtime inspection verified the API as UID 999 (`parkingpro`) and Nginx as UID
  101 (`nginx`), with zero restarts and healthy probes. CI repeats these builds on
  a clean runner and must still be green before a hosted release.
- A fresh disposable PostGIS database upgraded through both revisions and
  cleanly downgraded to base, upgraded again, and passed `flask db check` with no
  schema drift after extension-owned objects were excluded from Alembic ownership.
