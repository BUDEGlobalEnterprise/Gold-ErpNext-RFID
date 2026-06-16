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
from frappe.utils import flt, get_datetime, now_datetime, today

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
