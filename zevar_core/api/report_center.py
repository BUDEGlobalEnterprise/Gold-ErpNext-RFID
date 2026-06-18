"""
Report Center — the four "Command Center" aggregators behind the Reports suite.

Each whitelisted endpoint is a thin, cached, fault-tolerant orchestrator that
*composes* the existing, already-validated methods in ``sales_monitor``,
``profit_intelligence`` and ``workforce`` rather than re-querying the DB. This
keeps a single source of truth for every metric and avoids the SQL-injection /
drift that private copy-paste helpers introduced.

Contract notes (consumed by ``pages/reports/*.vue`` via ``useReportData``):
  - all endpoints take ``start_date`` / ``end_date`` / ``store`` (all optional,
    defaulting to today / all-stores) and return a single dict with ``as_of``.
  - a sub-query failure degrades to an empty widget (``_safe``) and never 500s.
  - payloads are Redis-cached with a volatility-tiered TTL; the live ``pace``
    feed is always recomputed so the Sales Monitor pulse stays fresh.
"""

import frappe
from frappe.utils import add_days, date_diff, flt, getdate, today

from zevar_core.api.reports import (
	ACCOUNTING_ROLES,
	ADMIN_ROLES,
	EMPLOYEE_ROLES,
	HR_ROLES,
	MANAGER_ROLES,
	SALES_ROLES,
)
from zevar_core.api.profit_intelligence import (
	get_margin_analysis as pi_get_margin_analysis,
	get_margin_waterfall as pi_get_margin_waterfall,
	get_payment_method_breakdown as pi_get_payment_methods,
	get_profit_summary as pi_get_profit_summary,
)
from zevar_core.api.sales_monitor import (
	get_breakdown as sm_get_breakdown,
	get_hourly as sm_get_hourly,
	get_leaderboard as sm_get_leaderboard,
	get_pace as sm_get_pace,
	get_summary as sm_get_summary,
	get_top_bottom_items as sm_get_top_bottom,
	get_trend as sm_get_trend,
)
from zevar_core.api.workforce import get_staffing_heatmap as wf_get_staffing_heatmap

# Executive Overview / Sales Monitor — anyone who can open the Reports suite.
_MONITOR_ROLES = list(
	ADMIN_ROLES | MANAGER_ROLES | ACCOUNTING_ROLES | HR_ROLES | SALES_ROLES | EMPLOYEE_ROLES
)
# Profit Intelligence — admin/Accounts only (Store Manager restricted per PRD §7 / D2).
_PROFIT_ROLES = ["System Manager", "Accounts Manager", "Administrator"]
# Workforce Intelligence — managers + HR + admin.
_WORKFORCE_ROLES = list(ADMIN_ROLES | MANAGER_ROLES | HR_ROLES)


# ---------------------------------------------------------------------------
# Primitives
# ---------------------------------------------------------------------------


def _safe(fn, *args, **kwargs):
	"""Run ``fn``; log + swallow any error so one widget can't break the payload."""
	try:
		return fn(*args, **kwargs)
	except Exception:
		frappe.log_error(title="Report Center safe-exec failed")
		return {}


def _cache_get_set(key, ttl, fn):
	"""Redis get-then-set with a TTL (mirrors analytics_hub.get_hub_data)."""
	cached = frappe.cache().get_value(key)
	if cached is not None:
		return cached
	val = fn()
	frappe.cache().set_value(key, val, expires_in_sec=ttl)
	return val


def _previous_range(from_date, to_date):
	"""Same-length period immediately before ``from_date..to_date``."""
	f = getdate(from_date)
	t = getdate(to_date)
	diff = date_diff(t, f) + 1
	return add_days(f, -diff), add_days(t, -diff)


def _period_margin_pct(from_date, to_date):
	"""Aggregate gross-margin % straight from Sale Cost Breakdown (parameterized).

	Computed directly (rather than via the role-gated ``get_profit_summary``) so
	the Executive Overview's hero metric renders for Store Managers too — the
	PRD restricts Store Manager from the *Profit tab*, not from this one
	overview number.
	"""
	row = frappe.db.sql(
		"""
		SELECT COALESCE(SUM(gross_profit), 0) AS gross_profit,
		       COALESCE(SUM(total_revenue), 0) AS revenue
		FROM `tabSale Cost Breakdown`
		WHERE posting_date >= %(from)s AND posting_date <= %(to)s
		""",
		{"from": from_date, "to": to_date},
		as_dict=True,
	)[0]
	revenue = flt(row.revenue)
	gp = flt(row.gross_profit)
	return flt((gp / revenue * 100) if revenue else 0, 2)


