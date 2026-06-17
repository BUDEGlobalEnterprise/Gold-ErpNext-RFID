"""
Live Monitor API — WebSocket event publishing, multi-store command center,
and anomaly detection engine for Phase 3.
"""

from typing import Any

import frappe
from frappe import _
from frappe.utils import add_days, cint, flt, getdate, now_datetime, today

# ──────────────────────────────────────────────────
# 1. Real-time Event Publishing
# ──────────────────────────────────────────────────


def publish_repair_event(event_type: str, data: dict) -> None:
	"""Publish a repair-related event.

	Called from RepairOrder controller hooks and repair API endpoints. Routed
	through the central realtime bus (``zevar_core.api.realtime.bus``) so the
	envelope and the privacy rule are consistent. The event name
	(``repair_live_event``) and payload fields are preserved so existing callers
	and the CommandCenter subscription keep working.
	"""
	from zevar_core.api.realtime.bus import publish

	publish(
		"repair_live_event",
		{
			"event_type": event_type,
			"user": frappe.session.user,
			"user_name": frappe.db.get_value("User", frappe.session.user, "full_name")
			or frappe.session.user,
			**data,
		},
	)


# ──────────────────────────────────────────────────
# 2. Multi-Store Command Center
# ──────────────────────────────────────────────────


@frappe.whitelist(allow_guest=False)
def get_command_center_data() -> dict[str, Any]:
	"""Get aggregated real-time data for the multi-store command center.

	Returns per-store metrics, system-wide KPIs, and active alerts.
	"""
	frappe.only_for(["System Manager", "Store Manager", "Accounts Manager"])

	today_date = today()
	stores = _get_store_metrics(today_date)
	system_kpis = _get_system_kpis(today_date)
	alerts = run_anomaly_detection()

	return {
		"stores": stores,
		"system": system_kpis,
		"alerts": alerts,
		"timestamp": str(now_datetime()),
	}


def _get_store_metrics(today_date: str) -> list[dict]:
	"""Get per-store repair and sales metrics."""
	warehouses = frappe.get_all(
		"Warehouse",
		filters={"is_group": 0, "disabled": 0},
		fields=["name", "warehouse_name"],
		order_by="warehouse_name",
	)

	stores = []
	for wh in warehouses:
		# Active repairs
		active = cint(
			frappe.db.count(
				"Repair Order",
				filters={
					"warehouse": wh.name,
					"status": ["not in", ["Delivered", "Cancelled"]],
				},
			)
		)

		# Live sales today for this store (Q7 - the #1 owner metric).
		sales_today = flt(
			frappe.db.sql(
				"""
            SELECT COALESCE(SUM(base_net_total), 0) FROM `tabSales Invoice`
            WHERE is_pos = 1 AND docstatus = 1 AND posting_date = %(today)s
              AND set_warehouse = %(wh)s
            """,
				{"today": today_date, "wh": wh.name},
			)[0][0],
			2,
		)
		sales_txn_today = cint(
			frappe.db.count(
				"Sales Invoice",
				filters={
					"is_pos": 1,
					"docstatus": 1,
					"posting_date": today_date,
					"set_warehouse": wh.name,
				},
			)
		)

		# Never omit a quiet store that is selling (Q7 fix): only skip stores with
		# neither repair activity nor a sale today.
		if active == 0 and sales_txn_today == 0:
			continue

		# Overdue count
		overdue = cint(
			frappe.db.count(
				"Repair Order",
				filters={
					"warehouse": wh.name,
					"status": ["not in", ["Delivered", "Cancelled"]],
					"promised_date": ["is", "set"],
				},
			)
		)

		# Today's completions
		completed_today = cint(
			frappe.db.count(
				"Repair Order",
				filters={
					"warehouse": wh.name,
					"status": "Delivered",
					"delivered_date": today_date,
				},
			)
		)

		# Today's intake
		received_today = cint(
			frappe.db.count(
				"Repair Order",
				filters={
					"warehouse": wh.name,
					"received_date": today_date,
				},
			)
		)

		# Revenue today
		revenue = flt(
			frappe.db.sql(
				"""
            SELECT COALESCE(SUM(total_cost), 0) FROM `tabRepair Order`
            WHERE warehouse = %(wh)s AND status = 'Delivered' AND delivered_date = %(today)s
            """,
				{"wh": wh.name, "today": today_date},
			)[0][0],
			2,
		)

		# Status breakdown
		status_data = frappe.db.sql(
			"""
            SELECT status, COUNT(*) as cnt FROM `tabRepair Order`
            WHERE warehouse = %(wh)s AND status NOT IN ('Delivered', 'Cancelled')
            GROUP BY status
            """,
			{"wh": wh.name},
			as_dict=True,
		)

		stores.append(
			{
				"warehouse": wh.name,
				"name": wh.warehouse_name,
				"active": active,
				"overdue": overdue,
				"completed_today": completed_today,
				"received_today": received_today,
				"revenue_today": revenue,
				"sales_today": sales_today,
				"sales_txn_today": sales_txn_today,
				"status_breakdown": {r.status: r.cnt for r in status_data},
				"health": "critical" if overdue > 5 else ("warning" if overdue > 2 else "healthy"),
			}
		)

	stores.sort(key=lambda s: s["active"], reverse=True)
	return stores


