# ParkingPro 8/10 completion audit

**Status:** Implemented

**Audit date:** 2026-08-24

This matrix compares the approved early-release plan with current repository and
runtime evidence. `Verified locally` means the relevant implementation ran against
the local production-shaped stack. `Hosted pending` means code and automation exist,
but the claim requires provider credentials, a remote CI run, an EAS build, or a
public URL before it can become release evidence.

## Architecture and deliverables

| Requirement                          | Evidence                                                                                                                | Status                                    |
| ------------------------------------ | ----------------------------------------------------------------------------------------------------------------------- | ----------------------------------------- |
| Expo React Native Android driver     | `apps/mobile`, Expo Router routes, SDK 57 dependency checks and Android Hermes export                                   | Verified locally                          |
| React operator console               | `apps/operator-web`, production Vite build and Playwright operator lifecycle                                            | Verified locally                          |
| Flask modular monolith               | `backend/parkingpro`, application factory, schemas, services and Gunicorn image                                         | Verified locally                          |
| PostgreSQL/PostGIS booking authority | Alembic revisions, PostGIS search, `btree_gist` exclusion constraint and fresh-schema drift check                       | Verified locally                          |
| Redis and serverless jobs            | Redis readiness/rate limiting, QStash scheduling and signed callback tests                                              | Verified locally; hosted provider pending |
| Razorpay test payments               | Server orders, checkout verification, webhook deduplication and refunds with provider fakes                             | Verified locally; vendor sheet pending    |
| OpenAPI TypeScript contracts         | `packages/api-contracts`; generation is deterministic and CI rejects drift                                              | Verified locally                          |
| Shared design system                 | `packages/design-tokens`, five screen boards and implementation guidance                                                | Verified locally                          |
| Docker and Compose                   | API/operator images build, migrate, run non-root, return healthy probes and serve SPA fallback/CSP                      | Verified locally                          |
| Render, EAS and GitHub Actions       | Schema-valid Render blueprint, protected migration/deploy jobs, Android build/emulator workflow and public smoke script | Implemented; hosted pending               |
| Vue history preservation             | Existing `frontend` application and v1 screenshots remain unchanged                                                     | Verified locally                          |

## Product journeys

| Journey                             | Evidence                                                                                             | Status                                     |
| ----------------------------------- | ---------------------------------------------------------------------------------------------------- | ------------------------------------------ |
| Service wake-up and retry           | Explicit mobile launch state plus bounded operator pre-login health retry                            | Verified locally                           |
| Driver registration and login       | Strict Zod/RHF forms, rotating SecureStore refresh session and role-safe API                         | Verified locally                           |
| Map search and availability filters | Mapbox screen, name/address search, radius/time/type sheet and eligible-lot-only PostGIS query       | Verified locally                           |
| Vehicle CRUD                        | Create, edit, select and remove car/bike/EV/accessible vehicles; ownership checks remain server-side | Verified locally                           |
| Quote and ten-minute hold           | 30-minute arrival/duration controls through 24 hours, authoritative quote and idempotent hold        | Verified locally                           |
| Razorpay checkout                   | Native test checkout, server verification and signed webhook path                                    | Backend verified; EAS/vendor sheet pending |
| Offline QR pass                     | SecureStore cache and signed reservation-ID/nonce payload with live scan validation                  | Verified locally; physical device pending  |
| Cancellation and refund             | Pre-start cancellation, captured test refund and repeat-safety integration tests                     | Verified locally                           |
| Operator inventory                  | Facility create/edit/state, spot operational state and explicit lot assignments                      | Verified locally                           |
| Scan, check-in and checkout         | Camera/manual scan, replay protection, state transitions and immediate query invalidation            | Verified locally                           |
| Occupancy and revenue               | Ten-second polling, animated KPIs and Recharts reporting                                             | Verified locally                           |

## Automated acceptance scenarios

| Scenario from plan                                  | Authoritative evidence                                                      | Status                       |
| --------------------------------------------------- | --------------------------------------------------------------------------- | ---------------------------- |
| Reject privileged registration fields               | Flask contract test                                                         | Verified                     |
| Driver/operator ownership and role isolation        | PostgreSQL integration tests                                                | Verified                     |
| Reject expired/rotated refresh tokens               | PostgreSQL integration tests                                                | Verified                     |
| Structured validation errors and request IDs        | Flask contract tests                                                        | Verified                     |
| Radius/time/type filters return eligible facilities | PostgreSQL integration test                                                 | Verified                     |
| Database rejects overlapping reservations           | Exclusion constraint plus integration tests                                 | Verified                     |
| Fifty contenders produce exactly one hold           | Threaded PostgreSQL integration test                                        | Verified                     |
| Idempotency replay and changed-body rejection       | PostgreSQL integration tests                                                | Verified                     |
| Invalid payment signature preserves state           | PostgreSQL integration test                                                 | Verified                     |
| Duplicate webhook causes one transition             | PostgreSQL integration test                                                 | Verified                     |
| Missing/invalid/retried QStash signatures           | Flask callback contract tests                                               | Verified                     |
| Expired holds restore availability                  | PostgreSQL integration test                                                 | Verified                     |
| Invalid/completed/cancelled/replayed QR rejected    | PostgreSQL integration tests                                                | Verified                     |
| Cancellation/refund rules                           | PostgreSQL integration tests                                                | Verified                     |
| Active QR remains visible offline                   | SecureStore implementation; signed APK airplane-mode run still required     | Device pending               |
| Operator critical flow                              | Playwright facility edit → spot state → scan → check-in → checkout → report | Verified                     |
| Android critical flow                               | Maestro reaches the Razorpay boundary in the EAS workflow                   | EAS/vendor sheet pending     |
| Contract generation has no diff                     | Regeneration hash check and CI gate                                         | Verified                     |
| Images start non-root and pass readiness            | Local Docker runtime plus clean-runner CI steps                             | Verified locally; CI pending |

## Release acceptance boundary

The repository implementation is ready for review, but the 8/10 **hosted release is
not accepted yet**. The following evidence cannot be manufactured locally:

- green GitHub `verify`, `security`, and `containers` jobs on the release commit;
- live Render API and operator URLs backed by Neon and Upstash;
- an installable signed EAS Android APK/internal-build URL;
- Razorpay's real test sheet completing payment on that APK;
- airplane-mode display of the resulting QR pass on the documented Android device;
- the hosted QR → check-in → checkout smoke journey;
- verified deployment screenshots and a two-to-four-minute demo video.

Provider values and the exact first-release procedure are listed in
`docs/release-checklist.md`. None of the pending rows should be changed to verified
until the linked run, URL, build, screenshot, or device result exists.
