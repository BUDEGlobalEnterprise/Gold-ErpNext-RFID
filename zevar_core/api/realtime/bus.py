"""Lean realtime publish entry point (Quick-Win Q6).

Single place that wraps ``frappe.publish_realtime`` so every push carries a
consistent envelope (``timestamp`` + ``actor_user``) and the privacy rule is
enforced in one spot.

Privacy rule (the F4 fix): any payload that references a named employee,
customer, or commission amount MUST be published with ``user=`` (delivers only
to that user's personal socket) or to a manager-only ``room=`` - never broadcast
globally. The old ``publish_employee_event`` violated this and has been deleted.

Channel / event-name taxonomy is kept stable so existing frontend subscriptions
keep working:
  - ``repair_live_event``     repair status changes (admin/ops)
  - ``repair_anomaly_alert``  anomaly-detection output (admin)
  - ``system_health``         health heartbeat pulse (admin)

NOTE: full ``admin_wall`` room hardening (so admin/ops events also stop
broadcasting to every socket) lands in Phase 0 together with the frontend
room-join. Today, calls with neither ``user`` nor ``room`` broadcast as before
to avoid breaking the repair feed the wall already subscribes to.
"""

from __future__ import annotations

import frappe
from frappe.utils import now_datetime


def publish(event_name: str, data: dict | None = None, *, user: str | None = None, room: str | None = None, after_commit: bool = True) -> None:
	"""Publish a realtime event with a consistent envelope.

	:param event_name: socket event name (one of the channels above).
	:param data: event payload.
	:param user: deliver ONLY to this user's personal socket (required for any
	    employee/customer/commission-attributed payload).
	:param room: deliver only to clients that joined this room.
	With neither ``user`` nor ``room`` the event broadcasts to all connected
	clients (legacy behaviour; only for admin/ops events with no personal data).
	"""
	payload = {
		"timestamp": str(now_datetime()),
		"actor_user": frappe.session.user,
		**((data or {}) if isinstance(data, dict) else {"data": data}),
	}
	kwargs = {"event": event_name, "message": payload, "after_commit": after_commit}
	if user:
		kwargs["user"] = user
	elif room:
		kwargs["room"] = room
	frappe.publish_realtime(**kwargs)
