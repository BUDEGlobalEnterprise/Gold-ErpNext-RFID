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
from frappe.utils import flt, getdate, nowdate

# ---------------------------------------------------------------------------
# Role constants - every report references one of these sets
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
# Full report catalog - every report the system knows about
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
	{
		"id": "yoy_day_compare",
		"group": "sales",
		"title": "Year-over-Year Day Compare",
		"description": "Any day vs same day last year: sales, repairs, transactions, and delta analysis.",
		"report_name": "YoY Day Compare",
		"roles": MANAGER_ROLES | ACCOUNTING_ROLES,
		"scope": "store",
		"sensitivity": "manager",
		"featured": True,
	},
	{
		"id": "store_scorecard",
		"group": "sales",
		"title": "Store Scorecard",
		"description": "Side-by-side 5-store ranking: sales, avg ticket, audit compliance, shrinkage, and repair NPS.",
		"report_name": "Store Scorecard",
		"roles": MANAGER_ROLES | ACCOUNTING_ROLES,
		"scope": "all",
		"sensitivity": "manager",
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
	{
		"id": "inventory_timeline",
		"group": "inventory",
		"title": "Inventory Timeline",
		"description": "Serial-level lifecycle: every movement, sale, transfer, and audit event per piece.",
		"report_name": "Inventory Timeline",
		"roles": STOCK_ROLES,
		"scope": "store",
		"sensitivity": "operational",
		"featured": True,
	},
	{
		"id": "shrinkage_trend",
		"group": "inventory",
		"title": "Shrinkage Trend",
		"description": "Rolling 6-month shrinkage value by store and category for insurance and loss prevention.",
		"report_name": "Shrinkage Trend",
		"roles": MANAGER_ROLES | STOCK_ROLES,
		"scope": "store",
		"sensitivity": "financial",
		"featured": True,
	},
	{
		"id": "audit_compliance",
		"group": "inventory",
		"title": "Audit Compliance",
		"description": "On-time audit completion percentage by store, scope, and risk class.",
		"report_name": "Audit Compliance",
		"roles": MANAGER_ROLES | STOCK_ROLES,
		"scope": "store",
		"sensitivity": "manager",
		"featured": True,
	},
	{
		"id": "reorder_suggestions",
		"group": "inventory",
		"title": "Reorder Suggestions",
		"description": "Daily buyer worklist: items below safety stock with velocity data and draft Material Requests.",
		"report_name": "Reorder Suggestions",
		"roles": STOCK_ROLES,
		"scope": "store",
		"sensitivity": "operational",
		"featured": True,
	},
	{
		"id": "reservation_aging",
		"group": "inventory",
		"title": "Reservation Aging",
		"description": "Active reservations approaching expiry with customer and piece details.",
		"report_name": "Reservation Aging",
		"roles": SALES_ROLES | STOCK_ROLES,
		"scope": "store",
		"sensitivity": "operational",
	},
	{
		"id": "transfer_in_transit",
		"group": "inventory",
		"title": "Transfer In-Transit",
		"description": "Pieces currently between stores with dispatch date and expected arrival.",
		"report_name": "Transfer In-Transit",
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
	{
		"id": "high_risk_customers",
		"group": "layaway",
		"title": "High Risk Customers",
		"description": "Customers with repeat overdue payments, cancellations, or defaulted layaways.",
		"report_name": "High Risk Customers",
		"roles": MANAGER_ROLES | ACCOUNTING_ROLES,
		"scope": "store",
		"sensitivity": "financial",
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


@frappe.whitelist(allow_guest=False)
def get_eod_summary() -> dict[str, Any]:
	"""Return today's end-of-day KPIs for the Reports hub EOD section.

	Returns sales, repairs, layaway, and cash position summary for today.
	Only available to roles that can access daily closeout reports.
	"""
	from frappe.utils import cstr, flt, nowdate

	user = frappe.session.user
	if not user or user == "Guest":
		frappe.throw("Login required", frappe.PermissionError)

	user_roles = set(frappe.get_roles(user))
	today = nowdate()

	sales_data = {"total": 0, "count": 0, "avg_ticket": 0, "refunds": 0, "discounts": 0}
	if user_roles & (SALES_ROLES | ACCOUNTING_ROLES | ADMIN_ROLES):
		owner_filter = ""
		owner_params: list[str] = []
		if not (user_roles & (MANAGER_ROLES | ACCOUNTING_ROLES | ADMIN_ROLES)):
			owner_filter = " AND owner = %s"
			owner_params = [user]

		sales_result = frappe.db.sql(
			f"""SELECT
				COUNT(*) as cnt,
				COALESCE(SUM(grand_total), 0) as total,
				COALESCE(SUM(CASE WHEN si.status = 'Return' THEN ABS(grand_total) ELSE 0 END), 0) as refunds,
				COALESCE(SUM(CASE WHEN si.is_discounted = 1
					THEN ABS(discount_amount) ELSE 0 END), 0) as discounts
			FROM `tabSales Invoice` si
			WHERE si.docstatus = 1
			AND si.is_pos = 1
			AND si.posting_date = %s
			{owner_filter}""",
			(today, *owner_params),
			as_dict=True,
		)
		if sales_result and sales_result[0]:
			row = sales_result[0]
			sales_data["count"] = row.cnt or 0
			sales_data["total"] = flt(row.total)
			sales_data["refunds"] = flt(row.refunds)
			sales_data["discounts"] = flt(row.discounts)
			sales_data["avg_ticket"] = flt(row.total) / row.cnt if row.cnt else 0

	repairs_data = {"total_revenue": 0, "active_count": 0, "completed_today": 0, "overdue": 0}
	if user_roles & (SALES_ROLES | HR_ROLES | ADMIN_ROLES):
		repairs_completed = frappe.db.sql(
			"""SELECT COUNT(*) as cnt, COALESCE(SUM(estimated_cost), 0) as revenue
			FROM `tabRepair Order`
			WHERE docstatus < 2
			AND status = 'Ready for Pickup'
			AND DATE(modified) = %s""",
			(today,),
			as_dict=True,
		)
		if repairs_completed and repairs_completed[0]:
			repairs_data["completed_today"] = repairs_completed[0].cnt or 0
			repairs_data["total_revenue"] = flt(repairs_completed[0].revenue)

		repairs_active = frappe.db.sql(
			"""SELECT COUNT(*) as cnt FROM `tabRepair Order`
			WHERE docstatus < 2
			AND status NOT IN ('Ready for Pickup', 'Delivered', 'Cancelled')""",
			as_dict=True,
		)
		if repairs_active and repairs_active[0]:
			repairs_data["active_count"] = repairs_active[0].cnt or 0

		repairs_overdue = frappe.db.sql(
			"""SELECT COUNT(*) as cnt FROM `tabRepair Order`
			WHERE docstatus < 2
			AND status NOT IN ('Ready for Pickup', 'Delivered', 'Cancelled')
			AND promised_date < %s""",
			(today,),
			as_dict=True,
		)
		if repairs_overdue and repairs_overdue[0]:
			repairs_data["overdue"] = repairs_overdue[0].cnt or 0

	payment_breakdown = []
	if user_roles & (ACCOUNTING_ROLES | ADMIN_ROLES):
		payments = frappe.db.sql(
			"""SELECT
				mop.mode_of_payment as method,
				COALESCE(SUM(mop.amount), 0) as total,
				COUNT(*) as count
			FROM `tabSales Invoice Payment` mop
			JOIN `tabSales Invoice` si ON mop.parent = si.name
			WHERE si.docstatus = 1
			AND si.is_pos = 1
			AND si.posting_date = %s
			GROUP BY mop.mode_of_payment
			ORDER BY total DESC""",
			(today,),
			as_dict=True,
		)
		payment_breakdown = [
			{"method": p.method, "total": flt(p.total), "count": p.count} for p in (payments or [])
		]

	layaway_data = {"payments_due": 0, "overdue_count": 0}
	if user_roles & (SALES_ROLES | ACCOUNTING_ROLES | ADMIN_ROLES):
		layaway_due = frappe.db.sql(
			"""SELECT COUNT(*) as cnt, COALESCE(SUM(balance_amount), 0) as total
			FROM `tabLayaway Contract`
			WHERE docstatus = 1
			AND status = 'Active'
			AND next_payment_date = %s""",
			(today,),
			as_dict=True,
		)
		if layaway_due and layaway_due[0]:
			layaway_data["payments_due"] = layaway_due[0].cnt or 0

		layaway_overdue = frappe.db.sql(
			"""SELECT COUNT(*) as cnt FROM `tabLayaway Contract`
			WHERE docstatus = 1
			AND status = 'Active'
			AND next_payment_date < %s""",
			(today,),
			as_dict=True,
		)
		if layaway_overdue and layaway_overdue[0]:
			layaway_data["overdue_count"] = layaway_overdue[0].cnt or 0

	return {
		"date": today,
		"sales": sales_data,
		"repairs": repairs_data,
		"payments": payment_breakdown,
		"layaway": layaway_data,
		"can_view_financials": bool(user_roles & (ACCOUNTING_ROLES | ADMIN_ROLES)),
		"can_closeout": bool(user_roles & (MANAGER_ROLES | ACCOUNTING_ROLES | ADMIN_ROLES)),
	}


# ---------------------------------------------------------------------------
# Daily Brief - single aggregated endpoint for the Daily Brief tab
# ---------------------------------------------------------------------------

ROW_ACTION_MAP = {
	"reorder_suggestions": [
		{"action": "raise_mr", "label": "Raise MR", "icon": "add_shopping_cart"},
	],
	"overdue_layaway_payments": [
		{"action": "call_customer", "label": "Call Customer", "icon": "call"},
		{"action": "send_reminder", "label": "Send Reminder", "icon": "notifications"},
	],
	"overdue_repairs": [
		{"action": "sms_customer", "label": "SMS Customer", "icon": "sms"},
		{"action": "mark_delayed", "label": "Mark as Delayed", "icon": "schedule"},
	],
	"low_stock_alert": [
		{"action": "request_transfer", "label": "Request Transfer", "icon": "local_shipping"},
	],
	"reservation_aging": [
		{"action": "extend_hold", "label": "Extend Hold", "icon": "timelapse"},
		{"action": "convert_to_layaway", "label": "Convert to Layaway", "icon": "event_repeat"},
	],
}


@frappe.whitelist(allow_guest=False)
def get_daily_brief(store: str | None = None) -> dict[str, Any]:
	"""Return all KPI tiles + live feed for the Daily Brief in one round-trip."""
	from frappe.utils import add_days, flt, now_datetime

	user = frappe.session.user
	if not user or user == "Guest":
		frappe.throw("Login required", frappe.PermissionError)

	user_roles = set(frappe.get_roles(user))
	today = nowdate()
	today_dt = getdate(today)
	last_year_today = add_days(today_dt, -365)

	sales = _brief_sales(today, user_roles, user)
	repairs_rev = _brief_repair_revenue(today, user_roles)
	layaway_dep = _brief_layaway_deposits(today, user_roles)
	cash_var = _brief_cash_variance(today, user_roles)
	low_stock = _brief_low_stock_count(store, user_roles)
	overdue_rep = _brief_overdue_repairs(user_roles)
	fin_ar = _brief_financier_ar(today, user_roles)
	next_audit = _brief_next_audit(store, user_roles)
	pending = _brief_pending_approvals(user_roles)
	feed = _brief_live_feed(store, user_roles)
	yoy = _brief_yoy_deltas(today, last_year_today, user_roles, user)

	return {
		"date": today,
		"sales": sales,
		"repair_revenue": repairs_rev,
		"layaway_deposits": layaway_dep,
		"cash_variance_today": cash_var,
		"low_stock_count": low_stock,
		"overdue_repairs": overdue_rep,
		"financier_ar": fin_ar,
		"next_audit": next_audit,
		"pending_approvals": pending,
		"live_feed": feed,
		"yoy_deltas": yoy,
		"can_view_financials": bool(user_roles & (ACCOUNTING_ROLES | ADMIN_ROLES)),
	}


def _brief_sales(today, user_roles, user):
	from frappe.utils import flt

	if not (user_roles & (SALES_ROLES | ACCOUNTING_ROLES | ADMIN_ROLES)):
		return {"total": 0, "count": 0}
	owner_filter = ""
	params: list = [today]
	if not (user_roles & (MANAGER_ROLES | ACCOUNTING_ROLES | ADMIN_ROLES)):
		owner_filter = " AND si.owner = %s"
		params.append(user)
	row = frappe.db.sql(
		f"""SELECT COUNT(*) as cnt, COALESCE(SUM(grand_total), 0) as total
		FROM `tabSales Invoice` si
		WHERE si.docstatus = 1 AND si.is_pos = 1 AND si.posting_date = %s{owner_filter}""",
		params,
		as_dict=True,
	)
	r = row[0] if row else {}
	return {"total": flt(r.get("total", 0)), "count": r.get("cnt", 0)}


def _brief_repair_revenue(today, user_roles):
	from frappe.utils import flt

	if not (user_roles & (SALES_ROLES | ACCOUNTING_ROLES | ADMIN_ROLES)):
		return {"total": 0, "count": 0}
	row = frappe.db.sql(
		"""SELECT COUNT(*) as cnt, COALESCE(SUM(estimated_cost), 0) as total
		FROM `tabRepair Order` WHERE docstatus < 2 AND status = 'Ready for Pickup' AND DATE(modified) = %s""",
		(today,),
		as_dict=True,
	)
	r = row[0] if row else {}
	return {"total": flt(r.get("total", 0)), "count": r.get("cnt", 0)}


def _brief_layaway_deposits(today, user_roles):
	from frappe.utils import flt

	if not (user_roles & (SALES_ROLES | ACCOUNTING_ROLES | ADMIN_ROLES)):
		return {"total": 0}
	row = frappe.db.sql(
		"""SELECT COALESCE(SUM(sip.amount), 0) as total
		FROM `tabSales Invoice Payment` sip
		JOIN `tabSales Invoice` si ON sip.parent = si.name
		WHERE si.docstatus = 1 AND si.custom_transaction_stream = 'Layaway Deposit'
		AND si.posting_date = %s""",
		(today,),
		as_dict=True,
	)
	return {"total": flt(row[0].total) if row else 0}


def _brief_cash_variance(today, user_roles):
	from frappe.utils import flt

	if not (user_roles & (ACCOUNTING_ROLES | ADMIN_ROLES)):
		return 0.0
	frappe.db.sql(
		"""SELECT COALESCE(SUM(
			CASE WHEN sip.mode_of_payment = 'Cash' THEN sip.amount ELSE 0 END
		), 0) as expected
		FROM `tabSales Invoice Payment` sip
		JOIN `tabSales Invoice` si ON sip.parent = si.name
		WHERE si.docstatus = 1 AND si.is_pos = 1 AND si.posting_date = %s""",
		(today,),
		as_dict=True,
	)
	return 0.0


def _brief_low_stock_count(store, user_roles):
	if not (user_roles & (STOCK_ROLES | MANAGER_ROLES | ADMIN_ROLES)):
		return 0
	filters = {"actual_qty": ["<=", 2]}
	if store:
		filters["warehouse"] = ["like", f"%{store}%"]
	return frappe.db.count("Bin", filters)


def _brief_overdue_repairs(user_roles):
	if not (user_roles & (SALES_ROLES | MANAGER_ROLES | ADMIN_ROLES)):
		return {"count": 0, "max_days_overdue": 0}
	from frappe.utils import nowdate

	today = nowdate()
	rows = frappe.db.sql(
		"""SELECT COUNT(*) as cnt,
			COALESCE(MAX(DATEDIFF(%s, promised_date)), 0) as max_days
		FROM `tabRepair Order`
		WHERE docstatus < 2
		AND status NOT IN ('Ready for Pickup', 'Delivered', 'Cancelled')
		AND promised_date < %s""",
		(today, today),
		as_dict=True,
	)
	r = rows[0] if rows else {}
	return {"count": r.get("cnt", 0), "max_days_overdue": r.get("max_days", 0)}


def _brief_financier_ar(today, user_roles):
	from frappe.utils import flt

	from zevar_core.constants import FINANCING_WATERFALL

	if not (user_roles & (ACCOUNTING_ROLES | ADMIN_ROLES)):
		return []
	result = []
	for financier in FINANCING_WATERFALL:
		row = frappe.db.sql(
			"""SELECT COALESCE(SUM(sip.amount), 0) as today_total
			FROM `tabSales Invoice Payment` sip
			JOIN `tabSales Invoice` si ON sip.parent = si.name
			WHERE si.docstatus = 1 AND si.is_pos = 1
			AND sip.mode_of_payment = %s AND si.posting_date = %s""",
			(financier, today),
			as_dict=True,
		)
		result.append(
			{
				"financier": financier,
				"today_ar": flt(row[0].today_total) if row else 0,
			}
		)
	return result


def _brief_next_audit(store, user_roles):
	if not (user_roles & (STOCK_ROLES | MANAGER_ROLES | ADMIN_ROLES)):
		return {"scope": None, "due_in_hours": None}
	filters = {"status": "Scheduled"}
	if store:
		filters["store_location"] = ["like", f"%{store}%"]
	plans = frappe.get_all(
		"Audit Plan",
		filters=filters,
		fields=["scope", "scheduled_for"],
		order_by="scheduled_for asc",
		limit=1,
	)
	if not plans:
		return {"scope": None, "due_in_hours": None}
	from frappe.utils import now_datetime

	scheduled = plans[0]
	delta = (scheduled.scheduled_for - now_datetime()).total_seconds() / 3600
	return {"scope": scheduled.scope, "due_in_hours": max(0, round(delta))}


def _brief_pending_approvals(user_roles):
	if not (user_roles & (MANAGER_ROLES | ADMIN_ROLES)):
		return {"variance_overrides": 0, "transfer_receives": 0}
	variance = frappe.db.count(
		"POS Audit Log",
		{
			"event_type": "variance_override",
			"timestamp": [">=", frappe.utils.nowdate()],
		},
	)
	transfers = frappe.db.count(
		"Stock Entry",
		{
			"stock_entry_type": "Material Transfer",
			"docstatus": 0,
		},
	)
	return {"variance_overrides": variance, "transfer_receives": transfers}


def _brief_live_feed(store, user_roles, limit=50):
	if not (user_roles & (MANAGER_ROLES | ACCOUNTING_ROLES | ADMIN_ROLES)):
		return []
	filters = {}
	if store:
		filters["reference_document"] = ["like", f"%{store}%"]
	logs = frappe.get_all(
		"POS Audit Log",
		filters=filters,
		fields=["timestamp", "user", "event_type", "details"],
		order_by="timestamp desc",
		limit=limit,
	)
	return logs


def _brief_yoy_deltas(today, last_year_today, user_roles, user):
	from frappe.utils import flt

	result = {}
	if not (user_roles & (SALES_ROLES | ACCOUNTING_ROLES | ADMIN_ROLES)):
		return result
	owner_filter = ""
	params_this: list = [today]
	params_last: list = [last_year_today]
	if not (user_roles & (MANAGER_ROLES | ACCOUNTING_ROLES | ADMIN_ROLES)):
		owner_filter = " AND owner = %s"
		params_this.append(user)
		params_last.append(user)

	for label, params in [("this", params_this), ("last", params_last)]:
		row = frappe.db.sql(
			f"""SELECT COALESCE(SUM(grand_total), 0) as total
			FROM `tabSales Invoice`
			WHERE docstatus = 1 AND is_pos = 1 AND posting_date = %s{owner_filter}""",
			params,
			as_dict=True,
		)
		result[label] = flt(row[0].total) if row else 0

	this_val = result.get("this", 0)
	last_val = result.get("last", 0)
	pct = round(((this_val - last_val) / last_val) * 100, 1) if last_val else 0
	result["pct"] = pct
	return {"sales_total": result}


# ---------------------------------------------------------------------------
# Row-level actions
# ---------------------------------------------------------------------------


@frappe.whitelist(allow_guest=False)
def get_row_actions(report_id: str) -> list[dict]:
	"""Return available row actions for a given report."""
	user = frappe.session.user
	user_roles = set(frappe.get_roles(user))
	for r in REPORT_CATALOG:
		if r["id"] == report_id:
			if not _has_access(r, user_roles):
				return []
			return ROW_ACTION_MAP.get(report_id, [])
	return []


@frappe.whitelist(allow_guest=False)
def execute_row_action(report_id: str, action: str, row_data: dict | str = "{}"):
	"""Execute a row-level action from within a report."""
	import json

	from frappe.utils import flt

	user = frappe.session.user
	user_roles = set(frappe.get_roles(user))
	if isinstance(row_data, str):
		row_data = json.loads(row_data)

	report_def = None
	for r in REPORT_CATALOG:
		if r["id"] == report_id:
			report_def = r
			break
	if not report_def or not _has_access(report_def, user_roles):
		frappe.throw("No access", frappe.PermissionError)

	if action == "raise_mr" and report_id == "reorder_suggestions":
		return _action_raise_mr(row_data)
	if action == "call_customer" and report_id == "overdue_layaway_payments":
		return _action_call_customer(row_data)
	if action == "send_reminder" and report_id == "overdue_layaway_payments":
		return _action_send_layaway_reminder(row_data)
	if action == "sms_customer" and report_id == "overdue_repairs":
		return _action_sms_customer(row_data)
	if action == "mark_delayed" and report_id == "overdue_repairs":
		return _action_mark_repair_delayed(row_data)
	if action == "request_transfer" and report_id == "low_stock_alert":
		return _action_request_transfer(row_data)
	if action == "extend_hold" and report_id == "reservation_aging":
		return _action_extend_reservation(row_data)
	if action == "convert_to_layaway" and report_id == "reservation_aging":
		return _action_convert_reservation(row_data)

	frappe.throw(f"Unknown action: {action} for report: {report_id}", frappe.ValidationError)


def _action_raise_mr(row):
	from frappe.utils import add_days, today

	item_code = row.get("item_code") or row.get("Item Code")
	if not item_code:
		frappe.throw("Item code required", frappe.ValidationError)
	company = frappe.defaults.get_global_default("company")
	cost_center = frappe.get_cached_value("Company", company, "cost_center")
	qty = flt(row.get("suggested_qty") or row.get("qty") or 1)

	mr = frappe.new_doc("Material Request")
	mr.material_request_type = "Purchase"
	mr.company = company
	mr.cost_center = cost_center
	mr.schedule_date = add_days(today(), 7)
	mr.append(
		"items",
		{
			"item_code": item_code,
			"qty": qty,
			"schedule_date": add_days(today(), 7),
			"cost_center": cost_center,
		},
	)
	mr.insert(ignore_permissions=True)
	return {"status": "created", "name": mr.name}


def _action_call_customer(row):
	customer = row.get("customer") or row.get("Customer")
	if not customer:
		frappe.throw("Customer required", frappe.ValidationError)
	phone = frappe.db.get_value("Customer", customer, "mobile_no") or frappe.db.get_value(
		"Contact", {"links": {"link_doctype": "Customer", "link_name": customer}}, "phone"
	)
	return {"action": "call", "customer": customer, "phone": phone or ""}


def _action_send_layaway_reminder(row):
	customer = row.get("customer") or row.get("Customer")
	if not customer:
		frappe.throw("Customer required", frappe.ValidationError)
	email = frappe.db.get_value("Customer", customer, "email_id")
	if email:
		frappe.sendmail(
			recipients=[email],
			subject="Layaway Payment Reminder",
			message="This is a reminder that your layaway payment is overdue. Please contact the store.",
		)
	return {"status": "sent", "customer": customer}


def _action_sms_customer(row):
	customer = row.get("customer") or row.get("Customer")
	if not customer:
		frappe.throw("Customer required", frappe.ValidationError)
	phone = frappe.db.get_value("Customer", customer, "mobile_no")
	return {"action": "sms", "customer": customer, "phone": phone or ""}


def _action_mark_repair_delayed(row):
	repair = row.get("name") or row.get("Repair Order")
	if not repair:
		frappe.throw("Repair Order required", frappe.ValidationError)
	if frappe.db.exists("Repair Order", repair):
		frappe.db.set_value("Repair Order", repair, "status", "Delayed")
	return {"status": "updated", "repair": repair}


def _action_request_transfer(row):
	item_code = row.get("item_code") or row.get("Item Code")
	if not item_code:
		frappe.throw("Item code required", frappe.ValidationError)
	return {"action": "open_transfer_modal", "item_code": item_code}


def _action_extend_reservation(row):
	reservation = row.get("name") or row.get("Reservation")
	days = int(row.get("extend_days") or 2)
	if not reservation:
		frappe.throw("Reservation name required", frappe.ValidationError)
	if frappe.db.exists("Stock Reservation", reservation):
		from frappe.utils import add_days, now_datetime

		current = frappe.db.get_value("Stock Reservation", reservation, "hold_until")
		new_date = add_days(current, days) if current else add_days(now_datetime(), days)
		frappe.db.set_value("Stock Reservation", reservation, "hold_until", new_date)
	return {"status": "extended", "reservation": reservation, "days": days}


def _action_convert_reservation(row):
	reservation = row.get("name") or row.get("Reservation")
	customer = row.get("customer") or row.get("Customer")
	serial_no = row.get("serial_no") or row.get("Serial No")
	if not reservation or not customer:
		frappe.throw("Reservation and Customer required", frappe.ValidationError)
	return {
		"action": "open_layaway_modal",
		"reservation": reservation,
		"customer": customer,
		"serial_no": serial_no,
	}


# ---------------------------------------------------------------------------
# Report Subscription CRUD
# ---------------------------------------------------------------------------


@frappe.whitelist(allow_guest=False)
def get_report_subscriptions() -> list[dict]:
	"""Return all subscriptions for the current user."""
	user = frappe.session.user
	subs = frappe.get_all(
		"Report Subscription",
		filters={"user": user},
		fields=[
			"name",
			"report_id",
			"report_title",
			"enabled",
			"delivery_method",
			"export_format",
			"cron_expression",
			"schedule_label",
			"next_run",
			"last_run",
		],
		order_by="next_run asc",
	)
	return subs


@frappe.whitelist(allow_guest=False)
def create_report_subscription(
	report_id: str,
	cron_expression: str = "0 22 * * *",
	delivery_method: str = "Email",
	export_format: str = "PDF",
	filters_json: str = "{}",
	recipient_email: str | None = None,
	recipient_phone: str | None = None,
) -> dict:
	"""Create a new report subscription for the current user."""
	user = frappe.session.user
	user_roles = set(frappe.get_roles(user))

	report_def = None
	for r in REPORT_CATALOG:
		if r["id"] == report_id:
			report_def = r
			break
	if not report_def:
		frappe.throw(f"Unknown report: {report_id}", frappe.ValidationError)
	if not _has_access(report_def, user_roles):
		frappe.throw("No access to this report", frappe.PermissionError)

	existing = frappe.db.exists(
		"Report Subscription",
		{
			"user": user,
			"report_id": report_id,
			"cron_expression": cron_expression,
		},
	)
	if existing:
		frappe.throw("Subscription already exists for this report and schedule", frappe.DuplicateEntryError)

	doc = frappe.new_doc("Report Subscription")
	doc.user = user
	doc.report_id = report_id
	doc.cron_expression = cron_expression
	doc.delivery_method = delivery_method
	doc.export_format = export_format
	doc.filters_json = filters_json
	doc.recipient_email = recipient_email or frappe.db.get_value("User", user, "email")
	doc.recipient_phone = recipient_phone or ""
	doc.insert(ignore_permissions=True)
	return {"status": "created", "name": doc.name, "report_title": doc.report_title}


@frappe.whitelist(allow_guest=False)
def delete_report_subscription(name: str) -> dict:
	"""Delete a report subscription owned by the current user."""
	user = frappe.session.user
	sub_user = frappe.db.get_value("Report Subscription", name, "user")
	if sub_user != user and "System Manager" not in frappe.get_roles(user):
		frappe.throw("Not authorized", frappe.PermissionError)
	frappe.delete_doc("Report Subscription", name, ignore_permissions=True)
	return {"status": "deleted"}


@frappe.whitelist(allow_guest=False)
def toggle_report_subscription(name: str) -> dict:
	"""Toggle enabled/disabled on a subscription."""
	user = frappe.session.user
	sub_user = frappe.db.get_value("Report Subscription", name, "user")
	if sub_user != user and "System Manager" not in frappe.get_roles(user):
		frappe.throw("Not authorized", frappe.PermissionError)
	current = frappe.db.get_value("Report Subscription", name, "enabled")
	new_val = 0 if current else 1
	frappe.db.set_value("Report Subscription", name, "enabled", new_val)
	return {"status": "toggled", "enabled": bool(new_val)}
