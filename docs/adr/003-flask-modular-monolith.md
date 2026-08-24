# ADR-003: Flask modular monolith

**Status:** Accepted

Retain Flask and separate auth, catalog, reservation, payment, operator, and job
modules inside one deployable API. This preserves backend continuity and transaction
boundaries. Microservices add failure modes and operational cost without release-scale
benefit.
