# ParkingPro hosted-release checklist

**Status:** Implemented

The application and release automation are implemented. This checklist separates
repository readiness from external publication so the README never implies a live
release before hosted smoke tests pass.

## Current external state (2026-08-24)

- GitHub remote: `sriv144/ParkingPrro` (public), default branch `main`.
- Implementation branch: `codex/parkingpro-v2-foundation` at local base `d6a94ab`.
- GitHub authentication is available, but the repository currently has no Actions
  secrets, variables, protected `parkingpro-production` environment, workflows, or
  workflow runs on the remote.
- No commit, push, provider resource, migration, or deployment was created by this
  implementation session.
- Local PostGIS migrations, expanded application gates, and final non-root API and
  operator container health checks passed; hosted CI, EAS build, provider payment,
  and public smoke tests are still release requirements.

## GitHub environment

Create a protected `parkingpro-production` environment with an approval rule for
the migration/deploy jobs. Configure these repository values:

| Kind     | Name                                | Source                                                  |
| -------- | ----------------------------------- | ------------------------------------------------------- |
| Secret   | `PRODUCTION_DATABASE_URL`           | Neon pooled PostgreSQL URL with PostGIS access          |
| Secret   | `RENDER_API_DEPLOY_HOOK`            | Render API service deploy hook                          |
| Secret   | `RENDER_WEB_DEPLOY_HOOK`            | Render static-site deploy hook                          |
| Secret   | `PARKINGPRO_DEMO_DRIVER_PASSWORD`   | Synthetic driver credential                             |
| Secret   | `PARKINGPRO_DEMO_OPERATOR_PASSWORD` | Synthetic, facility-scoped operator credential          |
| Secret   | `EXPO_TOKEN`                        | Expo robot/personal access token scoped to this project |
| Secret   | `EXPO_PUBLIC_MAPBOX_ACCESS_TOKEN`   | Restricted Mapbox public runtime token                  |
| Secret   | `RNMAPBOX_MAPS_DOWNLOAD_TOKEN`      | Mapbox downloads token used only by EAS build           |
| Variable | `PARKINGPRO_API_URL`                | Public HTTPS API origin                                 |
| Variable | `PARKINGPRO_WEB_URL`                | Public HTTPS operator origin                            |
| Variable | `PARKINGPRO_DEMO_DRIVER_EMAIL`      | Published synthetic driver email                        |
| Variable | `PARKINGPRO_DEMO_OPERATOR_EMAIL`    | Published synthetic operator email                      |
| Variable | `EXPO_PROJECT_ID`                   | EAS project UUID                                        |
| Variable | `EXPO_PUBLIC_RAZORPAY_KEY_ID`       | Razorpay test-mode public key ID                        |

Do not use a personal password or a production-privileged operator account for the
published demo. Rotate the demo credentials if the environment is abused.

## Runtime providers

1. Create Neon PostgreSQL and enable `postgis` and `btree_gist` (the migration also
   uses `CREATE EXTENSION IF NOT EXISTS`).
2. Create Upstash Redis and QStash. Copy the Redis URL, QStash token, and both
   receiver signing keys into Render.
3. Create Razorpay test keys and a webhook secret. Register
   `/api/v1/webhooks/razorpay` on the final API origin.
4. Create a Render Blueprint, select the custom path
   `infrastructure/render/render.yaml`, set all `sync: false` values, and keep
   auto-deploy off because GitHub deploy hooks gate releases after CI. The file is
   locally validated against Render's official Blueprint schema.
5. Create the EAS project, set the project UUID, and configure Android push
   credentials before expecting remote notifications.
6. Configure Sentry projects/DSNs as desired; the API automatically uses Render's
   git commit as its release identifier.

## First release

1. Review and commit only the ParkingPro paths on the feature branch.
2. Push the branch and open a draft pull request to `main`.
3. Confirm `verify`, `security`, and `containers` are green, including PostGIS
   concurrency, contract drift, CodeQL, Gitleaks, and Trivy.
4. Merge after review. The protected job migrates and deterministically seeds five
   Bengaluru facilities and both demo accounts, then triggers Render deploy hooks.
5. Confirm the public smoke job passes readiness, demo login, facility count,
   driver/operator isolation, and operator HTML checks.
6. Run the Android internal-build workflow, install the APK on the documented
   mid-range Android device, and execute the Maestro flow.
7. Record verified screenshots, a 2–4 minute demo video, exact live URLs, build URL,
   CI run, migration revision, and test date in the root README.

The release is not accepted until the complete search → hold → Razorpay test
payment → offline QR → operator scan → check-in → checkout path succeeds against
the hosted services.
