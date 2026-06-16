"""Scheduler-driven realtime pushes (Quick-Win Q6).

These run on a cadence so anomalies and system-health reach the wall without a
client having to force a poll. Registered in ``hooks.py`` scheduler_events.
"""

from __future__ import annotations

import frappe

from zevar_core.api.realtime.bus import publish


def run_anomaly_push() -> None:
	"""Every 2 minutes: run anomaly detection and push active alerts.

	Publishes on ``repair_anomaly_alert`` (the event ``CommandCenter.vue``
	already subscribes to), so alerts surface live without a screen open.
	"""
	try:
		from zevar_core.api.live_monitor import run_anomaly_detection

		alerts = run_anomaly_detection() or []
	except Exception:
		frappe.log_error(title="Anomaly push failed", message=frappe.get_traceback())
		return

	if alerts:
		publish("repair_anomaly_alert", {"alerts": alerts, "count": len(alerts)})


def run_health_heartbeat() -> None:
	"""Every 5 minutes: push a lightweight system-health pulse on ``system_health``."""
	try:
		active_repairs = frappe.db.count(
			"Repair Order", filters={"status": ["not in", ["Delivered", "Cancelled"]]}
		)
		open_invoices_today = frappe.db.count(
			"Sales Invoice", filters={"docstatus": 1, "is_pos": 1}
		)
	except Exception:
		frappe.log_error(title="Health heartbeat failed", message=frappe.get_traceback())
		return

	publish(
		"system_health",
		{"active_repairs": active_repairs, "pos_invoices_submitted": open_invoices_today},
	)
