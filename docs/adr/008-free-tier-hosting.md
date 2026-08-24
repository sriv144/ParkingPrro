# ADR-008: Free-tier deployment

**Status:** Accepted

Use Render, Neon, Upstash, and Expo EAS free tiers for the public portfolio preview.
Accept API cold starts and no uptime SLA, expose warm-up/retry UX, and document the
paid path. Do not add Kubernetes or Jenkins to disguise the system's actual scale.