def _get_system_kpis(today_date: str) -> dict:
	"""System-wide KPIs across all stores."""
	total_active = cint(
		frappe.db.count(
			"Repair Order",
			filters={"status": ["not in", ["Delivered", "Cancelled"]]},
		)
	)

	total_overdue = cint(
		frappe.db.count(
			"Repair Order",
			filters={
				"status": ["not in", ["Delivered", "Cancelled"]],
				"promised_date": ["is", "set"],
			},
		)
	)

	completed_today = cint(
		frappe.db.count(
			"Repair Order",
			filters={"status": "Delivered", "delivered_date": today_date},
		)
	)

	received_today = cint(
		frappe.db.count(
			"Repair Order",
			filters={"received_date": today_date},
		)
	)

	revenue_today = flt(
		frappe.db.sql(
			"""
        SELECT COALESCE(SUM(total_cost), 0) FROM `tabRepair Order`
        WHERE status = 'Delivered' AND delivered_date = %(today)s
        """,
			{"today": today_date},
		)[0][0],
		2,
	)

	return {
		"total_active": total_active,
		"total_overdue": total_overdue,
		"completed_today": completed_today,
		"received_today": received_today,
		"revenue_today": revenue_today,
	}


# ──────────────────────────────────────────────────
# 3. Anomaly Detection Engine
# ──────────────────────────────────────────────────


