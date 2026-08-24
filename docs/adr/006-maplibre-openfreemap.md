# ADR-006: MapLibre with OpenFreeMap

**Status:** Accepted

Use MapLibre React Native for the native Android map and OpenFreeMap's public dark
style for vector tiles. This preserves the map-first interaction without requiring a
payment method, provider account, API key, or native dependency download token.
OpenFreeMap attribution remains enabled. Its public service has no SLA, so the project
documents it as a free-tier portfolio dependency and can later self-host compatible
tiles without changing the MapLibre client. Seeded facilities avoid dependence on an
external parking-inventory feed.