def _can_see_margin():
	"""Profit margin is admin/Accounts-only (mirrors profit_intelligence's D2 gating)."""
	if frappe.session.user == "Administrator":
		return True
	return bool(set(frappe.get_roles()) & {"System Manager", "Accounts Manager"})


def _leakage(from_date, to_date, store=None):
	"""Revenue lost to discounts, voids (docstatus=2) and returns (is_return=1)."""
	store_cond = "AND set_warehouse = %(store)s" if store else ""
	params = {"from": from_date, "to": to_date}
	if store:
		params["store"] = store

	def _sum(where_extra):
		return flt(
			frappe.db.sql(
				f"""
				SELECT COALESCE(SUM(base_grand_total), 0)
				FROM `tabSales Invoice`
				WHERE is_pos = 1 AND {where_extra}
				  AND posting_date >= %(from)s AND posting_date <= %(to)s
				  {store_cond}
				""",
				params,
			)[0][0],
			2,
		)

	return {
		"discounts": _sum("docstatus = 1"),
		"voids": _sum("docstatus = 2"),
		"returns": _sum("docstatus = 1 AND is_return = 1"),
	}


def _waterfall(from_date, to_date, store=None):
	"""Reuse ``get_margin_waterfall`` for the Revenue → Net Profit steps."""
	# Keyword args: get_margin_waterfall's signature is (sales_invoice, from_date, to_date),
	# so a positional call would route `from_date` into the single-invoice branch.
	wf = pi_get_margin_waterfall(from_date=from_date, to_date=to_date) or {}
	leakage = _leakage(from_date, to_date, store) or {}
	return {
		"revenue": flt(wf.get("revenue"), 2),
		"cogs": flt(wf.get("total_cost"), 2),
		"discounts": flt(leakage.get("discounts"), 2),
		"net_profit": flt(wf.get("gross_profit"), 2),
		"steps": wf.get("steps") or [],
	}


# ---------------------------------------------------------------------------
# Aggregators
# ---------------------------------------------------------------------------


@frappe.whitelist()
def get_executive_overview(start_date=None, end_date=None, store=None):
	"""Hero KPIs (GTV, Net Sales, Txns, Gross Margin %) with prior-period compare."""
	frappe.only_for(_MONITOR_ROLES)
	if not start_date:
		start_date = today()
	if not end_date:
		end_date = today()

	def fetch():
		sales = _safe(sm_get_summary, start_date, end_date, store) or {}
		trend = _safe(sm_get_trend, start_date, end_date, store) or []
		margin_pct = _safe(_period_margin_pct, start_date, end_date)

		prev_start, prev_end = _previous_range(start_date, end_date)
		prev_sales = _safe(sm_get_summary, str(prev_start), str(prev_end), store) or {}

		return {
			"gtv": flt(sales.get("grand_total"), 2),
			"net_sales": flt(sales.get("revenue"), 2),
			"txn_count": sales.get("txn_count") or 0,
			"gross_profit_margin_pct": flt(margin_pct, 2) if isinstance(margin_pct, (int, float)) else 0,
			"can_see_margin": True,
			"trend": trend,
			"previous_period": {
				"gtv": flt(prev_sales.get("grand_total"), 2),
				"net_sales": flt(prev_sales.get("revenue"), 2),
				"txn_count": prev_sales.get("txn_count") or 0,
			},
			"period": f"{start_date} to {end_date}",
			"as_of": frappe.utils.now(),
		}

	ttl = 120 if end_date == today() else (1800 if date_diff(today(), start_date) > 90 else 300)
	key = f"report_overview:{store or 'all'}:{start_date}:{end_date}"
	payload = _cache_get_set(key, ttl, fetch)
	# Margin is admin/Accounts-only (D2). Redact per-request so the shared,
	# role-agnostic cache key never leaks margin to a Store Manager.
	if not _can_see_margin():
		payload = dict(payload)
		payload["gross_profit_margin_pct"] = None
		payload["can_see_margin"] = False
	return payload


