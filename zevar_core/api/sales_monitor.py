"""
Sales Monitor API — live sales KPIs for the command center (Quick-Win Q7 + Q8).

This is a *lean* version of the Phase 2 sales spine: enough to put live sales on
the wall (Q7) and surface the zero-cost KPIs the data already supports - UPT,
run-rate, projected-day-close (Q8). Phase 2 will refactor the 5 duplicate
"today's sales" queries across revenue_dashboard / reports / analytics_hub to
delegate here.

All queries read submitted (docstatus=1) POS Sales Invoices.
"""

from __future__ import annotations

from typing import Any

import frappe
from frappe import _
from frappe.utils import add_days, flt, get_datetime, now_datetime, today

_MONITOR_ROLES = ["System Manager", "Store Manager", "Sales Manager", "Accounts Manager"]


def _date_range(from_date: str | None, to_date: str | None) -> tuple[str, str]:
	if not from_date:
		from_date = today()
	if not to_date:
		to_date = today()
	return from_date, to_date


def _store_condition(store: str | None) -> tuple[str, dict]:
	"""Return (sql_fragment, params) for the optional store filter.

	POS invoices carry the store on ``set_warehouse``; line items also carry a
	per-row ``warehouse``. Filter on set_warehouse (the header store).
	"""
	if store:
		return "AND set_warehouse = %(store)s", {"store": store}
	return "", {}


@frappe.whitelist()
def get_summary(from_date: str | None = None, to_date: str | None = None, store: str | None = None) -> dict[str, Any]:
	"""Today (or a range) sales summary with zero-cost KPIs.

	Returns: revenue (net), grand_total, txn_count, units, aov, upt,
	run_rate, projected_day_close (the latter two only for a single-day
	'today' range).
	"""
	frappe.only_for(_MONITOR_ROLES)
	from_date, to_date = _date_range(from_date, to_date)

	store_cond, store_params = _store_condition(store)

	header = frappe.db.sql(
		f"""
        SELECT COUNT(*) AS txn_count,
               COALESCE(SUM(base_net_total), 0) AS revenue,
               COALESCE(SUM(base_grand_total), 0) AS grand_total
        FROM `tabSales Invoice`
        WHERE is_pos = 1 AND docstatus = 1
          AND posting_date >= %(from)s AND posting_date <= %(to)s
          {store_cond}
        """,
		{"from": from_date, "to": to_date, **store_params},
		as_dict=True,
	)[0]

	units_row = frappe.db.sql(
		f"""
        SELECT COALESCE(SUM(sii.qty), 0) AS units,
               COUNT(DISTINCT si.name) AS line_invoice_count
        FROM `tabSales Invoice Item` sii
        JOIN `tabSales Invoice` si ON sii.parent = si.name
        WHERE si.is_pos = 1 AND si.docstatus = 1
          AND si.posting_date >= %(from)s AND si.posting_date <= %(to)s
          {store_cond}
        """,
		{"from": from_date, "to": to_date, **store_params},
		as_dict=True,
	)[0]

	txn_count = int(header.txn_count or 0)
	revenue = flt(header.revenue, 2)
	units = flt(units_row.units, 0)
	aov = flt(revenue / txn_count, 2) if txn_count else 0.0
	upt = flt(units / txn_count, 3) if txn_count else 0.0  # units per transaction

	run_rate = None
	projected_day_close = None
	# Run-rate only makes sense for "today so far".
	if from_date == to_date == today():
		elapsed = (now_datetime() - get_datetime(f"{from_date} 00:00:00")).total_seconds()
		day_seconds = 24 * 3600
		if elapsed > 0:
			fraction = min(elapsed / day_seconds, 1.0)
			if fraction > 0:
				run_rate = flt(revenue / fraction, 2)
				projected_day_close = run_rate

	return {
		"from_date": from_date,
		"to_date": to_date,
		"store": store,
		"revenue": revenue,
		"grand_total": flt(header.grand_total, 2),
		"txn_count": txn_count,
		"units": int(units),
		"aov": aov,
		"upt": upt,
		"run_rate": run_rate,
		"projected_day_close": projected_day_close,
	}


