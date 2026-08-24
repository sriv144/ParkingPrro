# ParkingPro product specification

**Status:** Implemented

ParkingPro is a portfolio parking-reservation system for Bengaluru. A driver uses
an Android application to find and reserve a synthetic parking facility; an
operator uses a React console to manage inventory and complete entry and exit.
Payments use Razorpay test mode and never collect real money.

## Actors

- **Driver:** registers, manages vehicles, searches, reserves, pays in test mode,
  presents an offline pass, cancels eligible stays, and views history.
- **Operator:** can access only assigned facilities, manage facility inventory,
  inspect reservations, scan passes, and check vehicles in and out.
- **Administrator:** creates operator accounts and facility assignments through a
  protected CLI. There is no public administrator-registration path.
- **Reviewer:** uses documented demo accounts and can follow the complete journey
  without private credentials or local tooling.

## Driver journey

1. Start the application and wait for the free preview API if it is sleeping.
2. Register or use the demo driver, then add/select a vehicle.
3. Search a map, choose a facility, start time, duration, and spot type.
4. Review an authoritative server quote and create a ten-minute hold.
5. Complete a Razorpay test payment; the signed webhook confirms the booking.
6. Cache and display the signed QR pass even when the device is offline.
7. Present the pass at entry, monitor the active stay, and complete checkout.

## Operator journey

1. Sign in with the demo operator account.
2. Review occupancy, recent activity, and assigned facilities.
3. Search the reservation queue or scan a QR pass.
4. Verify the server-returned driver, vehicle, facility, spot, time, and status.
5. Check in a confirmed reservation and check out an active reservation.
6. Review updated occupancy and test-mode revenue reports.

## Early-release boundaries

Included: Android internal distribution, responsive operator web, Flask API,
PostgreSQL booking safety, test payments, signed serverless jobs, Docker, CI/CD,
security gates, and synthetic Bengaluru data.

Deferred: iOS, real payments, social login, password reset delivery, WebSockets,
Celery in production, multi-tenant organizations, Kubernetes, Jenkins, formal
SLOs, and public Play Store publication.

## Release acceptance

- Search → hold → test payment → QR → check-in → checkout works end to end.
- One spot cannot have overlapping active holds/bookings, including under load.
- Drivers cannot read other drivers' data or call operator endpoints.
- Duplicate commands, Razorpay events, and QStash deliveries are safe.
- All clients explain offline, expired-session, empty, failure, and cold-start states.
- Documentation contains only measured or directly verified claims.
