"""
Command Center API (Phase 4) — the role-aware ops wall.

Composition layer: the pieces already live in their own modules (live_monitor
for stores/alerts/health + the realtime bus, sales_monitor for live sales,
workforce for the associate grid). This module hydrates the whole wall from one
call and exposes thin ticker/grid/lane accessors the frontend can poll.

The ack/snooze/resolve alert lifecycle and the Operations Alert doctype are
deferred (need migrate); for now alerts come read-only from the anomaly engine.
"""

from __future__ import annotations

import frappe
from frappe.utils import now_datetime, today

from zevar_core.api.live_monitor import get_command_center_data, get_repair_live_feed
from zevar_core.api.sales_monitor import get_hourly, get_summary
from zevar_core.api.workforce import get_team_scorecard

_CC_ROLES = ["System Manager", "Store Manager", "Sales Manager", "Accounts Manager"]


@frappe.whitelist()
def get_wall_state(store: str | None = None) -> dict:
	"""One-call wall hydrator: stores + system KPIs + alerts + live sales + associates."""
	frappe.only_for(_CC_ROLES)
	cc = get_command_center_data()  # stores, system, alerts (incl. per-store sales_today)
	return {
		"timestamp": str(now_datetime()),
		"stores": cc.get("stores", []),
		"system": cc.get("system", {}),
		"alerts": cc.get("alerts", []),
		"sales_today": get_summary(today(), today(), store),
		"associates": get_team_scorecard(store),
	}


@frappe.whitelist()
def get_sales_ticker(store: str | None = None) -> list[dict]:
	"""24-hour zero-bucketed sales series for the ticker."""
	frappe.only_for(_CC_ROLES)
	return get_hourly(today(), today(), store)


@frappe.whitelist()
def get_associate_grid(store: str | None = None, date: str | None = None) -> list[dict]:
	"""Ranked associate scoreboard for the wall grid."""
	frappe.only_for(_CC_ROLES)
	return get_team_scorecard(store, date or today())


@frappe.whitelist()
def get_repair_lane(hours: int = 4) -> list[dict]:
	"""Recent repair status changes for the repair lane tile."""
	frappe.only_for(_CC_ROLES)
	return get_repair_live_feed(hours)