@frappe.whitelist()
def get_hourly(from_date: str | None = None, to_date: str | None = None, store: str | None = None) -> list[dict]:
	"""Full 24-hour, zero-bucketed revenue/count series for the live ticker."""
	frappe.only_for(_MONITOR_ROLES)
	from_date, to_date = _date_range(from_date, to_date)
	store_cond, store_params = _store_condition(store)

	rows = frappe.db.sql(
		f"""
        SELECT HOUR(creation) AS hour,
               COUNT(*) AS count,
               COALESCE(SUM(base_net_total), 0) AS revenue
        FROM `tabSales Invoice`
        WHERE is_pos = 1 AND docstatus = 1
          AND posting_date >= %(from)s AND posting_date <= %(to)s
          {store_cond}
        GROUP BY HOUR(creation)
        """,
		{"from": from_date, "to": to_date, **store_params},
		as_dict=True,
	)
	by_hour = {int(r["hour"]): r for r in rows}
	return [
		{"hour": h, "count": int(by_hour[h]["count"]) if h in by_hour else 0, "revenue": flt(by_hour[h]["revenue"], 2) if h in by_hour else 0.0}
		for h in range(24)
	]


# ---------------------------------------------------------------------------
# Phase 2 — leaderboard / breakdown / trend / pace
# ---------------------------------------------------------------------------


@frappe.whitelist()
def get_leaderboard(from_date: str | None = None, to_date: str | None = None, store: str | None = None) -> list[dict]:
	"""Per-associate leaderboard from Performance Log 'Sale Completed' events:
	revenue, txn_count, units, UPT, commission.
	"""
	frappe.only_for(_MONITOR_ROLES)
	from_date, to_date = _date_range(from_date, to_date)

	filters = {
		"event_type": "Sale Completed",
		"event_date": ["between", [from_date, to_date]],
	}
	if store:
		filters["store_location"] = store

	rows = frappe.db.sql(
		"""
        SELECT employee, employee_name,
               COUNT(*) AS txn_count,
               COALESCE(SUM(revenue_amount), 0) AS revenue,
               COALESCE(SUM(item_count), 0) AS units,
               COALESCE(SUM(commission_amount), 0) AS commission
        FROM `tabPerformance Log`
        WHERE event_type = 'Sale Completed'
          AND event_date >= %(from)s AND event_date <= %(to)s
          {store_cond}
        GROUP BY employee
        ORDER BY revenue DESC
        """.replace("{store_cond}", "AND store_location = %(store)s" if store else ""),
		{"from": from_date, "to": to_date, **({"store": store} if store else {})},
		as_dict=True,
	)

	out = []
	for r in rows:
		txn = int(r.txn_count or 0)
		out.append(
			{
				"employee": r.employee,
				"employee_name": r.employee_name,
				"revenue": flt(r.revenue, 2),
				"txn_count": txn,
				"units": int(r.units or 0),
				"upt": flt((r.units or 0) / txn, 3) if txn else 0.0,
				"commission": flt(r.commission, 2),
			}
		)
	return out


