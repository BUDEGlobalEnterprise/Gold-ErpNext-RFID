"""
Zevar Desk Shortcuts API.

Provides endpoints for custom shortcut surfaces, quick stats, and recent activity.
"""

from __future__ import annotations

from collections import OrderedDict
from urllib.parse import quote

import frappe
from frappe import _
from frappe.utils import cint, flt

SHORTCUT_CACHE_KEY = "zevar_shortcuts_registry"
SHORTCUT_FIELDS = [
	"name",
	"shortcut_name",
	"section_name",
	"link_type",
	"link_to",
	"icon_name",
	"custom_icon",
	"color",
	"description",
	"sequence",
	"keyboard_shortcut",
	"open_in_new_tab",
	"show_on_desk",
	"show_on_workspace",
]


@frappe.whitelist()
def get_desk_shortcuts() -> list[dict]:
	"""Backward-compatible desk shortcut endpoint."""
	return get_shortcuts(surface="desk")


@frappe.whitelist()
def get_shortcuts(surface: str = "desk") -> list[dict]:
	"""Return normalized shortcuts for the requested surface."""
	surface = _validate_surface(surface)
	shortcuts = _get_all_shortcuts()
	visible_shortcuts = filter_by_roles(shortcuts)

	return [
		_prepare_shortcut(shortcut)
		for shortcut in visible_shortcuts
		if _is_visible_on_surface(shortcut, surface)
	]


@frappe.whitelist()
def get_shortcut_sections(surface: str = "desk") -> list[dict]:
	"""Return shortcuts grouped by section for the requested surface."""
	sections: OrderedDict[str, dict] = OrderedDict()

	for shortcut in get_shortcuts(surface=surface):
		section_name = shortcut.get("section_name") or "Quick Access"
		section = sections.setdefault(
			section_name,
			{
				"name": section_name,
				"items": [],
			},
		)
		section["items"].append(shortcut)

	return list(sections.values())


@frappe.whitelist()
def get_quick_stats() -> dict:
	"""Get dashboard statistics for the desk."""
	stats = {}
	today = frappe.utils.today()

	try:
		todays_sales = frappe.db.sql(  # nosemgrep
			"""
			SELECT COALESCE(SUM(grand_total), 0)
			FROM `tabSales Invoice`
			WHERE docstatus = 1
			AND posting_date = %s
		""",
			(today,),
		)[0][0]
		stats["todays_sales"] = flt(todays_sales)
	except Exception:
		stats["todays_sales"] = 0

	try:
		pending_repairs = frappe.db.count("Repair Order", {"status": "In Progress"})
		stats["pending_repairs"] = pending_repairs or 0
	except Exception:
		stats["pending_repairs"] = 0

	try:
		active_layaways = frappe.db.count("Layaway Contract", {"status": "Active"})
		stats["active_layaways"] = active_layaways or 0
	except Exception:
		stats["active_layaways"] = 0

	try:
		pending_trade_ins = frappe.db.count("Trade In Record", {"status": "Pending"})
		stats["pending_trade_ins"] = pending_trade_ins or 0
	except Exception:
		stats["pending_trade_ins"] = 0

	try:
		todays_customers = frappe.db.sql(  # nosemgrep
			"""
			SELECT COUNT(DISTINCT customer)
			FROM `tabSales Invoice`
			WHERE docstatus = 1
			AND posting_date = %s
		""",
			(today,),
		)[0][0]
		stats["todays_customers"] = todays_customers or 0
	except Exception:
		stats["todays_customers"] = 0

	return stats


@frappe.whitelist()
def get_recent_activity(limit: int = 10) -> list[dict]:
	"""Get recent activity feed for the desk."""
	limit = cint(limit) or 10
	activities = []

	try:
		recent_invoices = frappe.get_all(
			"Sales Invoice",
			fields=["name", "customer", "grand_total", "modified", "owner"],
			filters={"docstatus": 1, "is_pos": 1},
			order_by="modified desc",
			limit=5,
		)
		for inv in recent_invoices:
			activities.append(
				{
					"type": "invoice",
					"icon": "shopping-cart",
					"message": _("POS Invoice {0} created - ${1:,.2f}").format(
						inv.name, flt(inv.grand_total)
					),
					"time": inv.modified,
					"link": f"/app/sales-invoice/{inv.name}",
				}
			)
	except Exception:
		pass

	try:
		recent_repairs = frappe.get_all(
			"Repair Order",
			fields=["name", "status", "modified", "customer"],
			order_by="modified desc",
			limit=3,
		)
		for repair in recent_repairs:
			status_icon = "check" if repair.status == "Completed" else "tools"
			activities.append(
				{
					"type": "repair",
					"icon": status_icon,
					"message": _("Repair Order {0} - {1}").format(repair.name, repair.status),
					"time": repair.modified,
					"link": f"/app/repair-order/{repair.name}",
				}
			)
	except Exception:
		pass

	try:
		recent_layaways = frappe.get_all(
			"Layaway Contract",
			fields=["name", "status", "modified", "customer"],
			order_by="modified desc",
			limit=3,
		)
		for layaway in recent_layaways:
			activities.append(
				{
					"type": "layaway",
					"icon": "credit-card",
					"message": _("Layaway Contract {0} - {1}").format(layaway.name, layaway.status),
					"time": layaway.modified,
					"link": f"/app/layaway-contract/{layaway.name}",
				}
			)
	except Exception:
		pass

	activities.sort(key=lambda activity: activity.get("time") or "", reverse=True)
	return activities[:limit]


