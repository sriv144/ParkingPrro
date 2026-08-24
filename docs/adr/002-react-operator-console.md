# ADR-002: React replaces Vue for the operator console

**Status:** Accepted

Build a new Vite React console against the v2 OpenAPI contract. Keep Vue operational
until feature parity, then preserve it under `legacy/vue-showcase`. Do not translate
Vue components mechanically; preserve verified behaviours and redesign the workflow.