@frappe.whitelist()
def get_breakdown(
	from_date: str | None = None,
	to_date: str | None = None,
	store: str | None = None,
	dimension: str = "category",
) -> list[dict]:
	"""Revenue/units by dimension: category | metal | item_group | salesperson."""
	frappe.only_for(_MONITOR_ROLES)
	from_date, to_date = _date_range(from_date, to_date)
	store_cond, store_params = _store_condition(store)

	dim_column = {
		"category": "i.custom_jewelry_type",
		"metal": "i.custom_metal_type",
		"item_group": "i.item_group",
	}.get(dimension)

	if dim_column:
		rows = frappe.db.sql(
			f"""
            SELECT {dim_column} AS dim,
                   COALESCE(SUM(sii.amount), 0) AS revenue,
                   COALESCE(SUM(sii.qty), 0) AS units,
                   COUNT(*) AS line_count
            FROM `tabSales Invoice` si
            JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
            JOIN `tabItem` i ON i.name = sii.item_code
            WHERE si.is_pos = 1 AND si.docstatus = 1
              AND si.posting_date >= %(from)s AND si.posting_date <= %(to)s
              {store_cond}
            GROUP BY {dim_column}
            ORDER BY revenue DESC
            """,
			{"from": from_date, "to": to_date, **store_params},
			as_dict=True,
		)
		return [
			{"dimension": r.dim or "Unknown", "revenue": flt(r.revenue, 2), "units": int(r.units or 0)}
			for r in rows
		]

	if dimension == "salesperson":
		rows = frappe.db.sql(
			f"""
            SELECT ss.employee AS dim,
                   COALESCE(SUM(si.base_net_total * ss.split_percent / 100), 0) AS revenue,
                   COUNT(DISTINCT si.name) AS txn_count
            FROM `tabSales Invoice` si
            JOIN `tabSalesperson Split Detail` ss ON ss.parent = si.name AND ss.parenttype = 'Sales Invoice'
            WHERE si.is_pos = 1 AND si.docstatus = 1
              AND si.posting_date >= %(from)s AND si.posting_date <= %(to)s
              {store_cond}
            GROUP BY ss.employee
            ORDER BY revenue DESC
            """,
			{"from": from_date, "to": to_date, **store_params},
			as_dict=True,
		)
		return [
			{
				"dimension": r.dim,
				"dimension_name": frappe.db.get_value("Employee", r.dim, "employee_name") if r.dim else "Unknown",
				"revenue": flt(r.revenue, 2),
				"txn_count": int(r.txn_count or 0),
			}
			for r in rows
		]

	frappe.throw(_("Unknown dimension {0}. Use category, metal, item_group, or salesperson.").format(dimension))


@frappe.whitelist()
def get_trend(
	from_date: str | None = None,
	to_date: str | None = None,
	store: str | None = None,
	metric: str = "revenue",
) -> list[dict]:
	"""Daily series of {date, revenue, txn_count, units} for trend lines."""
	frappe.only_for(_MONITOR_ROLES)
	from_date, to_date = _date_range(from_date, to_date)
	store_cond, store_params = _store_condition(store)

	rows = frappe.db.sql(
		f"""
        SELECT si.posting_date AS date,
               COALESCE(SUM(si.base_net_total), 0) AS revenue,
               COUNT(*) AS txn_count,
               COALESCE(SUM(sii.qty), 0) AS units
        FROM `tabSales Invoice` si
        LEFT JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
        WHERE si.is_pos = 1 AND si.docstatus = 1
          AND si.posting_date >= %(from)s AND si.posting_date <= %(to)s
          {store_cond}
        GROUP BY si.posting_date
        ORDER BY si.posting_date
        """,
		{"from": from_date, "to": to_date, **store_params},
		as_dict=True,
	)
	return [
		{
			"date": str(r.date),
			"revenue": flt(r.revenue, 2),
			"txn_count": int(r.txn_count or 0),
			"units": int(r.units or 0),
		}
		for r in rows
	]


