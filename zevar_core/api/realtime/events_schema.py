"""Versioned realtime event schema — the single source of truth (Phase 0).

Both the Python publishers (``bus.publish``) and the generated TypeScript
(``frontend/zevar_ui/src/types/realtime-events.ts``, produced by
``scripts/gen_realtime_types.py``) read :data:`EVENT_TYPES` below, so a field
added here appears on both sides with no hand-sync. The CI gate
``gen_realtime_types.py --check`` fails the build if the checked-in ``.ts``
drifts from this registry — this is what kills the ``new_status`` vs ``status``
class of bug.

Phase 0 seed: the channels and event types the suite already emits (Q6 bus +
the sale/repair/anomaly/health producers). Add new events here and re-run the
generator.
"""

from __future__ import annotations

from typing import Any

SCHEMA_VERSION = "1.0.0"

# Channel taxonomy. ``scope`` encodes the privacy rule from the bus:
#   admin  -> manager/owner room (or legacy global for ops events)
#   store  -> room="store_<warehouse>"
#   user   -> user=<employee_user_id>  (NEVER global; personal data)
CHANNELS: dict[str, dict[str, str]] = {
	"repair_live_event": {"scope": "admin", "description": "Repair status changes."},
	"repair_anomaly_alert": {"scope": "admin", "description": "Anomaly-detection output."},
	"system_health": {"scope": "admin", "description": "System health heartbeat."},
	"sales_tick": {"scope": "store", "description": "Sale posted / cancelled."},
	"associate_personal": {"scope": "user", "description": "Employee-attributed event (user-scoped only)."},
}

# TS type mapping for payload fields.
TYPE_MAP: dict[str, str] = {
	"str": "string",
	"int": "number",
	"float": "number",
	"bool": "boolean",
	"OptionalStr": "string | null",
	"OptionalInt": "number | null",
	"OptionalFloat": "number | null",
}

# The registry. Each entry: channel + payload field -> python type label.
# ``type label`` must be a key in TYPE_MAP (or a literal TS type).
EVENT_TYPES: dict[str, dict[str, Any]] = {
	"sale.completed": {
		"channel": "sales_tick",
		"fields": {
			"invoice": "str",
			"customer": "OptionalStr",
			"net_total": "float",
			"grand_total": "float",
			"qty": "int",
			"channel": "str",
			"gross_margin_pct": "OptionalFloat",
		},
	},
	"sale.cancelled": {
		"channel": "sales_tick",
		"fields": {
			"invoice": "str",
			"reason": "OptionalStr",
		},
	},
	"repair.status_changed": {
		"channel": "repair_live_event",
		"fields": {
			"repair": "str",
			"status": "str",  # canonical status string
			"customer": "OptionalStr",
			"warehouse": "OptionalStr",
			"assigned_to": "OptionalStr",
		},
	},
	"anomaly.detected": {
		"channel": "repair_anomaly_alert",
		"fields": {
			"severity": "str",  # critical | warning | info
			"type": "str",
			"title": "str",
			"message": "str",
			"count": "OptionalInt",
		},
	},
	"health.heartbeat": {
		"channel": "system_health",
		"fields": {
			"active_repairs": "OptionalInt",
			"pos_invoices_submitted": "OptionalInt",
		},
	},
}


def envelope_fields() -> dict[str, str]:
	"""The common EventEnvelope wrapped around every payload (matches bus.publish)."""
	return {
		"v": "str",
		"id": "str",
		"channel": "str",
		"event_type": "str",
		"ts": "str",
		"store": "OptionalStr",
		"actor_user": "str",
		"actor_name": "str",
	}