@frappe.whitelist(allow_guest=False)
def run_anomaly_detection() -> list[dict[str, Any]]:
	"""Run anomaly detection rules and return active alerts.

	Rules:
	1. Severely overdue repairs (>7 days past promised)
	2. Unusual volume spikes/drops
	3. Stuck repairs (no status change in 5+ days)
	4. Unassigned repairs > 24h
	5. High-value repairs without deposit
	"""
	frappe.has_permission("Repair Order", ptype="read", throw=True)

	alerts: list[dict] = []
	today_date = today()

	# Rule 1: Severely overdue (>7 days)
	severe_overdue = frappe.db.sql(
		"""
        SELECT ro.name, c.customer_name, ro.promised_date, ro.status, ro.warehouse,
               DATEDIFF(%(today)s, ro.promised_date) as days_overdue
        FROM `tabRepair Order` ro
        LEFT JOIN `tabCustomer` c ON c.name = ro.customer
        WHERE ro.status NOT IN ('Delivered', 'Cancelled')
          AND ro.promised_date IS NOT NULL
          AND DATEDIFF(%(today)s, ro.promised_date) > 7
        ORDER BY days_overdue DESC
        LIMIT 10
        """,
		{"today": today_date},
		as_dict=True,
	)
	for r in severe_overdue:
		alerts.append(
			{
				"severity": "critical",
				"type": "severe_overdue",
				"title": f"Severely overdue: {r.name}",
				"message": f"{r.customer_name or '—'} — {r.days_overdue} days past due ({r.status})",
				"repair": r.name,
				"warehouse": r.warehouse,
			}
		)

	# Rule 2: Stuck repairs (no activity in 5+ days on active repairs)
	stuck = frappe.db.sql(
		"""
        SELECT ro.name, c.customer_name, ro.status, ro.modified, ro.warehouse,
               DATEDIFF(%(today)s, ro.modified) as days_stuck
        FROM `tabRepair Order` ro
        LEFT JOIN `tabCustomer` c ON c.name = ro.customer
        WHERE ro.status IN ('In Progress', 'Waiting for Parts', 'Estimated')
          AND DATEDIFF(%(today)s, ro.modified) >= 5
        ORDER BY days_stuck DESC
        LIMIT 10
        """,
		{"today": today_date},
		as_dict=True,
	)
	for r in stuck:
		alerts.append(
			{
				"severity": "warning",
				"type": "stuck_repair",
				"title": f"Stuck repair: {r.name}",
				"message": f"No activity for {r.days_stuck} days in '{r.status}' status",
				"repair": r.name,
				"warehouse": r.warehouse,
			}
		)

	# Rule 3: Unassigned repairs > 24h
	unassigned = cint(
		frappe.db.sql(
			"""
        SELECT COUNT(*) FROM `tabRepair Order`
        WHERE (assigned_to IS NULL OR assigned_to = '')
          AND status NOT IN ('Delivered', 'Cancelled')
          AND TIMESTAMPDIFF(HOUR, creation, %(now)s) > 24
        """,
			{"now": str(now_datetime())},
		)[0][0]
	)
	if unassigned > 0:
		alerts.append(
			{
				"severity": "warning",
				"type": "unassigned",
				"title": f"{unassigned} unassigned repair(s)",
				"message": f"{unassigned} repairs have been unassigned for over 24 hours",
				"repair": None,
				"warehouse": None,
			}
		)

	# Rule 4: High-value without deposit (>$500, no deposit)
	no_deposit = cint(
		frappe.db.sql(
			"""
        SELECT COUNT(*) FROM `tabRepair Order`
        WHERE estimated_cost > 500
          AND (deposit_amount IS NULL OR deposit_amount = 0)
          AND status NOT IN ('Delivered', 'Cancelled')
        """,
		)[0][0]
	)
	if no_deposit > 0:
		alerts.append(
			{
				"severity": "info",
				"type": "no_deposit",
				"title": f"{no_deposit} high-value repair(s) without deposit",
				"message": "Repairs over $500 with no deposit collected — financial risk",
				"repair": None,
				"warehouse": None,
			}
		)

	# Sort by severity
	severity_order = {"critical": 0, "warning": 1, "info": 2}
	alerts.sort(key=lambda a: severity_order.get(a["severity"], 9))

	return alerts


# ──────────────────────────────────────────────────
# 4. Live Activity Feed
# ──────────────────────────────────────────────────


@frappe.whitelist(allow_guest=False)
def get_repair_live_feed(hours: int = 4) -> list[dict[str, Any]]:
	"""Get recent repair activity events for the live feed.

	Pulls from the status_log child table and Version history.
	"""
	frappe.has_permission("Repair Order", ptype="read", throw=True)

	hours_ago = frappe.utils.add_to_date(now_datetime(), hours=-int(hours))

	# Get recent status changes from status_log
	events = frappe.db.sql(
		"""
        SELECT
            sl.status, sl.timestamp, sl.changed_by, sl.notes,
            ro.name as repair_order, c.customer_name, ro.warehouse,
            ro.repair_type
        FROM `tabRepair Status Log` sl
        JOIN `tabRepair Order` ro ON sl.parent = ro.name
        LEFT JOIN `tabCustomer` c ON c.name = ro.customer
        WHERE sl.timestamp >= %(since)s
        ORDER BY sl.timestamp DESC
        LIMIT 100
        """,
		{"since": str(hours_ago)},
		as_dict=True,
	)

	feed = []
	for ev in events:
		user_name = ""
		if ev.changed_by:
			user_name = frappe.db.get_value("User", ev.changed_by, "full_name") or ev.changed_by

		feed.append(
			{
				"type": "status_change",
				"repair": ev.repair_order,
				"customer": ev.customer_name,
				"warehouse": ev.warehouse,
				"status": ev.status,
				"timestamp": str(ev.timestamp),
				"user": ev.changed_by,
				"user_name": user_name,
				"repair_type": ev.repair_type,
				"notes": ev.notes or "",
			}
		)

	return feed
