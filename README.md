# ParkingPro

ParkingPro is a portfolio-grade parking reservation system for Bengaluru with a
React Native driver app, React operator console, and transaction-safe Flask API.
The v2 implementation is active on the codex/parkingpro-v2-foundation branch.
Deployment links will be added only after hosted smoke tests pass.

> Release status: implementation in progress. Local quality gates pass, but the
> public Render services and EAS Android build are not published yet. Render's
> free API can cold-start, and both clients surface that limitation explicitly.

## What a reviewer can evaluate

- Mapbox nearby-facility discovery in an Expo SDK 57 Android development build.
- Vehicle management, server quotes, ten-minute holds, and integer-paise pricing.
- PostgreSQL/PostGIS search and a btree_gist exclusion rule preventing overlap.
- Razorpay test orders, signatures, webhook deduplication, and test refunds.
- Signed offline QR passes with live replay and state validation.
- A responsive React console for inventory, scanning, check-in, checkout, and reports.
- Rotating mobile refresh tokens and CSRF-protected HttpOnly web refresh cookies.
- Generated OpenAPI types, tests, Docker, CI, Render, and EAS configuration.

## Architecture

    Expo React Native driver ─┐
                              ├── HTTPS / OpenAPI ── Flask modular monolith
    React operator console ───┘                         │
                                                       ├── PostgreSQL + PostGIS
                                                       ├── Upstash Redis / QStash
                                                       ├── Razorpay test mode
                                                       └── Sentry

This is intentionally a modular monolith. Kubernetes, Jenkins, microservices,
Terraform, WebSockets, real payments, iOS, and store publication are deferred;
their operational cost would not improve the early portfolio release.

## Repository

    apps/mobile                 Expo Router / React Native
    apps/operator-web           Vite / React / TypeScript
    backend/parkingpro          Flask application factory and domain modules
    backend/migrations          PostgreSQL/PostGIS Alembic history
    packages/api-contracts      OpenAPI and generated TypeScript
    packages/design-tokens      Shared visual and motion values
    infrastructure              Docker and Render definitions
    docs                        Specs, ADRs, runbooks, and mockups
    frontend                    Preserved Vue v1 application

The Vue application and its verified screenshots remain intact until React parity
and deployed evidence are complete. They are historical proof, not the v2 runtime.

## Local setup

Requirements: Node.js 22+, Python 3.11+, Docker Desktop, a public Mapbox token,
and Razorpay/Upstash test credentials for their respective workflows.

    npm ci
    python -m venv backend\.venv
    backend\.venv\Scripts\python.exe -m pip install -e "backend[dev]"
    docker compose up -d postgres redis

    $env:DATABASE_URL = "postgresql+psycopg://parkingpro:parkingpro@localhost:5432/parkingpro"
    backend\.venv\Scripts\python.exe -m flask --app parkingpro.wsgi db upgrade
    backend\.venv\Scripts\python.exe -m flask --app parkingpro.wsgi seed-demo
    backend\.venv\Scripts\python.exe -m flask --app parkingpro.wsgi run

Copy the example client environments, then run npm run web:dev and
npm run mobile:start. Mapbox and Razorpay are native modules, so the full mobile
journey requires an EAS development/internal build rather than Expo Go.

## Quality gates

    npm run lint
    npm run typecheck
    npm test
    npm run build
    backend\.venv\Scripts\python.exe -m ruff check backend\parkingpro backend\tests backend\migrations

PostgreSQL-only tests cover refresh rotation, role isolation, idempotent replay,
overlap rejection, and fifty concurrent hold attempts for one spot. They run in CI
against PostGIS and skip when no integration database is configured locally.

The current Expo/Metro build chain carries three reviewed upstream `image-size`
and `uuid` advisories for which its dependency ranges have no compatible patch as
of 2026-08-21. These build-only paths are not exposed to untrusted input; CI
allowlists only those exact advisory IDs and the exception is recorded in
[security.md](docs/security.md).

## Documentation

Start with [docs/README.md](docs/README.md). It links product, architecture, data
model, API, design, security, testing, deployment, skills, ADRs, and screen boards.
The exact provider credentials and first-release evidence gate are in the
[hosted release checklist](docs/release-checklist.md).

## Legacy ParkingPrro v1

The original Vue + Flask + SQLite showcase remains under frontend/ and the
historical backend modules. Screenshots remain in docs/screenshots/. It moves with
Git history to legacy/vue-showcase only after v2 reaches deployed feature parity.

For local historical review only, run `python legacy_app.py` from `backend/`, then
run `npm ci` and `npm run serve` from `frontend/`. The v1 runner is excluded from v2 containers and
must not be deployed because its intentionally preserved authentication model is
documented as insecure in `docs/security.md`.
