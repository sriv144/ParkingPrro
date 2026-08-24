# ADR-004: PostgreSQL exclusion constraint for booking safety

**Status:** Accepted

Use a GiST exclusion constraint over spot ID and a half-open `tstzrange` for blocking
reservation states. Application checks improve errors but cannot be the concurrency
authority. This constraint makes overlapping active reservations impossible even
when multiple API requests race.