@frappe.whitelist()
def get_pace(from_date: str | None = None, to_date: str | None = None, store: str | None = None) -> dict:
	"""Pace-to-target: today's run-rate projection + attainment vs Sales Target (if any)."""
	frappe.only_for(_MONITOR_ROLES)
	summary = get_summary(from_date, to_date, store)

	target = None
	attainment_pct = None
	if frappe.db.exists("DocType", "Sales Target"):
		# One row per store/period; sum any covering the range.
		t = frappe.db.sql(
			"""SELECT COALESCE(SUM(target_revenue), 0) AS target
            FROM `tabSales Target`
            WHERE period_start <= %(to)s AND period_end >= %(from)s
              AND (%(store)s = '' OR store = %(store)s OR store IS NULL)""",
			{"from": summary["from_date"], "to": summary["to_date"], "store": store or ""},
		)[0][0]
		target = flt(t)
		if target > 0:
			attainment_pct = flt(summary["revenue"] / target * 100, 1)

	return {
		"revenue_so_far": summary["revenue"],
		"run_rate": summary["run_rate"],
		"projected_day_close": summary["projected_day_close"],
		"target_revenue": target,
		"attainment_pct": attainment_pct,
		"upt": summary["upt"],
		"aov": summary["aov"],
	}


# ---------------------------------------------------------------------------
# Phase 0 — Daily Store Sales Rollup (materialized for sub-100ms reads)
# ---------------------------------------------------------------------------


@frappe.whitelist()
def rebuild_daily_rollup(from_date: str | None = None, to_date: str | None = None) -> dict:
	"""Idempotent batch rebuild of the Daily Store Sales Rollup for a range.

	One row per (date x store x category x metal). Revenue is summed per line;
	COGS/gross_profit are the SCB's values allocated to each line by its revenue
	share (same basis as top_profitability_by_product). Delete-then-insert over
	the range, so it is safe to re-run. Scheduled nightly; also runnable by hand.
	"""
	frappe.only_for(["System Manager"])
	if not from_date:
		from_date = add_days(today(), -90)
	if not to_date:
		to_date = today()

	frappe.db.delete("Daily Store Sales Rollup", {"date": ["between", [from_date, to_date]]})

	rows = frappe.db.sql(
		"""
        SELECT
            si.posting_date AS date,
            si.set_warehouse AS store,
            i.custom_jewelry_type AS category,
            i.custom_metal_type AS metal,
            COUNT(DISTINCT si.name) AS invoice_count,
            COALESCE(SUM(sii.qty), 0) AS unit_count,
            COALESCE(SUM(sii.amount), 0) AS net_revenue,
            COALESCE(SUM(sii.amount), 0) AS gross_revenue,
            COALESCE(SUM(CASE WHEN si.base_net_total > 0
                THEN scb.total_cost * (sii.amount / si.base_net_total) ELSE 0 END), 0) AS cogs_total,
            COALESCE(SUM(CASE WHEN si.base_net_total > 0
                THEN scb.gross_profit * (sii.amount / si.base_net_total) ELSE 0 END), 0) AS gross_profit,
            AVG(scb.gold_rate_at_sale) AS gold_rate_avg
        FROM `tabSales Invoice` si
        LEFT JOIN `tabSale Cost Breakdown` scb ON scb.sales_invoice = si.name
        JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
        JOIN `tabItem` i ON i.name = sii.item_code
        WHERE si.is_pos = 1 AND si.docstatus = 1
          AND si.posting_date >= %s AND si.posting_date <= %s
        GROUP BY si.posting_date, si.set_warehouse, i.custom_jewelry_type, i.custom_metal_type
        """,
		(from_date, to_date),
		as_dict=True,
	)

	for r in rows:
		doc = frappe.new_doc("Daily Store Sales Rollup")
		doc.date = r.date
		doc.store = r.store
		doc.category = r.category
		doc.metal = r.metal
		doc.invoice_count = int(r.invoice_count or 0)
		doc.unit_count = int(r.unit_count or 0)
		doc.net_revenue = flt(r.net_revenue, 2)
		doc.gross_revenue = flt(r.gross_revenue, 2)
		doc.cogs_total = flt(r.cogs_total, 2)
		doc.gross_profit = flt(r.gross_profit, 2)
		doc.gold_rate_avg = flt(r.gold_rate_avg, 2) or 0
		doc.insert(ignore_permissions=True)

	frappe.db.commit()
	return {"rebuilt": len(rows), "from_date": from_date, "to_date": to_date}


