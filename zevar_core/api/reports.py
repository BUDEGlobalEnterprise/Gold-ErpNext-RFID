"""Role-aware POS report catalog.

Provides the frontend with a filtered list of available reports based on the
logged-in user's roles, along with role-safe default filters and quick summary
stats for the Reports hub page.

Server-side enforcement note:
  The catalog controls *visibility* on the frontend.  Each linked Frappe Report
  or POS API must independently verify roles via ``frappe.has_permission()`` or
  explicit role checks before returning data.
"""

from __future__ import annotations

from typing import Any

import frappe
from frappe.utils import getdate, nowdate

# ---------------------------------------------------------------------------
# Role constants – every report references one of these sets
# ---------------------------------------------------------------------------

ADMIN_ROLES = {"Administrator", "System Manager"}
MANAGER_ROLES = {"Store Manager", "Sales Manager", "System Manager"}
SALES_ROLES = {"Sales User", "Store Manager", "Sales Manager", "System Manager"}
ACCOUNTING_ROLES = {
	"Accounts Manager",
	"Store Manager",
	"Sales Manager",
	"System Manager",
}
STOCK_ROLES = {
	"Stock Manager",
	"Inventory Manager",
	"Store Manager",
	"Sales Manager",
	"System Manager",
}
HR_ROLES = {"HR User", "HR Manager", "System Manager"}
EMPLOYEE_ROLES = {"Employee", "Employee Self Service"}

# ---------------------------------------------------------------------------
# Report groups (tabs on the Reports hub)
# ---------------------------------------------------------------------------

REPORT_GROUPS = [
	{"id": "daily_closeout", "label": "Daily Closeout", "icon": "point_of_sale"},
	{"id": "sales", "label": "Sales Performance", "icon": "monitoring"},
	{"id": "inventory", "label": "Inventory", "icon": "inventory_2"},
	{"id": "layaway", "label": "Layaway & Finance", "icon": "event_repeat"},
	{"id": "repairs", "label": "Repairs", "icon": "build"},
	{"id": "accounting", "label": "Accounting", "icon": "account_balance"},
	{"id": "employee", "label": "Employee Reports", "icon": "badge"},
]

# ---------------------------------------------------------------------------
# Full report catalog – every report the system knows about
# ---------------------------------------------------------------------------

