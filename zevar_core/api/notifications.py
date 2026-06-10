"""
Notification & Alert System API — Unified alert engine for all dashboard types.

Combines anomaly detection, inventory alerts, cash management alerts, and
sales alerts into a single real-time notification stream.
"""

from typing import Any

import frappe
from frappe import _
from frappe.utils import add_days, cint, flt, getdate, now_datetime, today

# ──────────────────────────────────────────────────
# 1. Unified Alert Engine
# ──────────────────────────────────────────────────


@frappe.whitelist(allow_guest=False)
def get_alerts(severity: str | None = None, limit: int = 50) -> dict[str, Any]:
	"""Get all active alerts for the current user, scoped by role.

	Returns alerts from multiple sources: repairs, inventory, cash, sales.
	Each alert has: severity, type, title, message, timestamp, reference.
	"""
	user = frappe.session.user
	roles = frappe.get_roles(user)
	is_admin = bool(set(roles) & {"System Manager", "Accounts Manager"})
	is_manager = bool(set(roles) & {"Store Manager", "Store Supervisor"}) or is_admin

	alerts: list[dict] = []

	# ── Repair Alerts (all authenticated users see their own; managers see all) ──
	alerts.extend(_get_repair_alerts(is_manager))

	# ── Inventory Alerts (managers and admins) ──
	if is_manager:
		alerts.extend(_get_inventory_alerts())

	# ── Cash Alerts (managers and admins) ──
	if is_manager:
		alerts.extend(_get_cash_alerts())

	# ── Sales Alerts (all staff) ──
	alerts.extend(_get_sales_alerts(is_manager))

	# Sort by severity then timestamp
	severity_order = {"critical": 0, "warning": 1, "info": 2}
	alerts.sort(key=lambda a: (severity_order.get(a.get("severity"), 9), a.get("timestamp", "")))

	if severity:
		alerts = [a for a in alerts if a.get("severity") == severity]

	return {
		"alerts": alerts[: cint(limit)],
		"total": len(alerts),
		"unread_count": len([a for a in alerts if a.get("severity") in ("critical", "warning")]),
		"timestamp": str(now_datetime()),
	}


@frappe.whitelist(allow_guest=False)
def get_alert_summary() -> dict[str, Any]:
	"""Lightweight summary for the notification bell badge.

	Returns counts by severity and the 3 most recent alerts.
	"""
	data = get_alerts(limit=10)
	alerts = data["alerts"]
	return {
		"critical": len([a for a in alerts if a.get("severity") == "critical"]),
		"warning": len([a for a in alerts if a.get("severity") == "warning"]),
		"info": len([a for a in alerts if a.get("severity") == "info"]),
		"total": data["total"],
		"recent": alerts[:3],
	}


# ──────────────────────────────────────────────────
# 2. Alert Source: Repairs
# ──────────────────────────────────────────────────


def _get_repair_alerts(is_manager: bool) -> list[dict]:
	"""Repair-related alerts: overdue, stuck, unassigned, no deposit."""
	alerts: list[dict] = []
	today_date = today()

	# Severely overdue repairs (>7 days past promised date)
	overdue = frappe.db.sql(
		"""
		SELECT name, customer, promised_date, status, warehouse,
		       DATEDIFF(%(today)s, promised_date) as days_overdue
		FROM `tabRepair Order`
		WHERE status NOT IN ('Delivered', 'Cancelled')
		  AND promised_date IS NOT NULL
		  AND DATEDIFF(%(today)s, promised_date) > 7
		ORDER BY days_overdue DESC
		LIMIT 10
	""",
		{"today": today_date},
		as_dict=True,
	)

	for r in overdue:
		alerts.append(
			{
				"severity": "critical",
				"type": "repair_overdue",
				"title": f"Overdue: {r.name}",
				"message": f"{r.customer} — {r.days_overdue} days past due",
				"reference_doctype": "Repair Order",
				"reference_name": r.name,
				"timestamp": str(now_datetime()),
			}
		)

	# Stuck repairs (no activity in 5+ days)
	if is_manager:
		stuck = frappe.db.sql(
			"""
			SELECT name, customer, status, modified, warehouse,
			       DATEDIFF(%(today)s, modified) as days_stuck
			FROM `tabRepair Order`
			WHERE status IN ('In Progress', 'Waiting for Parts', 'Estimated')
			  AND DATEDIFF(%(today)s, modified) >= 5
			ORDER BY days_stuck DESC
			LIMIT 5
		""",
			{"today": today_date},
			as_dict=True,
		)

		for r in stuck:
			alerts.append(
				{
					"severity": "warning",
					"type": "repair_stuck",
					"title": f"Stuck: {r.name}",
					"message": f"No activity for {r.days_stuck} days (status: {r.status})",
					"reference_doctype": "Repair Order",
					"reference_name": r.name,
					"timestamp": str(r.modified),
				}
			)

	# High-value without deposit (>$500)
	if is_manager:
		no_deposit = frappe.db.sql(
			"""
			SELECT name, customer, estimated_cost
			FROM `tabRepair Order`
			WHERE estimated_cost > 500
			  AND (deposit_amount IS NULL OR deposit_amount = 0)
			  AND status NOT IN ('Delivered', 'Cancelled')
			LIMIT 5
		""",
			as_dict=True,
		)

		for r in no_deposit:
			alerts.append(
				{
					"severity": "warning",
					"type": "repair_no_deposit",
					"title": f"No deposit: {r.name}",
					"message": f"${r.estimated_cost:.2f} repair for {r.customer} — no deposit",
					"reference_doctype": "Repair Order",
					"reference_name": r.name,
					"timestamp": str(now_datetime()),
				}
			)

	return alerts


