# ParkingPro AI workflow skills

**Status:** Approved

Skills are reviewable workflow guidance, not application dependencies. Before use,
record the retrieval date, source revision/license, inputs, expected output, and any
guidance intentionally modified or rejected. Official framework/provider docs remain
authoritative when a community skill conflicts.

| Phase          | Skill                                   | Install command                                                                        | Decision                          |
| -------------- | --------------------------------------- | -------------------------------------------------------------------------------------- | --------------------------------- |
| React Native   | Official Expo skills                    | `codex plugin add expo@openai-curated`                                                 | Required when available           |
| Product UI     | `creative-design/ui-ux-pro-max`         | `npx claude-code-templates@latest --skill creative-design/ui-ux-pro-max --yes`         | Supplement local frontend skill   |
| React web      | `development/frontend-dev-guidelines`   | `npx claude-code-templates@latest --skill development/frontend-dev-guidelines --yes`   | Review before use                 |
| Python         | `development/python-pro`                | `npx claude-code-templates@latest --skill development/python-pro --yes`                | Review before use                 |
| PostgreSQL     | `database/postgresql`                   | `npx claude-code-templates@latest --skill database/postgresql --yes`                   | Required for schema work          |
| API security   | `security/api-security-best-practices`  | `npx claude-code-templates@latest --skill security/api-security-best-practices --yes`  | Supplement secure-coding baseline |
| Testing        | `development/testing-patterns`          | `npx claude-code-templates@latest --skill development/testing-patterns --yes`          | Review before use                 |
| Browser E2E    | `development/playwright-e2e-builder`    | `npx claude-code-templates@latest --skill development/playwright-e2e-builder --yes`    | Required for web E2E              |
| Accessibility  | `creative-design/accessibility-auditor` | `npx claude-code-templates@latest --skill creative-design/accessibility-auditor --yes` | Required before release           |
| Containers     | `development/docker-expert`             | `npx claude-code-templates@latest --skill development/docker-expert --yes`             | Required for Docker review        |
| CI/CD          | `development/github-actions-creator`    | `npx claude-code-templates@latest --skill development/github-actions-creator --yes`    | Required for workflow review      |
| 9/10 hardening | `development/observability-engineer`    | `npx claude-code-templates@latest --skill development/observability-engineer --yes`    | Deferred                          |

**Catalog retrieval date:** 2026-08-21. Community entries above were identified
through [AI Templates](https://www.aitmpl.com/) and its
[component documentation](https://docs.aitmpl.com/introduction). Each package's
manifest is the authoritative source URL, version, and license; those fields remain
pending review until the user installs a reviewed revision. ParkingPro does not
silently execute latest-tag community templates.

| Guidance            | Required input                    | Expected output                             | Current disposition                    |
| ------------------- | --------------------------------- | ------------------------------------------- | -------------------------------------- |
| Expo / React Native | Approved flows, providers, SDK    | Accessible Expo Router app and EAS checks   | Local equivalent applied               |
| UI/UX               | Visual thesis, screens, reference | Tokens, mobile/web boards, motion rules     | Accepted; generated under docs/mockups |
| React web           | OpenAPI and operator journeys     | Typed routes, query states, responsive UI   | Accepted with security changes         |
| Python / PostgreSQL | Domain and threats                | Flask modules, migrations, constraints      | Accepted; database stays authoritative |
| API security        | Actors, callbacks, secrets        | Least privilege, rotation, CSRF, signatures | Accepted and implemented               |
| Testing             | Acceptance scenarios              | Unit, integration, contract, and E2E tests  | Hosted/device verification pending     |
| Docker / CI         | Runtime graph, gates              | Non-root images and gated workflow          | Accepted; local runtime verified       |
| Accessibility       | Completed screens                 | Audit findings and remediations             | Formal device audit pending            |

The built-in local image-generation, frontend, and security-best-practices skills
were applied during implementation. They produced the five screen boards, shared
visual constraints, strict role and ownership controls, in-memory web access
tokens, SecureStore mobile refresh tokens, signature checks, and production
fail-closed configuration. Skills remain workflow guidance, never dependencies.

Do not install Kubernetes, Jenkins, microservice, Terraform, or offensive-security
bundles for the 8/10 release. Do not execute downloaded scripts before reviewing the
skill source, license, permissions, and repository diff.