REPORT_CATALOG: list[dict[str, Any]] = [
	# ── Daily Closeout ───────────────────────────────────────────────────
	{
		"id": "eod_stream_summary",
		"group": "daily_closeout",
		"title": "End of Day Summary",
		"description": "Closeout totals by sales, repairs, layaway, finance, tax, and cash stream.",
		"report_name": "EOD Stream Summary",
		"roles": ACCOUNTING_ROLES,
		"scope": "store",
		"sensitivity": "financial",
		"featured": True,
	},
	{
		"id": "cash_drawer_reconciliation",
		"group": "daily_closeout",
		"title": "Cash Drawer Reconciliation",
		"description": "Cash drawer totals, opening/closing balance, and variance by register.",
		"report_name": "Cash Drawer Reconciliation",
		"roles": ACCOUNTING_ROLES,
		"scope": "store",
		"sensitivity": "financial",
		"featured": True,
	},
	{
		"id": "payment_method_summary",
		"group": "daily_closeout",
		"title": "Payment Method Summary",
		"description": "Cash, card, gift card, layaway, and financier payment breakdown.",
		"report_name": "Payment Method Summary",
		"roles": ACCOUNTING_ROLES,
		"scope": "store",
		"sensitivity": "financial",
		"featured": True,
	},
	{
		"id": "register_variance",
		"group": "daily_closeout",
		"title": "Register Variance",
		"description": "Register-level variance between expected and actual cash.",
		"report_name": "Register Variance",
		"roles": ACCOUNTING_ROLES,
		"scope": "store",
		"sensitivity": "financial",
	},
	{
		"id": "refunds_voids_discounts",
		"group": "daily_closeout",
		"title": "Refunds, Voids & Discounts",
		"description": "Refund, void, discount, and override audit trail.",
		"report_name": "Refunds Voids and Discounts",
		"roles": MANAGER_ROLES | ACCOUNTING_ROLES,
		"scope": "store",
		"sensitivity": "financial",
	},
	# ── Sales Performance ────────────────────────────────────────────────
	{
		"id": "hourly_sales",
		"group": "sales",
		"title": "Hourly Sales",
		"description": "Sales activity by hour for staffing, goals, and traffic patterns.",
		"report_name": "Hourly Sales",
		"roles": MANAGER_ROLES,
		"scope": "store",
		"sensitivity": "manager",
		"featured": True,
	},
	{
		"id": "sales_history",
		"group": "sales",
		"title": "Sales History",
		"description": "Transaction search with automatic own-sales restriction for sales users.",
		"route": "/transactions",
		"roles": SALES_ROLES,
		"scope": "role_based",
		"sensitivity": "operational",
		"featured": True,
	},
	{
		"id": "sales_by_salesperson",
		"group": "sales",
		"title": "Sales by Salesperson",
		"description": "Store performance by associate, transaction count, and revenue.",
		"report_name": "Sales by Salesperson",
		"roles": MANAGER_ROLES,
		"scope": "store",
		"sensitivity": "manager",
		"featured": True,
	},
	{
		"id": "sales_by_category",
		"group": "sales",
		"title": "Sales by Category",
		"description": "Revenue and unit breakdown by jewelry category.",
		"report_name": "Sales by Category",
		"roles": MANAGER_ROLES,
		"scope": "store",
		"sensitivity": "manager",
	},
	{
		"id": "sales_by_metal",
		"group": "sales",
		"title": "Sales by Metal",
		"description": "Revenue and unit breakdown by metal type and purity.",
		"report_name": "Sales by Metal",
		"roles": MANAGER_ROLES,
		"scope": "store",
		"sensitivity": "manager",
	},
	{
		"id": "average_ticket",
		"group": "sales",
		"title": "Average Ticket",
		"description": "Average transaction value by period, category, and salesperson.",
		"report_name": "Average Ticket",
		"roles": MANAGER_ROLES,
		"scope": "store",
		"sensitivity": "manager",
	},
	{
		"id": "high_value_sales",
		"group": "sales",
		"title": "High Value Sales",
		"description": "Sales above configurable thresholds for manager review.",
		"report_name": "High Value Sales",
		"roles": MANAGER_ROLES,
		"scope": "store",
		"sensitivity": "manager",
	},
	{
		"id": "commission_summary",
		"group": "sales",
		"title": "Commission Summary",
		"description": "Commissionable sales splits for manager and payroll review.",
		"report_name": "Commission Summary",
		"roles": MANAGER_ROLES | HR_ROLES,
		"scope": "store",
		"sensitivity": "payroll",
		"featured": True,
	},
	# ── Inventory ────────────────────────────────────────────────────────
	{
		"id": "low_stock_alert",
		"group": "inventory",
		"title": "Low Stock Alert",
		"description": "Items below reorder level or operational stock thresholds.",
		"report_name": "Low Stock Alert",
		"roles": STOCK_ROLES,
		"scope": "store",
		"sensitivity": "operational",
		"featured": True,
	},
	{
		"id": "fast_moving_items",
		"group": "inventory",
		"title": "Fast Moving Items",
		"description": "Top-selling items by velocity for reorder decisions.",
		"report_name": "Fast Moving Items",
		"roles": STOCK_ROLES,
		"scope": "store",
		"sensitivity": "operational",
		"featured": True,
	},
	{
		"id": "slow_moving_items",
		"group": "inventory",
		"title": "Slow Moving Items",
		"description": "Stagnant inventory items with aging and holding cost indicators.",
		"report_name": "Slow Moving Items",
		"roles": STOCK_ROLES,
		"scope": "store",
		"sensitivity": "operational",
	},
	{
		"id": "aged_inventory",
		"group": "inventory",
		"title": "Aged Inventory",
		"description": "Inventory aging buckets showing unsold stock duration.",
		"report_name": "Aged Inventory",
		"roles": STOCK_ROLES,
		"scope": "store",
		"sensitivity": "operational",
	},
	{
		"id": "gold_rate_history",
		"group": "inventory",
		"title": "Gold Rate History",
		"description": "Gold rate changes used by pricing and customer quoting.",
		"report_name": "Gold Rate History",
		"roles": SALES_ROLES,
		"scope": "all",
		"sensitivity": "public_internal",
	},
	{
		"id": "stock_transfers",
		"group": "inventory",
		"title": "Stock Transfers",
		"description": "Inter-store stock transfer status and tracking.",
		"report_name": "Stock Transfers",
		"roles": STOCK_ROLES,
		"scope": "store",
		"sensitivity": "operational",
	},
	{
		"id": "catalog_quality",
		"group": "inventory",
		"title": "Catalog Quality",
		"description": "Items missing images, weights, or mandatory catalog fields.",
		"report_name": "Catalog Quality",
		"roles": STOCK_ROLES,
		"scope": "store",
		"sensitivity": "operational",
	},
	# ── Layaway & Finance ────────────────────────────────────────────────
	{
		"id": "layaway_status",
		"group": "layaway",
		"title": "Layaway Status",
		"description": "Active, completed, cancelled, and overdue layaway contracts.",
		"report_name": "Layaway Status",
		"roles": SALES_ROLES,
		"scope": "store",
		"sensitivity": "customer",
	},
	{
		"id": "layaway_aging",
		"group": "layaway",
		"title": "Layaway Aging",
		"description": "Aged layaway balances and overdue collection risk.",
		"report_name": "Layaway Aging",
		"roles": ACCOUNTING_ROLES,
		"scope": "store",
		"sensitivity": "financial",
		"featured": True,
	},
	{
		"id": "upcoming_layaway_payments",
		"group": "layaway",
		"title": "Upcoming Layaway Payments",
		"description": "Scheduled layaway installments due in the coming period.",
		"report_name": "Upcoming Layaway Payments",
		"roles": SALES_ROLES | ACCOUNTING_ROLES,
		"scope": "store",
		"sensitivity": "customer",
	},
	{
		"id": "overdue_layaway_payments",
		"group": "layaway",
		"title": "Overdue Layaway Payments",
		"description": "Missed layaway installments and delinquent accounts.",
		"report_name": "Overdue Layaway Payments",
		"roles": MANAGER_ROLES | ACCOUNTING_ROLES,
		"scope": "store",
		"sensitivity": "financial",
		"featured": True,
	},
	{
		"id": "cancelled_layaways",
		"group": "layaway",
		"title": "Cancelled Layaways",
		"description": "Cancelled layaway contracts, reasons, and stock return status.",
		"report_name": "Cancelled Layaways",
		"roles": ACCOUNTING_ROLES,
		"scope": "store",
		"sensitivity": "financial",
	},
	{
		"id": "finance_account_balances",
		"group": "layaway",
		"title": "Finance Account Balances",
		"description": "In-house finance balances and receivable exposure.",
		"report_name": "Finance Account Balances",
		"roles": ACCOUNTING_ROLES,
		"scope": "store",
		"sensitivity": "financial",
		"featured": True,
	},
	# ── Repairs ──────────────────────────────────────────────────────────
	{
		"id": "overdue_repairs",
		"group": "repairs",
		"title": "Overdue Repairs",
		"description": "Repair orders past promised date or stalled in workflow.",
		"report_name": "Overdue Repairs Report",
		"roles": SALES_ROLES,
		"scope": "store",
		"sensitivity": "customer",
		"featured": True,
	},
	{
		"id": "repair_turnaround",
		"group": "repairs",
		"title": "Repair Turnaround",
		"description": "Repair completion time by status, technician, and repair type.",
		"report_name": "Repair Turnaround Report",
		"roles": SALES_ROLES | ACCOUNTING_ROLES,
		"scope": "store",
		"sensitivity": "operational",
		"featured": True,
	},
	{
		"id": "repair_revenue",
		"group": "repairs",
		"title": "Repair Revenue",
		"description": "Repair income, collected amounts, and revenue stream health.",
		"report_name": "Repair Revenue Report",
		"roles": ACCOUNTING_ROLES,
		"scope": "store",
		"sensitivity": "financial",
	},
	{
		"id": "repair_type_popularity",
		"group": "repairs",
		"title": "Repair Type Popularity",
		"description": "Most common repair categories and service demand.",
		"report_name": "Repair Type Popularity",
		"roles": SALES_ROLES,
		"scope": "store",
		"sensitivity": "operational",
	},
	{
		"id": "customer_repair_history",
		"group": "repairs",
		"title": "Customer Repair History",
		"description": "Customer repair history for service lookup and follow-up.",
		"report_name": "Customer Repair History",
		"roles": SALES_ROLES,
		"scope": "customer",
		"sensitivity": "customer",
	},
	{
		"id": "technician_performance",
		"group": "repairs",
		"title": "Technician Performance",
		"description": "Repair completion rate, quality, and speed by technician.",
		"report_name": "Technician Performance",
		"roles": MANAGER_ROLES | HR_ROLES,
		"scope": "store",
		"sensitivity": "payroll",
	},
	# ── Accounting & Compliance ──────────────────────────────────────────
	{
		"id": "eod_accounting_export",
		"group": "accounting",
		"title": "EOD Accounting Export",
		"description": "EOD summary formatted for journal entry and GL posting.",
		"report_name": "EOD Accounting Export",
		"roles": ACCOUNTING_ROLES,
		"scope": "store",
		"sensitivity": "financial",
		"featured": True,
	},
	{
		"id": "payment_reconciliation",
		"group": "accounting",
		"title": "Payment Reconciliation",
		"description": "Reconcile payments received against POS invoices.",
		"report_name": "Payment Reconciliation",
		"roles": ACCOUNTING_ROLES,
		"scope": "store",
		"sensitivity": "financial",
		"featured": True,
	},
	{
		"id": "tax_summary",
		"group": "accounting",
		"title": "Tax Summary",
		"description": "Tax collected by category, rate, and period.",
		"report_name": "Tax Summary",
		"roles": ACCOUNTING_ROLES,
		"scope": "store",
		"sensitivity": "financial",
	},
	{
		"id": "gift_card_liability",
		"group": "accounting",
		"title": "Gift Card Liability",
		"description": "Outstanding gift card balances and redemption activity.",
		"report_name": "Gift Card Liability",
		"roles": ACCOUNTING_ROLES,
		"scope": "store",
		"sensitivity": "financial",
	},
	{
		"id": "layaway_liability",
		"group": "accounting",
		"title": "Layaway Liability",
		"description": "Outstanding layaway liability for balance sheet reporting.",
		"report_name": "Layaway Liability",
		"roles": ACCOUNTING_ROLES,
		"scope": "store",
		"sensitivity": "financial",
	},
	{
		"id": "repair_revenue_recognition",
		"group": "accounting",
		"title": "Repair Revenue Recognition",
		"description": "Recognized and deferred repair revenue.",
		"report_name": "Repair Revenue Recognition",
		"roles": ACCOUNTING_ROLES,
		"scope": "store",
		"sensitivity": "financial",
	},
	{
		"id": "audit_log",
		"group": "accounting",
		"title": "Audit Log",
		"description": "System audit trail for compliance and investigation.",
		"report_name": "Audit Log",
		"roles": ADMIN_ROLES | ACCOUNTING_ROLES,
		"scope": "all",
		"sensitivity": "financial",
	},
	{
		"id": "manager_overrides",
		"group": "accounting",
		"title": "Manager Overrides",
		"description": "Manager override events requiring approval.",
		"report_name": "Manager Overrides",
		"roles": ADMIN_ROLES,
		"scope": "all",
		"sensitivity": "financial",
	},
	{
		"id": "trade_in_summary",
		"group": "accounting",
		"title": "Trade-In Summary",
		"description": "Trade-in activity, approvals, and valuation controls.",
		"report_name": "Trade-In Summary",
		"roles": MANAGER_ROLES,
		"scope": "store",
		"sensitivity": "manager",
	},
	# ── Employee / HR ────────────────────────────────────────────────────
	{
		"id": "employee_portal_reports",
		"group": "employee",
		"title": "Employee Portal Reports",
		"description": "Attendance, leave, payroll, expenses, and task reporting.",
		"external_url": "/employee-portal/#/reports",
		"roles": EMPLOYEE_ROLES | HR_ROLES,
		"scope": "role_based",
		"sensitivity": "hr",
	},
	{
		"id": "my_sales",
		"group": "employee",
		"title": "My Sales",
		"description": "Personal sales transactions and performance.",
		"route": "/transactions",
		"roles": {"Sales User"} | EMPLOYEE_ROLES,
		"scope": "own",
		"sensitivity": "operational",
		"featured": True,
	},
	{
		"id": "my_commission",
		"group": "employee",
		"title": "My Commission",
		"description": "Personal commission breakdown and totals.",
		"report_name": "My Commission",
		"roles": {"Sales User"} | EMPLOYEE_ROLES,
		"scope": "own",
		"sensitivity": "payroll",
	},
	{
		"id": "my_attendance",
		"group": "employee",
		"title": "My Attendance",
		"description": "Personal attendance history and check-in status.",
		"external_url": "/employee-portal/#/attendance",
		"roles": EMPLOYEE_ROLES | HR_ROLES,
		"scope": "own",
		"sensitivity": "hr",
	},
	{
		"id": "team_attendance",
		"group": "employee",
		"title": "Team Attendance",
		"description": "Team attendance overview for managers.",
		"external_url": "/employee-portal/#/attendance",
		"roles": HR_ROLES,
		"scope": "department",
		"sensitivity": "hr",
	},
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _has_access(report: dict[str, Any], user_roles: set[str]) -> bool:
	"""Check whether *user_roles* grant access to *report*."""
	if user_roles & ADMIN_ROLES:
		return True
	required = set(report.get("roles") or [])
	return bool(user_roles & required)


def _serialize_report(report: dict[str, Any]) -> dict[str, Any]:
	"""Strip internal fields before sending to the frontend."""
	return {
		"id": report["id"],
		"group": report["group"],
		"title": report["title"],
		"description": report["description"],
		"report_name": report.get("report_name"),
		"route": report.get("route"),
		"external_url": report.get("external_url"),
		"scope": report["scope"],
		"sensitivity": report["sensitivity"],
		"featured": bool(report.get("featured")),
	}


def _get_primary_role(user_roles: set[str]) -> str:
	"""Return the highest-privilege role label for display."""
	for role in ("System Manager", "Administrator"):
		if role in user_roles:
			return "System Manager"
	if "Store Manager" in user_roles:
		return "Store Manager"
	if "Accounts Manager" in user_roles:
		return "Accounts Manager"
	if "Sales Manager" in user_roles:
		return "Sales Manager"
	if "Stock Manager" in user_roles or "Inventory Manager" in user_roles:
		return "Stock Manager"
	if "HR Manager" in user_roles:
		return "HR Manager"
	if "HR User" in user_roles:
		return "HR User"
	if "Sales User" in user_roles:
		return "Sales User"
	if user_roles & EMPLOYEE_ROLES:
		return "Employee"
	return "User"


def _get_scope_label(user_roles: set[str]) -> str:
	if user_roles & ADMIN_ROLES:
		return "All Stores"
	if user_roles & (MANAGER_ROLES | ACCOUNTING_ROLES | STOCK_ROLES | HR_ROLES):
		return "Current Store"
	return "Own Sales"


# ---------------------------------------------------------------------------
# Public API endpoints
# ---------------------------------------------------------------------------


@frappe.whitelist(allow_guest=False)
def get_report_catalog() -> dict[str, Any]:
	"""Return reports visible to the current user.

	The frontend uses this as its display catalog.  Native Frappe Report roles
	and report APIs still enforce actual data access when a report is opened.
	"""
	user = frappe.session.user
	if not user or user == "Guest":
		frappe.throw("Login required", frappe.PermissionError)

	user_roles = set(frappe.get_roles(user))
	reports = [_serialize_report(r) for r in REPORT_CATALOG if _has_access(r, user_roles)]
	visible_group_ids = {r["group"] for r in reports}

	groups = [
		{**g, "count": sum(1 for r in reports if r["group"] == g["id"])}
		for g in REPORT_GROUPS
		if g["id"] in visible_group_ids
	]

	own_sales_only = bool(
		{"Sales User"} & user_roles
		and not user_roles & (MANAGER_ROLES | ACCOUNTING_ROLES | STOCK_ROLES | HR_ROLES)
	)

	return {
		"groups": groups,
		"reports": reports,
		"defaults": {
			"from_date": nowdate(),
			"to_date": nowdate(),
		},
		"role_context": {
			"own_sales_only": own_sales_only,
			"can_export_financials": bool(user_roles & (ACCOUNTING_ROLES | ADMIN_ROLES)),
			"primary_role": _get_primary_role(user_roles),
			"scope_label": _get_scope_label(user_roles),
		},
	}


@frappe.whitelist(allow_guest=False)
def get_report_defaults(report_id: str) -> dict[str, Any]:
	"""Return role-safe default filters for a specific report.

	The frontend should call this before opening a report so the user sees
	correct default dates and scope without manual filter changes.
	"""
	user = frappe.session.user
	if not user or user == "Guest":
		frappe.throw("Login required", frappe.PermissionError)

	user_roles = set(frappe.get_roles(user))

	# Find the report definition
	report_def = None
	for r in REPORT_CATALOG:
		if r["id"] == report_id:
			report_def = r
			break

	if not report_def:
		frappe.throw(f"Unknown report: {report_id}", frappe.ValidationError)

	if not _has_access(report_def, user_roles):
		frappe.throw(
			f"You do not have access to report: {report_def['title']}",
			frappe.PermissionError,
		)

	today = nowdate()
	defaults: dict[str, Any] = {
		"from_date": today,
		"to_date": today,
		"report_id": report_id,
		"report_title": report_def["title"],
	}

	# Role-safe scope defaults
	if user_roles & ADMIN_ROLES:
		defaults["company"] = frappe.db.get_single_value("Global Defaults", "default_company")
	else:
		defaults["company"] = frappe.db.get_single_value("Global Defaults", "default_company")

	own_sales_only = bool(
		{"Sales User"} & user_roles
		and not user_roles & (MANAGER_ROLES | ACCOUNTING_ROLES | STOCK_ROLES | HR_ROLES)
	)

	if own_sales_only:
		defaults["sales_person"] = user
		defaults["owner"] = user
		defaults["scope"] = "own"
	else:
		defaults["scope"] = "store"

	# Report-specific defaults
	group = report_def.get("group", "")
	if group == "daily_closeout":
		defaults["from_date"] = today
		defaults["to_date"] = today
	elif group == "sales":
		defaults["from_date"] = today
		defaults["to_date"] = today
	elif group == "inventory":
		# Inventory reports default to current stock snapshot
		defaults.pop("to_date", None)
	elif group == "layaway":
		defaults["from_date"] = today
		defaults["to_date"] = today
	elif group == "repairs":
		defaults["from_date"] = today
		defaults["to_date"] = today
	elif group == "accounting":
		defaults["from_date"] = today
		defaults["to_date"] = today
	elif group == "employee":
		defaults["from_date"] = today
		defaults["to_date"] = today

	return defaults


@frappe.whitelist(allow_guest=False)
def get_report_summary() -> dict[str, Any]:
	"""Return quick summary KPIs for the Reports hub page header.

	This is a lightweight endpoint used to populate the summary cards at
	the top of the Reports page.
	"""
	user = frappe.session.user
	if not user or user == "Guest":
		frappe.throw("Login required", frappe.PermissionError)

	user_roles = set(frappe.get_roles(user))
	visible_reports = [r for r in REPORT_CATALOG if _has_access(r, user_roles)]
	visible_group_ids = {r["group"] for r in visible_reports}

	return {
		"total_reports": len(visible_reports),
		"total_groups": len(visible_group_ids),
		"featured_count": sum(1 for r in visible_reports if r.get("featured")),
		"primary_role": _get_primary_role(user_roles),
		"scope_label": _get_scope_label(user_roles),
		"groups": [
			{
				"id": g["id"],
				"label": g["label"],
				"icon": g["icon"],
				"count": sum(1 for r in visible_reports if r["group"] == g["id"]),
			}
			for g in REPORT_GROUPS
			if g["id"] in visible_group_ids
		],
	}