@frappe.whitelist()
def get_sales_monitor_data(start_date=None, end_date=None, store=None):
	"""Hourly sales, category split, top items, dead stock + a live pace pulse."""
	frappe.only_for(_MONITOR_ROLES)
	if not start_date:
		start_date = today()
	if not end_date:
		end_date = today()

	def fetch():
		top_bottom = _safe(sm_get_top_bottom, start_date, end_date, store, 5) or {}
		return {
			"hourly": _safe(sm_get_hourly, start_date, end_date, store) or [],
			"breakdown": _safe(sm_get_breakdown, start_date, end_date, store, "category") or [],
			"top_items": top_bottom.get("top") or [],
			"dead_stock": top_bottom.get("bottom") or [],
			"as_of": frappe.utils.now(),
		}

	ttl = 120 if end_date == today() else 300
	key = f"report_sales:{store or 'all'}:{start_date}:{end_date}"
	# Charts/tables are cached; pace is always fresh so the pulse stays live.
	data = _cache_get_set(key, ttl, fetch)
	data["pace"] = _safe(sm_get_pace, start_date, end_date, store) or {}
	return data


@frappe.whitelist()
def get_profit_intelligence_data(start_date=None, end_date=None, store=None):
	"""Summary, margin analysis, waterfall, payment mix, leakage (admin/Accounts)."""
	frappe.only_for(_PROFIT_ROLES)
	if not start_date:
		start_date = today()
	if not end_date:
		end_date = today()

	def fetch():
		payments = _safe(pi_get_payment_methods, start_date, end_date) or []
		return {
			"summary": _safe(pi_get_profit_summary, start_date, end_date) or {},
			"analysis": _safe(pi_get_margin_analysis, start_date, end_date, "jewelry_type")
			or {"data": []},
			"waterfall": _safe(_waterfall, start_date, end_date, store) or {},
			"payment_split": [
				{
					"mode_of_payment": (p.get("method") or p.get("mode_of_payment") or "Other"),
					"amount": flt(p.get("total") or p.get("amount") or 0, 2),
				}
				for p in (payments or [])
			],
			"leakage": _safe(_leakage, start_date, end_date, store) or {},
			"as_of": frappe.utils.now(),
		}

	ttl = 1800 if date_diff(today(), start_date) > 90 else 300
	key = f"report_profit:{store or 'all'}:{start_date}:{end_date}"
	return _cache_get_set(key, ttl, fetch)


@frappe.whitelist()
def get_workforce_data(start_date=None, end_date=None, store=None):
	"""Associate leaderboard (with ATV) + sales-vs-staffing series."""
	frappe.only_for(_WORKFORCE_ROLES)
	if not start_date:
		start_date = today()
	if not end_date:
		end_date = today()

	def fetch():
		leaderboard = _safe(sm_get_leaderboard, start_date, end_date, store) or []
		for row in leaderboard:
			txn = row.get("txn_count") or 0
			row["atv"] = flt((row.get("revenue") or 0) / txn, 2) if txn else 0
		return {
			"leaderboard": leaderboard,
			"heatmap": _safe(wf_get_staffing_heatmap, start_date, end_date, store) or [],
			"as_of": frappe.utils.now(),
		}

	key = f"report_workforce:{store or 'all'}:{start_date}:{end_date}"
	return _cache_get_set(key, 300, fetch)


# ---------------------------------------------------------------------------
# Cache invalidation (Sales Invoice on_submit / on_cancel hook)
# ---------------------------------------------------------------------------


def _invalidate_report_cache(doc, method=None):
	"""Clear all cached report payloads when a Sales Invoice changes.

	Broad by design: any submit/cancel can move every period that includes that
	date, so we drop the four report prefixes and let the next read recompute.
	"""
	for prefix in ("report_overview", "report_sales", "report_profit", "report_workforce"):
		try:
			frappe.cache().delete_keys(prefix)
		except Exception:
			frappe.log_error(title="Report cache invalidation failed")