def filter_by_roles(shortcuts: list) -> list:
	"""Filter shortcuts by user roles."""
	user_roles = set(frappe.get_roles())
	filtered = []

	if not shortcuts:
		return []

	shortcut_names = [
		_shortcut_value(shortcut, "name") for shortcut in shortcuts if _shortcut_value(shortcut, "name")
	]
	all_roles = frappe.get_all(
		"Zevar Desk Shortcut Role",
		filters={"parent": ("in", shortcut_names)},
		fields=["parent", "role"],
	)

	role_map = {}
	for role_row in all_roles:
		role_map.setdefault(role_row.parent, []).append(role_row.role)

	for shortcut in shortcuts:
		shortcut_name = _shortcut_value(shortcut, "name")
		shortcut_roles = role_map.get(shortcut_name, [])
		if not shortcut_roles or user_roles & set(shortcut_roles):
			filtered.append(shortcut)

	return filtered


def _validate_surface(surface: str) -> str:
	surface = (surface or "desk").lower().strip()
	if surface not in {"desk", "workspace"}:
		frappe.throw(_("Unsupported shortcut surface: {0}").format(surface))
	return surface


def _get_all_shortcuts() -> list:
	cached = frappe.cache.get_value(SHORTCUT_CACHE_KEY)
	if cached:
		return cached

	shortcuts = frappe.get_all(
		"Zevar Desk Shortcut",
		fields=SHORTCUT_FIELDS,
		order_by="sequence asc, modified asc",
	)
	frappe.cache.set_value(SHORTCUT_CACHE_KEY, shortcuts, expires_in_sec=300)
	return shortcuts


def _is_visible_on_surface(shortcut, surface: str) -> bool:
	if surface == "workspace":
		return cint(_shortcut_value(shortcut, "show_on_workspace")) == 1
	return cint(_shortcut_value(shortcut, "show_on_desk")) == 1


def _prepare_shortcut(shortcut) -> dict:
	link_type = _shortcut_value(shortcut, "link_type")
	link_to = _shortcut_value(shortcut, "link_to")

	return {
		"name": _shortcut_value(shortcut, "name"),
		"shortcut_name": _shortcut_value(shortcut, "shortcut_name"),
		"section_name": _shortcut_value(shortcut, "section_name") or "Quick Access",
		"link_type": link_type,
		"link_to": link_to,
		"route": _build_route(link_type, link_to),
		"icon_name": _shortcut_value(shortcut, "icon_name"),
		"custom_icon": _shortcut_value(shortcut, "custom_icon"),
		"color": _shortcut_value(shortcut, "color") or "#2563eb",
		"description": _shortcut_value(shortcut, "description") or "",
		"sequence": cint(_shortcut_value(shortcut, "sequence") or 0),
		"keyboard_shortcut": _shortcut_value(shortcut, "keyboard_shortcut") or "",
		"open_in_new_tab": cint(_shortcut_value(shortcut, "open_in_new_tab") or 0),
	}


def _build_route(link_type: str | None, link_to: str | None) -> str:
	if not link_to:
		return "#"
	if link_type == "DocType":
		return f"/app/{frappe.scrub(link_to).replace('_', '-')}"
	if link_type == "Page":
		return f"/app/{frappe.scrub(link_to).replace('_', '-')}"
	if link_type == "Report":
		return f"/app/query-report/{quote(link_to, safe='')}"
	return link_to


def _shortcut_value(shortcut, key: str):
	if isinstance(shortcut, dict):
		return shortcut.get(key)
	return getattr(shortcut, key, None)
