# ParkingPro engineering documentation

**Status:** Implemented

This directory is the source of truth for ParkingPro v2. Documents move through
`Draft`, `Approved`, `Implemented`, and `Verified`; a document is `Verified` only
after its claims are exercised against the deployed release.

## Product and design

- [Product](product.md) — actors, journeys, release boundaries, and acceptance.
- [Design system](design-system.md) — visual thesis, tokens, motion, and mockups.
- [Legacy Vue showcase](screenshots/) — verified screenshots of ParkingPrro v1.

## Engineering

- [Architecture](architecture.md) — system context, components, and data flow.
- [Data model](data-model.md) — entities, states, and database invariants.
- [API contract](api-contract.md) — public endpoints and error conventions.
- [Security](security.md) — trust boundaries and secure defaults.
- [Testing](testing.md) — test layers and release gates.
- [Completion audit](completion-audit.md) — plan-to-evidence matrix and hosted boundary.
- [Deployment](deployment.md) — local, preview, production, and rollback procedures.
- [Hosted release checklist](release-checklist.md) — provider setup and evidence gate.
- [Skills](skills.md) — reviewed AI workflow guidance; never runtime dependencies.
- [Architecture decisions](adr/) — decisions and rejected alternatives.

## Status rules

- **Draft:** incomplete or awaiting a product decision.
- **Approved:** decision-complete and safe to implement.
- **Implemented:** represented in code but not yet proven in production.
- **Verified:** automated tests and deployed evidence support every claim.