# ──────────────────────────────────────────────────
# 3. Alert Source: Inventory
# ──────────────────────────────────────────────────


def _get_inventory_alerts() -> list[dict]:
	"""Inventory alerts: low stock, overstock, reorder needed."""
	alerts: list[dict] = []

	# Low stock items (actual qty <= reorder_level)
	if not frappe.db.table_exists("Item"):
		return alerts

	low_stock = frappe.db.sql(
		"""
		SELECT i.name, i.item_name, i.item_code,
		       COALESCE(b.actual_qty, 0) as actual_qty,
		       COALESCE(b.warehouse, '') as warehouse
		FROM `tabItem` i
		LEFT JOIN `tabBin` b ON b.item_code = i.item_code
		WHERE i.disabled = 0
		  AND i.is_stock_item = 1
		  AND COALESCE(b.actual_qty, 0) <= COALESCE(i.safety_stock, 0)
		  AND COALESCE(i.safety_stock, 0) > 0
		LIMIT 10
	""",
		as_dict=True,
	)

	for item in low_stock:
		alerts.append(
			{
				"severity": "warning",
				"type": "low_stock",
				"title": f"Low stock: {item.item_name or item.item_code}",
				"message": f"Qty: {item.actual_qty:.0f} at {item.warehouse}",
				"reference_doctype": "Item",
				"reference_name": item.name,
				"timestamp": str(now_datetime()),
			}
		)

	# Items with no stock at all (stocked out)
	stockouts = frappe.db.sql(
		"""
		SELECT i.name, i.item_name, i.item_code
		FROM `tabItem` i
		WHERE i.disabled = 0
		  AND i.is_stock_item = 1
		  AND NOT EXISTS (
		    SELECT 1 FROM `tabBin` b
		    WHERE b.item_code = i.item_code AND b.actual_qty > 0
		  )
		  AND EXISTS (
		    SELECT 1 FROM `tabStock Ledger Entry` sle
		    WHERE sle.item_code = i.item_code
		    AND sle.creation >= DATE_SUB(NOW(), INTERVAL 30 DAY)
		  )
		LIMIT 5
	""",
		as_dict=True,
	)

	for item in stockouts:
		alerts.append(
			{
				"severity": "critical",
				"type": "stockout",
				"title": f"Stockout: {item.item_name or item.item_code}",
				"message": "Previously sold item has zero stock across all locations",
				"reference_doctype": "Item",
				"reference_name": item.name,
				"timestamp": str(now_datetime()),
			}
		)

	return alerts


# ──────────────────────────────────────────────────
# 4. Alert Source: Cash Management
# ──────────────────────────────────────────────────


