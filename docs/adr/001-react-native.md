# ADR-001: React Native instead of Flutter

**Status:** Accepted

Use Expo React Native for the driver app to demonstrate React/TypeScript across
mobile and web while retaining native maps, camera, notifications, secure storage,
and Android distribution. Flutter is capable but weakens the intended React resume
narrative and prevents sharing TypeScript contracts/domain utilities.

The implementation uses Expo SDK 57 rather than the originally planned SDK 56.
Expo Doctor identified a Hermes V1 memory regression in SDK 56; SDK 57 with React
Native 0.86.2 contains the upstream fix and passes all Expo dependency checks.
