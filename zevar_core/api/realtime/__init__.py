"""Realtime event-bus package (Quick-Win Q6).

Phase 0 will extend this with a versioned event schema, a 24h rolling
``live_event_log`` backfill table, and generated TypeScript types. For the
Quick-Win Sprint it provides a single :func:`publish` entry point that
centralises realtime publishing and enforces the privacy rule, plus the
scheduler-driven pushes (anomaly / health) so the wall updates on a cadence
instead of only when a client forces a poll.
"""