def _get_cash_alerts() -> list[dict]:
	"""Cash alerts: variance, unclosed registers, blind count discrepancy."""
	alerts: list[dict] = []
	today_date = today()

	# Large cash variance in today's POS Closings
	if frappe.db.table_exists("POS Closing Entry"):
		variances = frappe.db.sql(
			"""
			SELECT name, pos_period_start_date, pos_period_end_date,
			       grand_closing_amount, grand_opening_amount,
			       (grand_closing_amount - grand_opening_amount) as net_difference
			FROM `tabPOS Closing Entry`
			WHERE docstatus = 1
			  AND pos_period_end_date = %(today)s
			  AND ABS(grand_closing_amount - grand_opening_amount) > 20
			ORDER BY ABS(grand_closing_amount - grand_opening_amount) DESC
			LIMIT 5
		""",
			{"today": today_date},
			as_dict=True,
		)

		for v in variances:
			variance_amt = flt(v.net_difference or 0, 2)
			alerts.append(
				{
					"severity": "critical" if abs(variance_amt) > 50 else "warning",
					"type": "cash_variance",
					"title": f"Cash variance: ${abs(variance_amt):.2f}",
					"message": f"Closing {v.name} has ${abs(variance_amt):.2f} variance",
					"reference_doctype": "POS Closing Entry",
					"reference_name": v.name,
					"timestamp": str(now_datetime()),
				}
			)

	# Stale open POS Opening Entries (>12 hours without closing)
	if frappe.db.table_exists("POS Opening Entry"):
		stale = frappe.db.sql(
			"""
			SELECT name, period_start_date, pos_profile
			FROM `tabPOS Opening Entry`
			WHERE docstatus = 1
			  AND status = 'Open'
			  AND TIMESTAMPDIFF(HOUR, period_start_date, NOW()) > 12
			LIMIT 5
		""",
			as_dict=True,
		)

		for s in stale:
			alerts.append(
				{
					"severity": "warning",
					"type": "stale_register",
					"title": f"Open register: {s.name}",
					"message": "Register has been open for over 12 hours without closing",
					"reference_doctype": "POS Opening Entry",
					"reference_name": s.name,
					"timestamp": str(now_datetime()),
				}
			)

	return alerts


# ──────────────────────────────────────────────────
# 5. Alert Source: Sales Anomalies
# ──────────────────────────────────────────────────


def _get_sales_alerts(is_manager: bool) -> list[dict]:
	"""Sales alerts: unusual transaction patterns, large returns."""
	alerts: list[dict] = []
	today_date = today()

	if not is_manager:
		return alerts

	# Large returns today (credit notes / returns > $200)
	if frappe.db.table_exists("Sales Invoice"):
		large_returns = frappe.db.sql(
			"""
			SELECT name, customer, grand_total, posting_date
			FROM `tabSales Invoice`
			WHERE docstatus = 1
			  AND is_return = 1
			  AND posting_date = %(today)s
			  AND ABS(grand_total) > 200
			ORDER BY ABS(grand_total) DESC
			LIMIT 5
		""",
			{"today": today_date},
			as_dict=True,
		)

		for r in large_returns:
			alerts.append(
				{
					"severity": "warning",
					"type": "large_return",
					"title": f"Large return: ${abs(flt(r.grand_total)):.2f}",
					"message": f"Return {r.name} for {r.customer}",
					"reference_doctype": "Sales Invoice",
					"reference_name": r.name,
					"timestamp": str(now_datetime()),
				}
			)

	# Unusual: No sales today (if it's a business day and past noon)
	if is_manager:
		now = now_datetime()
		weekday = now.weekday()  # 0=Mon, 6=Sun
		if weekday < 6 and now.hour >= 13:  # Past 1 PM on a weekday/Saturday
			today_sales = cint(
				frappe.db.sql(
					"""
				SELECT COUNT(*) FROM `tabSales Invoice`
				WHERE docstatus = 1 AND posting_date = %(today)s AND is_return = 0
			""",
					{"today": today_date},
				)[0][0]
			)

			if today_sales == 0:
				alerts.append(
					{
						"severity": "info",
						"type": "no_sales",
						"title": "No sales today",
						"message": "It's past 1 PM and no sales have been recorded",
						"reference_doctype": None,
						"reference_name": None,
						"timestamp": str(now_datetime()),
					}
				)

	return alerts


# ──────────────────────────────────────────────────
# 6. Real-time Alert Publishing
# ──────────────────────────────────────────────────


def publish_alert(
	alert_type: str,
	severity: str,
	title: str,
	message: str,
	reference_doctype: str | None = None,
	reference_name: str | None = None,
	target_role: str | None = None,
) -> None:
	"""Publish a real-time alert via WebSocket.

	Args:
	    alert_type: Category (e.g., 'cash_variance', 'low_stock')
	    severity: 'critical', 'warning', or 'info'
	    title: Short alert title
	    message: Detailed message
	    reference_doctype: Optional DocType for drill-down
	    reference_name: Optional document name for drill-down
	    target_role: If set, only users with this role see the alert
	"""
	payload = {
		"severity": severity,
		"type": alert_type,
		"title": title,
		"message": message,
		"reference_doctype": reference_doctype,
		"reference_name": reference_name,
		"timestamp": str(now_datetime()),
	}

	if target_role:
		payload["target_role"] = target_role

	frappe.publish_realtime(
		event="zevar_alert",
		message=payload,
		after_commit=True,
	)
