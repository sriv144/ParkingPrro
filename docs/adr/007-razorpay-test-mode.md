# ADR-007: Razorpay test mode

**Status:** Accepted

Use Razorpay test orders to demonstrate provider boundaries, signatures, webhooks,
idempotency, and refunds in INR without collecting money. The API owns amount and
state; clients never confirm payment based only on a local success callback.
