"""
Workforce Intelligence API (Phase 3).

Complements ``performance.py`` (which owns the scoreboard, the compensation
engine, and quarterly reviews) with quota-progress, payout projection, and a
team scorecard. Every endpoint here is a **read-only projection** — none of them
runs the compensation calculation. The actual comp run stays behind
``performance.run_compensation_calculation`` until Phase 0/3 ship and history is
reconciled (the payroll guardrail).
"""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import flt, getdate, today

from zevar_core.api.performance import (
	_get_active_target,
	get_employee_performance_summary,
	get_team_performance,
)

_WF_ROLES = ["System Manager", "HR Manager", "Store Manager", "Sales Manager"]


def _period_fraction(period_start: str, period_end: str) -> tuple[float, int, int]:
	"""Return (elapsed_fraction, elapsed_days, total_days) for a period vs today."""
	ps = getdate(period_start)
	pe = getdate(period_end)
	now = getdate(today())
	total_days = max((pe - ps).days + 1, 1)
	elapsed_days = max(min((now - ps).days + 1, total_days), 0)
	return (elapsed_days / total_days, elapsed_days, total_days)


@frappe.whitelist(methods=["GET"])
def get_quota_progress(employee: str, period_start: str | None = None, period_end: str | None = None) -> dict:
	"""An associate's revenue vs quota with a pace projection to period end."""
	frappe.only_for(_WF_ROLES + ["HR User"])

	summary = get_employee_performance_summary(employee, period_start, period_end)
	target = summary.get("target") or {}
	revenue_target = flt(target.get("revenue_target"))
	revenue = flt(summary.get("total_revenue"))

	attainment = (revenue / revenue_target * 100) if revenue_target else None
	fraction, elapsed_days, total_days = _period_fraction(summary["period_start"], summary["period_end"])
	projected_revenue = (revenue / fraction) if fraction else revenue
	projected_attainment = (projected_revenue / revenue_target * 100) if revenue_target else None

	return {
		"employee": employee,
		"employee_name": summary.get("employee_name"),
		"revenue": revenue,
		"revenue_target": revenue_target,
		"attainment_pct": flt(attainment, 1) if attainment is not None else None,
		"projected_revenue": flt(projected_revenue, 2),
		"projected_attainment_pct": flt(projected_attainment, 1) if projected_attainment is not None else None,
		"period_start": summary["period_start"],
		"period_end": summary["period_end"],
		"days_elapsed": elapsed_days,
		"days_total": total_days,
	}


@frappe.whitelist(methods=["GET"])
def project_payout(employee: str, period_start: str | None = None, period_end: str | None = None) -> dict:
	"""READ-ONLY projected commission for the period.

	Derives the effective commission rate from actual Performance Log
	(commission / revenue so far), falling back to the employee's flat-rate rule,
	and projects to period end at the current pace. Does NOT call the comp engine.
	"""
	frappe.only_for(_WF_ROLES + ["HR User"])

	summary = get_employee_performance_summary(employee, period_start, period_end)
	revenue = flt(summary.get("total_revenue"))
	commission_so_far = flt(summary.get("total_commission"))

	effective_rate = (commission_so_far / revenue * 100) if revenue > 0 else None
	if effective_rate is None:
		from zevar_core.api.commission import _get_applicable_rule

		rule = _get_applicable_rule(employee)
		effective_rate = flt(rule.flat_rate) if (rule and rule.calculation_type == "Flat Rate") else 0.0

	fraction, _elapsed, _total = _period_fraction(summary["period_start"], summary["period_end"])
	projected_revenue = (revenue / fraction) if fraction else revenue
	projected_commission = projected_revenue * flt(effective_rate) / 100

	return {
		"employee": employee,
		"employee_name": summary.get("employee_name"),
		"revenue_so_far": revenue,
		"commission_so_far": commission_so_far,
		"effective_rate_pct": flt(effective_rate, 2),
		"projected_revenue": flt(projected_revenue, 2),
		"projected_commission": flt(projected_commission, 2),
		"period_start": summary["period_start"],
		"period_end": summary["period_end"],
	}


@frappe.whitelist(methods=["GET"])
def get_team_scorecard(store_location: str | None = None, date: str | None = None) -> list[dict]:
	"""Team scoreboard with quota-attainment bars + UPT, ranked by revenue.

	Thin layer over ``performance.get_team_performance`` (which reads the
	canonical Performance Log) that flattens the shape for the team console.
	"""
	frappe.only_for(_WF_ROLES)

	rows = get_team_performance(store_location, date)
	out = []
	for r in rows:
		revenue = flt(r.get("total_revenue"))
		target = flt((r.get("target") or {}).get("revenue_target"))
		txn = int(r.get("total_transactions") or 0)
		items = int(r.get("total_items") or 0)
		out.append(
			{
				"employee": r.get("employee"),
				"employee_name": r.get("employee_name"),
				"revenue": revenue,
				"target": target,
				"attainment_pct": flt((revenue / target * 100) if target else 0, 1),
				"transactions": txn,
				"upt": flt((items / txn) if txn else 0, 2),
				"commission": flt(r.get("total_commission"), 2),
			}
		)
	out.sort(key=lambda x: x["revenue"], reverse=True)
	return out
