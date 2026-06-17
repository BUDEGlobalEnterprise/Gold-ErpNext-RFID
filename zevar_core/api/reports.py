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
	# ── Accounting ───────────────────────────────────────────────────────
	{
		"id": "profit_and_loss",
		"group": "accounting",
		"title": "Profit & Loss Statement",
		"description": "Income vs expenses for a period. Shows net profit/loss.",
		"report_name": "Profit and Loss Statement",
		"report_type": "Report Builder",
		"roles": ACCOUNTING_ROLES,
		"scope": "company",
		"sensitivity": "financial",
		"featured": True,
	},
	{
		"id": "balance_sheet",
		"group": "accounting",
		"title": "Balance Sheet",
		"description": "Assets, liabilities, and equity at a point in time.",
		"report_name": "Balance Sheet",
		"report_type": "Report Builder",
		"roles": ACCOUNTING_ROLES,
		"scope": "company",
		"sensitivity": "financial",
		"featured": True,
	},
	{
		"id": "general_ledger",
		"group": "accounting",
		"title": "General Ledger",
		"description": "All journal entries for an account or period.",
		"report_name": "General Ledger",
		"report_type": "Script Report",
		"roles": ACCOUNTING_ROLES,
		"scope": "company",
		"sensitivity": "financial",
	},
	{
		"id": "trial_balance",
		"group": "accounting",
		"title": "Trial Balance",
		"description": "Debit and credit totals for all accounts.",
		"report_name": "Trial Balance",
		"report_type": "Script Report",
		"roles": ACCOUNTING_ROLES,
		"scope": "company",
		"sensitivity": "financial",
	},
	{
		"id": "accounts_receivable",
		"group": "accounting",
		"title": "Accounts Receivable",
		"description": "Outstanding customer balances and aging.",
		"report_name": "Accounts Receivable",
		"report_type": "Script Report",
		"roles": ACCOUNTING_ROLES,
		"scope": "company",
		"sensitivity": "financial",
	},
	{
		"id": "accounts_payable",
		"group": "accounting",
		"title": "Accounts Payable",
		"description": "Outstanding supplier balances and aging.",
		"report_name": "Accounts Payable",
		"report_type": "Script Report",
		"roles": ACCOUNTING_ROLES,
		"scope": "company",
		"sensitivity": "financial",
	},
	{
		"id": "sales_register",
		"group": "accounting",
		"title": "Sales Register",
		"description": "All sales invoices with tax and payment details.",
		"report_name": "Sales Register",
		"report_type": "Script Report",
		"roles": ACCOUNTING_ROLES,
		"scope": "company",
		"sensitivity": "financial",
	},
	{
		"id": "purchase_register",
		"group": "accounting",
		"title": "Purchase Register",
		"description": "All purchase invoices with tax and payment details.",
		"report_name": "Purchase Register",
		"report_type": "Script Report",
		"roles": ACCOUNTING_ROLES,
		"scope": "company",
		"sensitivity": "financial",
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
	row = frappe.db.sql(
		"""SELECT COALESCE(SUM(
			CASE WHEN sip.mode_of_payment = 'Cash' THEN sip.amount ELSE 0 END
		), 0) as expected
		FROM `tabSales Invoice Payment` sip
		JOIN `tabSales Invoice` si ON sip.parent = si.name
		WHERE si.docstatus = 1 AND si.is_pos = 1 AND si.posting_date = %s""",
		(today,),
		as_dict=True,
	)
	return flt(row[0].expected) if row else 0.0


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

# ===========================================================================
# End-of-Day Closeout Report
#
# A single comprehensive endpoint that returns ALL EOD data in one call so the
# frontend EOD closeout page can render a unified Z-Report.  Mirrors the
# role-aware pattern used by ``get_daily_brief``: sales figures are
# owner-restricted for non-managers, while financial / cash / audit sections
# are only populated for accounting / manager / admin roles.
#
# All SQL uses parameterised placeholders (%s) — user / date / store values are
# never string-interpolated.  Helpers return zeros (never raise) when a section
# is not permitted or when the underlying doctype / field is absent.
# ===========================================================================

EOD_DEFAULT_VARIANCE_THRESHOLD = 5.0
EOD_HIGH_VALUE_ITEM_THRESHOLD = 5000.0  # items sold above this rate are "high value"

# Tender groupings used by the payment-method breakdown
EOD_TENDER_GROUPS = {
	"cash": ["Cash"],
	"card": ["Credit Card", "Debit Card", "Apple Pay", "Google Pay", "Venmo", "Cash App"],
	"check": ["Check", "Wire Transfer", "Zelle"],
	"financing": [],  # filled from FINANCING_WATERFALL at runtime
	"gift_card": ["Gift Card"],
	"trade_in": ["Trade-In"],
	"store_credit": ["Store Credit"],
}


def _eod_can_see_store(user_roles: set[str]) -> bool:
	"""Whole-store visibility (vs. own-sales-only) for managers/accounting/admin."""
	return bool(user_roles & (MANAGER_ROLES | ACCOUNTING_ROLES | ADMIN_ROLES))


def _eod_can_see_financials(user_roles: set[str]) -> bool:
	return bool(user_roles & (ACCOUNTING_ROLES | ADMIN_ROLES))


def _eod_owner_clause(user_roles: set[str], user: str, alias: str = "si"):
	"""Return ``(sql_fragment, params)`` restricting sales to the caller's own.

	The fragment is a static string (never user input), so it is safe to
	interpolate into the query the same way ``_brief_sales`` does.
	"""
	if _eod_can_see_store(user_roles):
		return "", []
	return f" AND {alias}.owner = %s", [user]


def _eod_resolve_date(date: str | None) -> str:
	"""Normalise the requested date to a ``YYYY-MM-DD`` string (defaults today)."""
	from frappe.utils import getdate, nowdate

	if not date or str(date).strip().lower() in ("today", "now", ""):
		return nowdate()
	return getdate(date).isoformat()


def _eod_safe(label: str, fn, default):
	"""Run an EOD section defensively — log + return *default* on any failure.

	This guarantees a missing custom field, an absent doctype, or a schema
	drift in one section never breaks the whole closeout payload (the report
	contract is "zeros, not errors").
	"""
	try:
		return fn()
	except Exception:
		frappe.log_error(f"EOD closeout section failed: {label}", frappe.get_traceback())
		return default


def _eod_si_has_stream_field() -> bool:
	"""Whether Sales Invoice exposes the custom ``custom_transaction_stream`` field."""
	try:
		return bool(frappe.get_meta("Sales Invoice").has_field("custom_transaction_stream"))
	except Exception:
		return False


@frappe.whitelist(allow_guest=False)
def get_eod_closeout_report(date: str | None = None, store: str | None = None) -> dict[str, Any]:
	"""Return the full End-of-Day closeout dataset for *date* (default today).

	The response is a structured dict with the ten EOD sections (A-J) plus a
	``meta`` block describing permissions and the generation timestamp.  Each
	section gracefully degrades to zeros / empty when the caller lacks the role
	to view it.
	"""
	from frappe.utils import now_datetime

	user = frappe.session.user
	if not user or user == "Guest":
		frappe.throw("Login required", frappe.PermissionError)

	user_roles = set(frappe.get_roles(user))
	target = _eod_resolve_date(date)

	report = {
		"date": target,
		"store": store or None,
		"session_info": _eod_safe("session_info", lambda: _eod_session_info(target, store, user_roles, user), _empty_session()),
		"revenue": _eod_safe("revenue", lambda: _eod_revenue(target, store, user_roles, user), _empty_revenue()),
		"transaction_streams": _eod_safe(
			"transaction_streams",
			lambda: _eod_transaction_streams(target, store, user_roles, user),
			{
				"jewelry_sales": {"count": 0, "total": 0, "avg_ticket": 0},
				"repairs": {"count": 0, "total_revenue": 0, "completed_today": 0, "active": 0},
				"custom_orders": {"count": 0, "total_deposits": 0},
				"layaway": {"new_contracts": 0, "deposits_collected": 0, "matured_today": 0, "active": 0},
				"trade_ins": {"count": 0, "total_value": 0},
				"gold_purchases": {"count": 0, "total_weight_g": 0, "total_value": 0},
				"gift_cards": {"sold": {"count": 0, "amount": 0}, "redeemed": {"count": 0, "amount": 0}},
			},
		),
		"payment_methods": _eod_safe("payment_methods", lambda: _eod_tender_breakdown(target, store, user_roles, user), {"methods": [], "groups": {}, "financing": [], "total": 0}),
		"cash_reconciliation": _eod_safe("cash_reconciliation", lambda: _eod_cash_reconciliation(target, store, user_roles, user), {"permitted": False, **_empty_cash_recon()}),
		"audit_trail": _eod_safe("audit_trail", lambda: _eod_audit_trail(target, store, user_roles, user), {"permitted": False, "voids": {"count": 0, "total": 0, "reasons": []}, "refunds": {"count": 0, "total": 0, "items_returned": 0, "reasons": []}, "discounts": {"count": 0, "total": 0, "top_reasons": []}, "manager_overrides": {"count": 0, "by_approver": [], "recent": []}, "price_overrides": {"count": 0, "recent": []}}),
		"salesperson_performance": _eod_safe("salesperson_performance", lambda: _eod_salesperson_performance(target, store, user_roles, user), {"permitted": False, "salespeople": [], "top_by_revenue": None, "top_by_count": None, "total_commission": 0}),
		"inventory_impact": _eod_safe("inventory_impact", lambda: _eod_inventory_impact(target, store, user_roles, user), {"permitted": False, "items_sold": 0, "items_returned": 0, "net_change": 0, "low_stock_count": 0, "low_stock": [], "high_value_items": []}),
		"repair_status": _eod_safe("repair_status", lambda: _eod_repair_status(target, store, user_roles, user), {"permitted": False, "new_today": 0, "completed_today": 0, "delivered_today": 0, "active": 0, "overdue": 0, "oldest_overdue": None}),
		"operational_notes": _eod_safe("operational_notes", lambda: _eod_operational_notes(target, store, user_roles, user), {"manager_notes": [], "flagged_incidents": [], "next_day_opening_schedule": None}),
		"meta": {
			"can_see_store": _eod_can_see_store(user_roles),
			"can_see_financials": _eod_can_see_financials(user_roles),
			"primary_role": _get_primary_role(user_roles),
			"generated_at": now_datetime().isoformat(),
		},
	}
	return report


# ---------------------------------------------------------------------------
# Section A — Session Summary
# ---------------------------------------------------------------------------


def _eod_session_info(target, store, user_roles, user):
	"""POS session metadata: opening float, session window, cashiers on duty."""
	from frappe.utils import flt, get_datetime, now_datetime, time_diff_in_hours

	if not (user_roles & (SALES_ROLES | MANAGER_ROLES | ACCOUNTING_ROLES | ADMIN_ROLES)):
		return _empty_session()

	owner_clause, owner_params = ("", []) if _eod_can_see_store(user_roles) else (
		" AND poe.user = %s",
		[user],
	)

	openings = frappe.db.sql(
		f"""SELECT poe.name, poe.user, poe.pos_profile, poe.company,
			poe.period_start_date, poe.status, poe.pos_closing_entry
		FROM `tabPOS Opening Entry` poe
		WHERE poe.docstatus = 1
		AND DATE(poe.period_start_date) = %s{owner_clause}""",
		(target, *owner_params),
		as_dict=True,
	)

	if not openings:
		return _empty_session()

	opening_names = [o.name for o in openings]
	# Opening cash float from balance_details child
	opening_cash_rows = frappe.db.sql(
		"""SELECT parent, COALESCE(SUM(opening_amount), 0) as opening_amount
		FROM `tabPOS Opening Entry Detail`
		WHERE parent IN %s AND mode_of_payment = 'Cash'
		GROUP BY parent""",
		(opening_names,),
		as_dict=True,
	)
	opening_float_by_session = {r.parent: flt(r.opening_amount) for r in opening_cash_rows}
	total_opening_float = sum(opening_float_by_session.values())

	# Cashiers + full names
	cashier_ids = list({o.user for o in openings if o.user})
	cashier_names = {}
	if cashier_ids:
		users = frappe.get_all("User", filters={"name": ["in", cashier_ids]}, fields=["name", "full_name"])
		cashier_names = {u.name: u.full_name or u.name for u in users}

	# Closing entries (end times + counted cash) from linked POS Closing Entries
	closing_names = [o.pos_closing_entry for o in openings if o.pos_closing_entry]
	closings = {}
	if closing_names:
		cl_rows = frappe.db.sql(
			"""SELECT name, period_end_date
			FROM `tabPOS Closing Entry`
			WHERE name IN %s""",
			(closing_names,),
			as_dict=True,
		)
		closings = {c.name: c for c in cl_rows}

	starts = [get_datetime(o.period_start_date) for o in openings if o.period_start_date]
	ends = [get_datetime(closings[o.pos_closing_entry].period_end_date) for o in openings
			if o.pos_closing_entry and o.pos_closing_entry in closings and closings[o.pos_closing_entry].period_end_date]

	session_start = min(starts).isoformat() if starts else None
	session_end = max(ends).isoformat() if ends else None
	now = now_datetime()
	duration_hours = round(time_diff_in_hours(now, min(starts)), 2) if starts else 0

	return {
		"has_session": True,
		"opening_balance": total_opening_float,
		"session_count": len(openings),
		"session_start": session_start,
		"session_end": session_end,
		"duration_hours": duration_hours,
		"cashiers": [
			{"user": u, "full_name": cashier_names.get(u, u)} for u in cashier_ids
		],
		"open_sessions": sum(1 for o in openings if o.status == "Open"),
		"closed_sessions": sum(1 for o in openings if o.status != "Open"),
	}


def _empty_session():
	return {
		"has_session": False,
		"opening_balance": 0,
		"session_count": 0,
		"session_start": None,
		"session_end": None,
		"duration_hours": 0,
		"cashiers": [],
		"open_sessions": 0,
		"closed_sessions": 0,
	}


# ---------------------------------------------------------------------------
# Section B — Revenue Summary (with hourly breakdown + YoY/WoW deltas)
# ---------------------------------------------------------------------------


def _eod_revenue(target, store, user_roles, user):
	"""Gross/net sales, tax, txn count, avg ticket, peak hour, YoY/WoW."""
	from frappe.utils import add_days, flt

	if not (user_roles & (SALES_ROLES | ACCOUNTING_ROLES | ADMIN_ROLES)):
		return _empty_revenue()

	owner_clause, owner_params = _eod_owner_clause(user_roles, user, "si")

	row = frappe.db.sql(
		f"""SELECT
			COUNT(*) AS cnt,
			COALESCE(SUM(grand_total), 0) AS gross,
			COALESCE(SUM(net_total), 0) AS net,
			COALESCE(SUM(total_taxes_and_charges), 0) AS tax,
			COALESCE(SUM(CASE WHEN is_return = 1 THEN ABS(grand_total) ELSE 0 END), 0) AS refunds,
			COALESCE(SUM(CASE WHEN is_return = 0 THEN grand_total ELSE 0 END), 0) AS gross_sales
		FROM `tabSales Invoice` si
		WHERE si.docstatus = 1 AND si.is_pos = 1
		AND si.posting_date = %s{owner_clause}""",
		(target, *owner_params),
		as_dict=True,
	)
	r = row[0] if row else {}
	cnt = r.get("cnt") or 0
	gross_sales = flt(r.get("gross_sales"))
	refunds = flt(r.get("refunds"))
	net_sales = gross_sales - refunds
	tax = flt(r.get("tax"))

	hourly = _eod_hourly_breakdown(target, owner_clause, owner_params)
	peak = max(hourly, key=lambda h: h["count"]) if hourly else None

	yoy = _eod_compare_deltas(target, add_days(target, -365), user_roles, user, owner_clause)
	wow = _eod_compare_deltas(target, add_days(target, -7), user_roles, user, owner_clause)

	return {
		"gross_sales": gross_sales,
		"refunds": refunds,
		"net_sales": net_sales,
		"tax_collected": tax,
		"transaction_count": cnt,
		"avg_ticket": round(gross_sales / cnt, 2) if cnt else 0,
		"peak_hour": peak,
		"hourly_breakdown": hourly,
		"yoy": yoy,
		"wow": wow,
	}


def _empty_revenue():
	return {
		"gross_sales": 0,
		"refunds": 0,
		"net_sales": 0,
		"tax_collected": 0,
		"transaction_count": 0,
		"avg_ticket": 0,
		"peak_hour": None,
		"hourly_breakdown": [],
		"yoy": {"this": 0, "compare": 0, "pct": 0},
		"wow": {"this": 0, "compare": 0, "pct": 0},
	}


def _eod_hourly_breakdown(target, owner_clause, owner_params):
	"""Sales transaction count + total grouped by hour-of-day."""
	from frappe.utils import flt

	rows = frappe.db.sql(
		f"""SELECT HOUR(posting_time) AS hour,
			COUNT(*) AS cnt,
			COALESCE(SUM(grand_total), 0) AS total
		FROM `tabSales Invoice` si
		WHERE si.docstatus = 1 AND si.is_pos = 1
		AND si.posting_date = %s AND is_return = 0{owner_clause}
		GROUP BY HOUR(posting_time)
		ORDER BY hour""",
		(target, *owner_params),
		as_dict=True,
	)
	return [
		{"hour": int(r.hour), "count": r.cnt, "total": flt(r.total)} for r in rows
	]


def _eod_compare_deltas(this_date, compare_date, user_roles, user, owner_clause):
	"""YoY / WoW: this-day total vs compare-day total with pct delta."""
	from frappe.utils import flt

	def _total(d):
		row = frappe.db.sql(
			f"""SELECT COALESCE(SUM(CASE WHEN is_return = 0 THEN grand_total ELSE 0 END), 0) AS total
			FROM `tabSales Invoice` si
			WHERE si.docstatus = 1 AND si.is_pos = 1
			AND si.posting_date = %s{owner_clause}""",
			(d, *_eod_owner_clause(user_roles, user, "si")[1]),
			as_dict=True,
		)
		return flt(row[0].total) if row else 0

	this_val = _total(this_date)
	compare_val = _total(compare_date)
	pct = round(((this_val - compare_val) / compare_val) * 100, 1) if compare_val else 0
	return {"this": this_val, "compare": compare_val, "compare_date": compare_date, "pct": pct}


# ---------------------------------------------------------------------------
# Section C — Transaction Stream Breakdown (jewelry-specific)
# ---------------------------------------------------------------------------


def _eod_transaction_streams(target, store, user_roles, user):
	"""Breakdown per revenue stream: sales, repairs, layaway, trade-in, gold, gift cards."""
	from frappe.utils import flt

	owner_clause, owner_params = _eod_owner_clause(user_roles, user, "si")
	can_sales = bool(user_roles & (SALES_ROLES | ACCOUNTING_ROLES | ADMIN_ROLES))
	has_stream = _eod_si_has_stream_field()

	streams: dict[str, Any] = {}

	# Jewelry Sales (when the stream field is absent, all POS sales are treated
	# as jewelry sales — the default stream)
	if can_sales:
		stream_clause = " AND si.custom_transaction_stream = 'Jewelry Sale'" if has_stream else ""
		row = frappe.db.sql(
			f"""SELECT COUNT(*) AS cnt, COALESCE(SUM(grand_total), 0) AS total
			FROM `tabSales Invoice` si
			WHERE si.docstatus = 1 AND si.is_pos = 1 AND is_return = 0
			AND si.posting_date = %s{stream_clause}{owner_clause}""",
			(target, *owner_params),
			as_dict=True,
		)
		r = row[0] if row else {}
		streams["jewelry_sales"] = {
			"count": r.cnt or 0,
			"total": flt(r.total),
			"avg_ticket": round(flt(r.total) / r.cnt, 2) if r.cnt else 0,
		}
	else:
		streams["jewelry_sales"] = {"count": 0, "total": 0, "avg_ticket": 0}

	# Repairs
	streams["repairs"] = _eod_repair_stream(target, user_roles)

	# Custom Orders (no dedicated doctype in this system — graceful zeros)
	streams["custom_orders"] = {"count": 0, "total_deposits": 0}

	# Layaway
	streams["layaway"] = _eod_layaway_stream(target, store, user_roles, user, owner_clause, owner_params, has_stream)

	# Trade-Ins (credit taken today via Sales Invoice Payment 'Trade-In')
	streams["trade_ins"] = _eod_trade_in_stream(target, owner_clause, owner_params, can_sales)

	# Gold Purchases
	streams["gold_purchases"] = _eod_gold_purchase_stream(target, store, user_roles)

	# Gift Cards
	streams["gift_cards"] = _eod_gift_card_stream(target, owner_clause, owner_params, can_sales)

	return streams


def _eod_repair_stream(target, user_roles):
	from frappe.utils import flt

	if not (user_roles & (SALES_ROLES | HR_ROLES | ACCOUNTING_ROLES | ADMIN_ROLES)):
		return {"count": 0, "total_revenue": 0, "completed_today": 0, "active": 0}

	completed = frappe.db.sql(
		"""SELECT COUNT(*) AS cnt, COALESCE(SUM(estimated_cost), 0) AS revenue
		FROM `tabRepair Order`
		WHERE docstatus < 2 AND DATE(completed_date) = %s""",
		(target,),
		as_dict=True,
	)
	active = frappe.db.sql(
		"""SELECT COUNT(*) AS cnt FROM `tabRepair Order`
		WHERE docstatus < 2 AND status NOT IN ('Delivered', 'Cancelled')""",
		as_dict=True,
	)
	# Revenue mirrors the Daily Brief definition: ready-for-pickup, modified today
	revenue = frappe.db.sql(
		"""SELECT COALESCE(SUM(estimated_cost), 0) AS revenue
		FROM `tabRepair Order`
		WHERE docstatus < 2 AND status = 'Ready for Pickup' AND DATE(modified) = %s""",
		(target,),
		as_dict=True,
	)
	c = completed[0] if completed else {}
	return {
		"count": c.cnt or 0,
		"total_revenue": flt((revenue[0].revenue if revenue else 0)),
		"completed_today": c.cnt or 0,
		"active": (active[0].cnt if active else 0),
	}


def _eod_layaway_stream(target, store, user_roles, user, owner_clause, owner_params, has_stream=True):
	from frappe.utils import flt

	if not (user_roles & (SALES_ROLES | ACCOUNTING_ROLES | ADMIN_ROLES)):
		return {"new_contracts": 0, "deposits_collected": 0, "matured_today": 0, "active": 0}

	store_clause, store_params = _eod_store_location_clause(store)

	new_row = frappe.db.sql(
		f"""SELECT COUNT(*) AS cnt, COALESCE(SUM(deposit_amount), 0) AS deposits
		FROM `tabLayaway Contract`
		WHERE docstatus = 1 AND contract_date = %s{store_clause}""",
		(target, *store_params),
		as_dict=True,
	)
	nr = new_row[0] if new_row else {}

	# Deposits collected today via the layaway-deposit payment stream (only
	# available when the stream field exists on Sales Invoice)
	deposits_total = 0.0
	if has_stream:
		deposits = frappe.db.sql(
			f"""SELECT COALESCE(SUM(sip.amount), 0) AS total
			FROM `tabSales Invoice Payment` sip
			JOIN `tabSales Invoice` si ON sip.parent = si.name
			WHERE si.docstatus = 1 AND si.custom_transaction_stream = 'Layaway Deposit'
			AND si.posting_date = %s{owner_clause}""",
			(target, *owner_params),
			as_dict=True,
		)
		deposits_total = flt(deposits[0].total) if deposits else 0

	matured = frappe.db.sql(
		f"""SELECT COUNT(*) AS cnt FROM `tabLayaway Contract`
		WHERE docstatus = 1 AND status = 'Completed'
		AND DATE(modified) = %s{store_clause}""",
		(target, *store_params),
		as_dict=True,
	)
	active = frappe.db.sql(
		f"""SELECT COUNT(*) AS cnt FROM `tabLayaway Contract`
		WHERE docstatus = 1 AND status = 'Active'{store_clause}""",
		(*store_params,),
		as_dict=True,
	)
	return {
		"new_contracts": nr.cnt or 0,
		"deposits_collected": deposits_total,
		"matured_today": (matured[0].cnt if matured else 0),
		"active": (active[0].cnt if active else 0),
	}


def _eod_trade_in_stream(target, owner_clause, owner_params, can_sales):
	from frappe.utils import flt

	if not can_sales:
		return {"count": 0, "total_value": 0}

	# Trade-in credit recorded as a tender on POS invoices
	row = frappe.db.sql(
		f"""SELECT COUNT(DISTINCT sip.parent) AS cnt, COALESCE(SUM(sip.amount), 0) AS total
		FROM `tabSales Invoice Payment` sip
		JOIN `tabSales Invoice` si ON sip.parent = si.name
		WHERE si.docstatus = 1 AND si.is_pos = 1 AND is_return = 0
		AND sip.mode_of_payment = 'Trade-In'
		AND si.posting_date = %s{owner_clause}""",
		(target, *owner_params),
		as_dict=True,
	)
	r = row[0] if row else {}
	# Also count standalone Trade In Records created today (best-effort)
	record_count = 0
	if frappe.db.table_exists("tabTrade In Record"):
		rec = frappe.db.sql(
			"SELECT COUNT(*) AS cnt FROM `tabTrade In Record` WHERE DATE(creation) = %s",
			(target,),
			as_dict=True,
		)
		record_count = (rec[0].cnt if rec else 0) or 0
	return {
		"count": (r.cnt or 0) or record_count,
		"invoice_count": r.cnt or 0,
		"record_count": record_count,
		"total_value": flt(r.total),
	}


def _eod_gold_purchase_stream(target, store, user_roles):
	from frappe.utils import flt

	if not (user_roles & (SALES_ROLES | ACCOUNTING_ROLES | ADMIN_ROLES)):
		return {"count": 0, "total_weight_g": 0, "total_value": 0}

	store_clause, store_params = _eod_store_location_clause(store)
	row = frappe.db.sql(
		f"""SELECT COUNT(*) AS cnt,
			COALESCE(SUM(total_gross_weight), 0) AS weight,
			COALESCE(SUM(total_agreed_value), 0) AS total
		FROM `tabGold Purchase`
		WHERE docstatus = 1 AND DATE(purchase_date) = %s{store_clause}""",
		(target, *store_params),
		as_dict=True,
	)
	r = row[0] if row else {}
	return {
		"count": r.cnt or 0,
		"total_weight_g": flt(r.weight),
		"total_value": flt(r.total),
	}


def _eod_gift_card_stream(target, owner_clause, owner_params, can_sales):
	from frappe.utils import flt

	if not can_sales:
		return {"sold": {"count": 0, "amount": 0}, "redeemed": {"count": 0, "amount": 0}}

	# Sold today (issued via purchase)
	sold = frappe.db.sql(
		"""SELECT COUNT(*) AS cnt, COALESCE(SUM(initial_value), 0) AS amount
		FROM `tabGift Card`
		WHERE docstatus < 2 AND source = 'Purchase' AND issue_date = %s""",
		(target,),
		as_dict=True,
	)
	sr = sold[0] if sold else {}
	# Redeemed today via gift-card tender on POS invoices
	redeemed = frappe.db.sql(
		f"""SELECT COUNT(DISTINCT sip.parent) AS cnt, COALESCE(SUM(sip.amount), 0) AS amount
		FROM `tabSales Invoice Payment` sip
		JOIN `tabSales Invoice` si ON sip.parent = si.name
		WHERE si.docstatus = 1 AND si.is_pos = 1 AND is_return = 0
		AND sip.mode_of_payment = 'Gift Card'
		AND si.posting_date = %s{owner_clause}""",
		(target, *owner_params),
		as_dict=True,
	)
	rr = redeemed[0] if redeemed else {}
	return {
		"sold": {"count": sr.cnt or 0, "amount": flt(sr.amount)},
		"redeemed": {"count": rr.cnt or 0, "amount": flt(rr.amount)},
	}


def _eod_store_location_clause(store):
	"""Return ``(sql_fragment, params)`` filtering a ``store_location`` column."""
	if not store:
		return "", []
	return " AND store_location = %s", [store]


# ---------------------------------------------------------------------------
# Section D — Payment Method (Tender) Breakdown
# ---------------------------------------------------------------------------


def _eod_tender_breakdown(target, store, user_roles, user):
	"""Per-tender totals + grouped split + financing approvals."""
	from frappe.utils import flt

	from zevar_core.constants import FINANCING_WATERFALL

	if not _eod_can_see_financials(user_roles):
		return {"methods": [], "groups": {}, "financing": [], "total": 0}

	owner_clause, owner_params = _eod_owner_clause(user_roles, user, "si")
	rows = frappe.db.sql(
		f"""SELECT sip.mode_of_payment AS method,
			COUNT(*) AS cnt,
			COALESCE(SUM(sip.amount), 0) AS total
		FROM `tabSales Invoice Payment` sip
		JOIN `tabSales Invoice` si ON sip.parent = si.name
		WHERE si.docstatus = 1 AND si.is_pos = 1 AND is_return = 0
		AND si.posting_date = %s{owner_clause}
		GROUP BY sip.mode_of_payment
		ORDER BY total DESC""",
		(target, *owner_params),
		as_dict=True,
	)

	total_collected = flt(sum(flt(r.total) for r in rows))
	methods = []
	for r in rows:
		methods.append({
			"method": r.method,
			"count": r.cnt,
			"total": flt(r.total),
			"pct": round(flt(r.total) / total_collected * 100, 1) if total_collected else 0,
		})

	# Grouped split
	financing_set = set(FINANCING_WATERFALL)
	groups: dict[str, dict] = {}
	for key, modes in EOD_TENDER_GROUPS.items():
		applicable = financing_set if key == "financing" else set(modes)
		groups[key] = {
			"total": sum(m["total"] for m in methods if m["method"] in applicable),
			"count": sum(m["count"] for m in methods if m["method"] in applicable),
		}

	# Financing approvals today (per provider)
	financing = []
	if frappe.db.table_exists("tabFinancing Application"):
		for provider in FINANCING_WATERFALL:
			row = frappe.db.sql(
				"""SELECT COUNT(*) AS cnt, COALESCE(SUM(financed_amount), 0) AS total
				FROM `tabFinancing Application`
				WHERE status = 'Approved' AND provider = %s AND DATE(approval_date) = %s""",
				(provider, target),
				as_dict=True,
			)
			r = row[0] if row else {}
			financing.append({
				"provider": provider,
				"approved_count": r.cnt or 0,
				"total_financed": flt(r.total),
			})

	return {
		"methods": methods,
		"groups": groups,
		"financing": financing,
		"total": total_collected,
	}


# ---------------------------------------------------------------------------
# Section E — Cash Drawer Reconciliation
# ---------------------------------------------------------------------------


def _eod_cash_reconciliation(target, store, user_roles, user):
	"""Opening float -> expected -> counted -> variance, from POS Opening/Closing entries."""
	from frappe.utils import flt

	if not _eod_can_see_financials(user_roles):
		return {"permitted": False, **_empty_cash_recon()}

	owner_clause, owner_params = ("", []) if _eod_can_see_store(user_roles) else (
		" AND poe.user = %s",
		[user],
	)

	# Opening float (sum of Cash balance_details for sessions opened that day)
	openings = frappe.db.sql(
		f"""SELECT poe.name, poe.pos_closing_entry, poe.user
		FROM `tabPOS Opening Entry` poe
		WHERE poe.docstatus = 1 AND DATE(poe.period_start_date) = %s{owner_clause}""",
		(target, *owner_params),
		as_dict=True,
	)
	opening_names = [o.name for o in openings]
	opening_float = 0.0
	counted_cash = 0.0
	expected_cash = 0.0
	denominations: list[dict] = []
	if opening_names:
		of = frappe.db.sql(
			"""SELECT COALESCE(SUM(opening_amount), 0) AS opening_amount
			FROM `tabPOS Opening Entry Detail`
			WHERE parent IN %s AND mode_of_payment = 'Cash'""",
			(opening_names,),
			as_dict=True,
		)
		opening_float = flt(of[0].opening_amount) if of else 0

		# Counted + expected from linked POS Closing Entries' payment_reconciliation
		closing_names = [o.pos_closing_entry for o in openings if o.pos_closing_entry]
		if closing_names:
			cr = frappe.db.sql(
				"""SELECT mode_of_payment,
					COALESCE(SUM(opening_amount), 0) AS opening,
					COALESCE(SUM(expected_amount), 0) AS expected,
					COALESCE(SUM(closing_amount), 0) AS closing
				FROM `tabPOS Closing Entry Detail`
				WHERE parent IN %s
				GROUP BY mode_of_payment""",
				(closing_names,),
				as_dict=True,
			)
			for c in cr:
				if c.mode_of_payment == "Cash":
					counted_cash += flt(c.closing)
					expected_cash += flt(c.expected)
					denominations.append({
						"mode_of_payment": "Cash",
						"opening": flt(c.opening),
						"expected": flt(c.expected),
						"counted": flt(c.closing),
					})

	# Cash sales + cash refunds directly from invoices (covers open / unclosed sessions)
	si_owner_clause, si_owner_params = _eod_owner_clause(user_roles, user, "si")
	cash_sales = frappe.db.sql(
		f"""SELECT COALESCE(SUM(sip.amount), 0) AS total
		FROM `tabSales Invoice Payment` sip
		JOIN `tabSales Invoice` si ON sip.parent = si.name
		WHERE si.docstatus = 1 AND si.is_pos = 1 AND is_return = 0
		AND sip.mode_of_payment = 'Cash' AND si.posting_date = %s{si_owner_clause}""",
		(target, *si_owner_params),
		as_dict=True,
	)
	cash_sales_total = flt(cash_sales[0].total) if cash_sales else 0
	cash_refunds = frappe.db.sql(
		f"""SELECT COALESCE(SUM(sip.amount), 0) AS total
		FROM `tabSales Invoice Payment` sip
		JOIN `tabSales Invoice` si ON sip.parent = si.name
		WHERE si.docstatus = 1 AND si.is_pos = 1 AND is_return = 1
		AND sip.mode_of_payment = 'Cash' AND si.posting_date = %s{si_owner_clause}""",
		(target, *si_owner_params),
		as_dict=True,
	)
	cash_refunds_total = flt(cash_refunds[0].total) if cash_refunds else 0

	# If no closing entries yet, expected falls back to opening float + cash sales
	if expected_cash == 0:
		expected_cash = opening_float + cash_sales_total - cash_refunds_total
	if counted_cash == 0:
		# Session not yet closed; counted unknown
		counted_cash = 0.0

	variance = counted_cash - expected_cash if counted_cash else 0.0
	threshold = _eod_variance_threshold()
	variance_status = "balanced"
	if variance > 0:
		variance_status = "excess"
	elif variance < 0:
		variance_status = "short"

	return {
		"permitted": True,
		"opening_float": opening_float,
		"cash_sales": cash_sales_total,
		"cash_refunds": cash_refunds_total,
		"cash_drops_payouts": 0,  # no dedicated payout doctype; reserved
		"expected_closing": expected_cash,
		"counted_closing": counted_cash,
		"variance": round(variance, 2),
		"variance_pct": round(abs(variance) / expected_cash * 100, 1) if expected_cash else 0,
		"variance_status": variance_status,
		"override_required": abs(variance) > threshold if counted_cash else False,
		"threshold": threshold,
		"denominations": denominations,
		"session_closed": bool(counted_cash),
	}


def _empty_cash_recon():
	return {
		"opening_float": 0,
		"cash_sales": 0,
		"cash_refunds": 0,
		"cash_drops_payouts": 0,
		"expected_closing": 0,
		"counted_closing": 0,
		"variance": 0,
		"variance_pct": 0,
		"variance_status": "balanced",
		"override_required": False,
		"threshold": EOD_DEFAULT_VARIANCE_THRESHOLD,
		"denominations": [],
		"session_closed": False,
	}


def _eod_variance_threshold():
	"""Best-effort threshold from any POS Profile configured variance setting."""
	try:
		val = frappe.db.get_value(
			"POS Profile",
			{"custom_enforce_fixed_float": 1},
			"custom_variance_alert_threshold",
		)
		return flt(val) if val is not None else EOD_DEFAULT_VARIANCE_THRESHOLD
	except Exception:
		return EOD_DEFAULT_VARIANCE_THRESHOLD


# ---------------------------------------------------------------------------
# Section F — Audit Trail
# ---------------------------------------------------------------------------


def _eod_audit_trail(target, store, user_roles, user):
	"""Voids, refunds, discounts, manager overrides, price overrides."""
	from frappe.utils import flt

	if not (user_roles & (MANAGER_ROLES | ACCOUNTING_ROLES | ADMIN_ROLES)):
		return {"permitted": False, "voids": {}, "refunds": {}, "discounts": {}, "manager_overrides": {}, "price_overrides": {}}

	owner_clause, owner_params = _eod_owner_clause(user_roles, user, "si")

	# Voids = cancelled POS invoices today (use posting_date / creation fallback)
	voids = _audit_voids(target, owner_clause, owner_params)
	# Refunds / returns
	refunds = _audit_refunds(target, owner_clause, owner_params)
	# Discounts applied
	discounts = _audit_discounts(target, owner_clause, owner_params)
	# Manager overrides
	manager_overrides = _audit_manager_overrides(target)
	# Price overrides (subset of overrides / audit log)
	price_overrides = _audit_price_overrides(target)

	return {
		"permitted": True,
		"voids": voids,
		"refunds": refunds,
		"discounts": discounts,
		"manager_overrides": manager_overrides,
		"price_overrides": price_overrides,
	}


def _audit_voids(target, owner_clause, owner_params):
	from frappe.utils import flt

	row = frappe.db.sql(
		f"""SELECT COUNT(*) AS cnt, COALESCE(SUM(ABS(grand_total)), 0) AS total
		FROM `tabSales Invoice` si
		WHERE si.docstatus = 2 AND si.is_pos = 1
		AND si.posting_date = %s{owner_clause}""",
		(target, *owner_params),
		as_dict=True,
	)
	r = row[0] if row else {}
	reasons = _audit_log_reasons(
		target, ("invoice_voided", "invoice_cancelled")
	)
	return {"count": r.cnt or 0, "total": flt(r.total), "reasons": reasons}


def _audit_refunds(target, owner_clause, owner_params):
	from frappe.utils import flt

	row = frappe.db.sql(
		f"""SELECT COUNT(*) AS cnt, COALESCE(SUM(ABS(grand_total)), 0) AS total
		FROM `tabSales Invoice` si
		WHERE si.docstatus = 1 AND si.is_pos = 1 AND is_return = 1
		AND si.posting_date = %s{owner_clause}""",
		(target, *owner_params),
		as_dict=True,
	)
	r = row[0] if row else {}
	# Items returned (qty across return invoice items)
	items = 0
	if r.cnt:
		qty = frappe.db.sql(
			f"""SELECT COALESCE(SUM(sii.qty), 0) AS qty
			FROM `tabSales Invoice Item` sii
			JOIN `tabSales Invoice` si ON sii.parent = si.name
			WHERE si.docstatus = 1 AND is_return = 1 AND si.posting_date = %s{owner_clause}""",
			(target, *owner_params),
			as_dict=True,
		)
		items = flt(qty[0].qty) if qty else 0
	reasons = _audit_log_reasons(target, ("invoice_returned", "payment_refunded"))
	return {"count": r.cnt or 0, "total": flt(r.total), "items_returned": items, "reasons": reasons}


def _audit_discounts(target, owner_clause, owner_params):
	from frappe.utils import flt

	has_discount = frappe.get_meta("Sales Invoice").has_field("is_discounted")
	if not has_discount:
		return {"count": 0, "total": 0, "top_reasons": []}
	row = frappe.db.sql(
		f"""SELECT COUNT(*) AS cnt, COALESCE(SUM(ABS(discount_amount)), 0) AS total
		FROM `tabSales Invoice` si
		WHERE si.docstatus = 1 AND si.is_pos = 1 AND is_return = 0
		AND si.is_discounted = 1 AND si.posting_date = %s{owner_clause}""",
		(target, *owner_params),
		as_dict=True,
	)
	r = row[0] if row else {}
	top_reasons = _audit_log_reasons(
		target, ("discount_applied", "large_discount_applied", "discount_override_approved")
	)
	return {"count": r.cnt or 0, "total": flt(r.total), "top_reasons": top_reasons}


def _audit_manager_overrides(target):
	"""Approved manager overrides today, grouped by approver."""
	if not frappe.db.table_exists("tabPOS Manager Override"):
		return {"count": 0, "by_approver": [], "recent": []}
	rows = frappe.db.sql(
		"""SELECT action, reason, requested_by, approved_by, reference_document
		FROM `tabPOS Manager Override`
		WHERE status = 'Approved' AND DATE(approval_time) = %s
		ORDER BY approval_time DESC LIMIT 50""",
		(target,),
		as_dict=True,
	)
	by_approver: dict[str, int] = {}
	for r in rows:
		who = r.approved_by or r.requested_by or "Unknown"
		by_approver[who] = by_approver.get(who, 0) + 1
	return {
		"count": len(rows),
		"by_approver": [{"user": k, "count": v} for k, v in sorted(by_approver.items(), key=lambda x: -x[1])],
		"recent": rows,
	}


def _audit_price_overrides(target):
	"""Price/line-item overrides via audit log."""
	rows = frappe.db.sql(
		"""SELECT timestamp, user, details, reference_document
		FROM `tabPOS Audit Log`
		WHERE event_type IN ('discount_override_approved', 'manager_override_approved')
		AND DATE(timestamp) = %s
		ORDER BY timestamp DESC LIMIT 50""",
		(target,),
		as_dict=True,
	)
	return {"count": len(rows), "recent": rows}


def _audit_log_reasons(target, event_types):
	"""Top reasons from POS Audit Log for the given event types today."""
	if not event_types:
		return []
	rows = frappe.db.sql(
		"""SELECT details, COUNT(*) AS cnt
		FROM `tabPOS Audit Log`
		WHERE event_type IN %s AND DATE(timestamp) = %s
		GROUP BY details ORDER BY cnt DESC LIMIT 5""",
		(tuple(event_types), target),
		as_dict=True,
	)
	return [{"reason": r.details or "(no detail)", "count": r.cnt} for r in rows]


# ---------------------------------------------------------------------------
# Section G — Salesperson Performance
# ---------------------------------------------------------------------------


def _eod_salesperson_performance(target, store, user_roles, user):
	"""Per-person transaction count, total, avg ticket, commission."""
	from frappe.utils import flt

	if not (user_roles & (MANAGER_ROLES | ACCOUNTING_ROLES | ADMIN_ROLES)):
		return {"permitted": False, "salespeople": [], "top_by_revenue": None, "top_by_count": None}

	owner_clause, owner_params = ("", []) if _eod_can_see_store(user_roles) else (
		" AND owner = %s",
		[user],
	)

	rows = frappe.db.sql(
		f"""SELECT owner,
			COUNT(*) AS cnt,
			COALESCE(SUM(CASE WHEN is_return = 0 THEN grand_total ELSE 0 END), 0) AS total
		FROM `tabSales Invoice` si
		WHERE si.docstatus = 1 AND si.is_pos = 1
		AND si.posting_date = %s{owner_clause}
		GROUP BY owner""",
		(target, *owner_params),
		as_dict=True,
	)

	# Owner -> full name
	owners = [r.owner for r in rows if r.owner]
	name_map = {}
	if owners:
		users = frappe.get_all("User", filters={"name": ["in", owners]}, fields=["name", "full_name"])
		name_map = {u.name: u.full_name or u.name for u in users}

	# Commission per employee (mapped to user via Employee.user_id where possible)
	commission_map = _commission_by_user(target)

	salespeople = []
	for r in rows:
		total = flt(r.total)
		cnt = r.cnt or 0
		salespeople.append({
			"user": r.owner,
			"name": name_map.get(r.owner, r.owner),
			"transaction_count": cnt,
			"total_sales": total,
			"avg_ticket": round(total / cnt, 2) if cnt else 0,
			"commission_earned": commission_map.get(r.owner, 0),
		})
	salespeople.sort(key=lambda s: s["total_sales"], reverse=True)

	top_rev = salespeople[0] if salespeople else None
	by_count = sorted(salespeople, key=lambda s: s["transaction_count"], reverse=True)
	top_cnt = by_count[0] if by_count else None

	total_commission = round(sum(s["commission_earned"] for s in salespeople), 2)
	return {
		"permitted": True,
		"salespeople": salespeople,
		"top_by_revenue": top_rev,
		"top_by_count": top_cnt,
		"total_commission": total_commission,
	}


def _commission_by_user(target):
	"""Map Sales Invoice owner -> commission earned today via Employee.user_id."""
	from frappe.utils import flt

	if not frappe.db.table_exists("tabSales Commission Split"):
		return {}
	splits = frappe.db.sql(
		"""SELECT employee, COALESCE(SUM(commission_amount), 0) AS commission
		FROM `tabSales Commission Split`
		WHERE docstatus < 2 AND posting_date = %s
		GROUP BY employee""",
		(target,),
		as_dict=True,
	)
	if not splits:
		return {}
	emp_ids = [s.employee for s in splits if s.employee]
	user_map = {}
	if emp_ids:
		emps = frappe.get_all("Employee", filters={"name": ["in", emp_ids]}, fields=["name", "user_id"])
		user_map = {e.name: e.user_id for e in emps if e.user_id}
	return {user_map.get(s.employee, s.employee): flt(s.commission) for s in splits}


# ---------------------------------------------------------------------------
# Section H — Inventory Impact
# ---------------------------------------------------------------------------


def _eod_inventory_impact(target, store, user_roles, user):
	"""Items sold/returned, low stock, high-value items, net change."""
	from frappe.utils import flt

	if not (user_roles & (STOCK_ROLES | MANAGER_ROLES | ACCOUNTING_ROLES | ADMIN_ROLES)):
		return {"permitted": False, "items_sold": 0, "items_returned": 0, "low_stock_count": 0,
				"low_stock": [], "high_value_items": [], "net_change": 0}

	owner_clause, owner_params = _eod_owner_clause(user_roles, user, "si")

	sold = frappe.db.sql(
		f"""SELECT COALESCE(SUM(sii.qty), 0) AS qty
		FROM `tabSales Invoice Item` sii
		JOIN `tabSales Invoice` si ON sii.parent = si.name
		WHERE si.docstatus = 1 AND si.is_pos = 1 AND is_return = 0
		AND si.posting_date = %s{owner_clause}""",
		(target, *owner_params),
		as_dict=True,
	)
	returned = frappe.db.sql(
		f"""SELECT COALESCE(SUM(sii.qty), 0) AS qty
		FROM `tabSales Invoice Item` sii
		JOIN `tabSales Invoice` si ON sii.parent = si.name
		WHERE si.docstatus = 1 AND is_return = 1
		AND si.posting_date = %s{owner_clause}""",
		(target, *owner_params),
		as_dict=True,
	)
	items_sold = flt(sold[0].qty) if sold else 0
	items_returned = flt(returned[0].qty) if returned else 0

	# High-value items sold today
	high_value = _high_value_items(target, owner_clause, owner_params)

	# Low stock
	low_stock_count, low_stock = _low_stock_items(store, user_roles)

	return {
		"permitted": True,
		"items_sold": items_sold,
		"items_returned": items_returned,
		"net_change": items_sold - items_returned,
		"high_value_threshold": EOD_HIGH_VALUE_ITEM_THRESHOLD,
		"high_value_items": high_value,
		"low_stock_count": low_stock_count,
		"low_stock": low_stock,
	}


def _high_value_items(target, owner_clause, owner_params):
	from frappe.utils import flt

	rows = frappe.db.sql(
		f"""SELECT sii.item_code, sii.item_name, sii.qty, sii.rate, sii.amount, sii.parent
		FROM `tabSales Invoice Item` sii
		JOIN `tabSales Invoice` si ON sii.parent = si.name
		WHERE si.docstatus = 1 AND si.is_pos = 1 AND is_return = 0
		AND sii.rate >= %s AND si.posting_date = %s{owner_clause}
		ORDER BY sii.rate DESC LIMIT 25""",
		(EOD_HIGH_VALUE_ITEM_THRESHOLD, target, *owner_params),
		as_dict=True,
	)
	return [
		{
			"item_code": r.item_code,
			"item_name": r.item_name,
			"qty": flt(r.qty),
			"rate": flt(r.rate),
			"amount": flt(r.amount),
			"invoice": r.parent,
		}
		for r in rows
	]


def _low_stock_items(store, user_roles):
	"""Items at/below reorder level (falls back to qty<=2 if no reorder level)."""
	warehouse_clause = ""
	params: list = []
	if store:
		warehouse_clause = " AND warehouse LIKE %s"
		params = [f"%{store}%"]
	has_reorder = frappe.get_meta("Bin").has_field("reorder_level") if frappe.db.table_exists("tabBin") else False
	threshold_expr = "reorder_level" if has_reorder else "2"
	rows = frappe.db.sql(
		f"""SELECT item_code, warehouse, actual_qty, {threshold_expr} AS threshold
		FROM `tabBin`
		WHERE actual_qty <= {threshold_expr}{warehouse_clause}
		ORDER BY actual_qty ASC LIMIT 50""",
		tuple(params),
		as_dict=True,
	)
	return len(rows), rows


# ---------------------------------------------------------------------------
# Section I — Repair Status
# ---------------------------------------------------------------------------


def _eod_repair_status(target, store, user_roles, user):
	"""Repair pipeline: new, completed, delivered, active, overdue."""
	from frappe.utils import flt, getdate

	if not (user_roles & (SALES_ROLES | HR_ROLES | ACCOUNTING_ROLES | ADMIN_ROLES)):
		return {"permitted": False, "new_today": 0, "completed_today": 0, "delivered_today": 0,
				"active": 0, "overdue": 0, "oldest_overdue": None}

	def _count(where, params):
		row = frappe.db.sql(
			f"""SELECT COUNT(*) AS cnt FROM `tabRepair Order` WHERE docstatus < 2 AND {where}""",
			tuple(params),
			as_dict=True,
		)
		return (row[0].cnt if row else 0) or 0

	new_today = _count("DATE(received_date) = %s", [target])
	completed_today = _count("DATE(completed_date) = %s", [target])
	delivered_today = _count("DATE(delivered_date) = %s", [target])
	active = _count("status NOT IN ('Delivered', 'Cancelled')", [])
	overdue_row = frappe.db.sql(
		"""SELECT COUNT(*) AS cnt, MIN(promised_date) AS oldest
		FROM `tabRepair Order`
		WHERE docstatus < 2
		AND status NOT IN ('Ready for Pickup', 'Delivered', 'Cancelled')
		AND promised_date < %s""",
		(target,),
		as_dict=True,
	)
	overdue = 0
	oldest = None
	if overdue_row:
		overdue = overdue_row[0].cnt or 0
		oldest = str(getdate(overdue_row[0].oldest)) if overdue_row[0].oldest else None

	return {
		"permitted": True,
		"new_today": new_today,
		"completed_today": completed_today,
		"delivered_today": delivered_today,
		"active": active,
		"overdue": overdue,
		"oldest_overdue": oldest,
	}


# ---------------------------------------------------------------------------
# Section J — Operational Notes
# ---------------------------------------------------------------------------


def _eod_operational_notes(target, store, user_roles, user):
	"""Manager notes, flagged incidents, next-day schedule."""
	notes: list[str] = []

	# Pull remarks from closing/opening entries for the day (guarded — the
	# ``remarks`` field is optional and absent on stock ERPNext POS Closing Entry)
	if user_roles & (MANAGER_ROLES | ACCOUNTING_ROLES | ADMIN_ROLES):
		if frappe.get_meta("POS Opening Entry").has_field("remarks"):
			for r in frappe.db.sql(
				"""SELECT remarks FROM `tabPOS Opening Entry`
				WHERE docstatus = 1 AND DATE(period_start_date) = %s
				AND remarks IS NOT NULL AND remarks != ''""",
				(target,),
				as_dict=True,
			) or []:
				notes.append(r.remarks)
		if frappe.db.table_exists("tabPOS Closing Entry") and frappe.get_meta("POS Closing Entry").has_field("remarks"):
			for r in frappe.db.sql(
				"""SELECT remarks FROM `tabPOS Closing Entry`
				WHERE docstatus = 1 AND DATE(period_end_date) = %s
				AND remarks IS NOT NULL AND remarks != ''""",
				(target,),
				as_dict=True,
			) or []:
				notes.append(r.remarks)

	# Flagged incidents (warnings in the audit log today)
	incidents = []
	if frappe.db.table_exists("tabPOS Audit Log") and frappe.get_meta("POS Audit Log").has_field("severity"):
		incidents = frappe.db.sql(
			"""SELECT timestamp, user, event_type, details
			FROM `tabPOS Audit Log`
			WHERE severity = 'Warning' AND DATE(timestamp) = %s
			ORDER BY timestamp DESC LIMIT 20""",
			(target,),
			as_dict=True,
		)

	return {
		"manager_notes": notes,
		"flagged_incidents": incidents,
		"next_day_opening_schedule": None,  # no scheduling doctype; reserved
	}


# ---------------------------------------------------------------------------
# Print / Export — Z-Report PDF generation for email attachment
# ---------------------------------------------------------------------------


@frappe.whitelist(allow_guest=False)
def generate_eod_pdf(date: str | None = None, store: str | None = None) -> dict[str, Any]:
	"""Generate a Z-Report PDF for the EOD and return a download URL.

	Uses the existing ``eod_daily_brief`` print format scaffolding when
	available, otherwise falls back to Frappe's standard PDF rendering of the
	report dict as a simple HTML Z-Report.
	"""
	from frappe.utils import now_datetime

	user = frappe.session.user
	if not user or user == "Guest":
		frappe.throw("Login required", frappe.PermissionError)

	user_roles = set(frappe.get_roles(user))
	if not (user_roles & (MANAGER_ROLES | ACCOUNTING_ROLES | ADMIN_ROLES)):
		frappe.throw("Not authorised to export EOD report", frappe.PermissionError)

	target = _eod_resolve_date(date)
	report = get_eod_closeout_report(date=target, store=store)

	html = _render_eod_z_report_html(report)
	pdf_data = frappe.utils.pdf.get_pdf(html)

	# Attach to a one-off File so it can be downloaded / emailed.  Two paths are
	# tried so this works across Frappe versions.
	filename = f"EOD_ZReport_{target}.pdf"
	file_url = _eod_save_pdf_file(filename, pdf_data, user)
	return {
		"status": "generated",
		"file_name": filename,
		"file_url": file_url,
		"date": target,
		"generated_at": now_datetime().isoformat(),
	}


def _eod_save_pdf_file(filename: str, pdf_data: bytes, user: str) -> str:
	"""Persist a generated PDF as a private File attached to *user*."""
	try:
		from frappe.core.doctype.file.file import File

		f = frappe.get_doc({
			"doctype": "File",
			"file_name": filename,
			"attached_to_doctype": "User",
			"attached_to_name": user,
			"is_private": 1,
			"content": pdf_data,
		})
		f.insert(ignore_permissions=True)
		return f.file_url
	except Exception:
		from frappe.utils.file_manager import save_file

		saved = save_file(filename, pdf_data, "User", user, is_private=1, df=None)
		return saved.file_url


def _render_eod_z_report_html(report: dict) -> str:
	"""Render a clean, print-ready HTML Z-Report from the closeout dict."""
	rev = report.get("revenue", {}) or {}
	cash = report.get("cash_reconciliation", {}) or {}
	streams = report.get("transaction_streams", {}) or {}
	meta = report.get("meta", {}) or {}
	audit = report.get("audit_trail", {}) or {}

	def _money(v):
		try:
			return f"${flt(v):,.2f}"
		except Exception:
			return "$0.00"

	method_rows = "".join(
		f"<tr><td>{m.get('method','')}</td><td style='text-align:right'>{m.get('count',0)}</td>"
		f"<td style='text-align:right'>{_money(m.get('total',0))}</td>"
		f"<td style='text-align:right'>{m.get('pct',0)}%</td></tr>"
		for m in (report.get("payment_methods", {}) or {}).get("methods", [])
	)

	salespeople_rows = "".join(
		f"<tr><td>{s.get('name','')}</td><td style='text-align:right'>{s.get('transaction_count',0)}</td>"
		f"<td style='text-align:right'>{_money(s.get('total_sales',0))}</td>"
		f"<td style='text-align:right'>{_money(s.get('commission_earned',0))}</td></tr>"
		for s in (report.get("salesperson_performance", {}) or {}).get("salespeople", [])
	)

	return f"""
	<html><head><style>
		body {{ font-family: 'Courier New', monospace; font-size: 11px; color: #000; margin: 24px; }}
		h1 {{ text-align: center; font-size: 16px; margin: 0 0 4px; }}
		h2 {{ font-size: 12px; border-bottom: 1px solid #000; padding-bottom: 2px; margin: 14px 0 6px; }}
		table {{ width: 100%; border-collapse: collapse; }}
		td, th {{ padding: 2px 4px; }}
		.muted {{ color: #555; }}
		.center {{ text-align: center; }}
		.kpi {{ display: inline-block; width: 23%; text-align: center; margin: 4px 1%; }}
		.kpi b {{ font-size: 14px; display: block; }}
	</style></head><body>
		<h1>Z-REPORT — END OF DAY</h1>
		<p class="center muted">{report.get('date','')} &middot; {meta.get('primary_role','')} &middot; Generated {meta.get('generated_at','')}</p>

		<h2>Revenue</h2>
		<span class="kpi"><span class='muted'>Gross</span><b>{_money(rev.get('gross_sales',0))}</b></span>
		<span class="kpi"><span class='muted'>Net</span><b>{_money(rev.get('net_sales',0))}</b></span>
		<span class="kpi"><span class='muted'>Tax</span><b>{_money(rev.get('tax_collected',0))}</b></span>
		<span class="kpi"><span class='muted'>Txns</span><b>{rev.get('transaction_count',0)}</b></span>
		<p class="muted">Avg Ticket: {_money(rev.get('avg_ticket',0))} &middot; Refunds: {_money(rev.get('refunds',0))}
		&middot; YoY {rev.get('yoy',{}).get('pct',0)}% &middot; WoW {rev.get('wow',{}).get('pct',0)}%</p>

		<h2>Cash Drawer</h2>
		<table>
			<tr><td>Opening Float</td><td style='text-align:right'>{_money(cash.get('opening_float',0))}</td></tr>
			<tr><td>Cash Sales</td><td style='text-align:right'>{_money(cash.get('cash_sales',0))}</td></tr>
			<tr><td>Expected Closing</td><td style='text-align:right'>{_money(cash.get('expected_closing',0))}</td></tr>
			<tr><td>Counted Closing</td><td style='text-align:right'>{_money(cash.get('counted_closing',0))}</td></tr>
			<tr><td><b>Variance ({cash.get('variance_status','')})</b></td>
				<td style='text-align:right'><b>{_money(cash.get('variance',0))}</b></td></tr>
		</table>

		<h2>Streams</h2>
		<table>
			<tr><td>Jewelry Sales</td><td style='text-align:right'>{streams.get('jewelry_sales',{}).get('count',0)}</td>
				<td style='text-align:right'>{_money(streams.get('jewelry_sales',{}).get('total',0))}</td></tr>
			<tr><td>Repairs (completed)</td><td style='text-align:right'>{streams.get('repairs',{}).get('completed_today',0)}</td>
				<td style='text-align:right'>{_money(streams.get('repairs',{}).get('total_revenue',0))}</td></tr>
			<tr><td>Layaway Deposits</td><td style='text-align:right'>{streams.get('layaway',{}).get('new_contracts',0)}</td>
				<td style='text-align:right'>{_money(streams.get('layaway',{}).get('deposits_collected',0))}</td></tr>
			<tr><td>Trade-Ins</td><td style='text-align:right'>{streams.get('trade_ins',{}).get('count',0)}</td>
				<td style='text-align:right'>{_money(streams.get('trade_ins',{}).get('total_value',0))}</td></tr>
			<tr><td>Gold Purchases</td><td style='text-align:right'>{streams.get('gold_purchases',{}).get('count',0)}</td>
				<td style='text-align:right'>{_money(streams.get('gold_purchases',{}).get('total_value',0))}</td></tr>
		</table>

		<h2>Payment Methods</h2>
		<table><tr><th>Method</th><th style='text-align:right'>Count</th>
			<th style='text-align:right'>Total</th><th style='text-align:right'>%</th></tr>
			{method_rows}</table>

		<h2>Team Performance</h2>
		<table><tr><th>Salesperson</th><th style='text-align:right'>Txns</th>
			<th style='text-align:right'>Sales</th><th style='text-align:right'>Commission</th></tr>
			{salespeople_rows}</table>

		<h2>Audit</h2>
		<p class="muted">Voids: {audit.get('voids',{}).get('count',0)} &middot;
		Refunds: {audit.get('refunds',{}).get('count',0)} &middot;
		Discounts: {audit.get('discounts',{}).get('count',0)} &middot;
		Overrides: {audit.get('manager_overrides',{}).get('count',0)}</p>

		<p class="center muted">— End of Z-Report —</p>
	</body></html>
	"""
