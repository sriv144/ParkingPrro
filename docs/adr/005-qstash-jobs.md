# ADR-005: QStash for the free-tier release

**Status:** Accepted

Use signed delayed HTTP callbacks for hold expiry and reminders. Free Render hosting
does not provide a continuous worker. Keep job handlers provider-neutral so a paid
Celery/Redis worker can replace the scheduler without changing reservation rules.
