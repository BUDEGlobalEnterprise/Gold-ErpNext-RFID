"""
Commission API - Commission calculation engine and query endpoints
"""

import frappe
from frappe import _
from frappe.utils import flt, today

# ---------------------------------------------------------------------------
# Query Endpoints
# ---------------------------------------------------------------------------


@frappe.whitelist(methods=["GET"])
def get_employee_commissions(employee: str, status: str = "") -> list:
	"""Return all commission splits for an employee, optionally filtered by status."""
	frappe.only_for(["Sales User", "Sales Manager", "System Manager", "HR User"])

	if not employee or not frappe.db.exists("Employee", employee):
		frappe.throw(_("Employee '{0}' not found.").format(employee))

	filters = {"employee": employee}
	if status:
		filters["status"] = status

	return frappe.get_all(
		"Sales Commission Split",
		filters=filters,
		fields=[
			"name",
			"sales_invoice",
			"posting_date",
			"sale_amount",
			"commission_rate",
			"commission_amount",
			"split_percent",
			"status",
		],
		order_by="posting_date desc",
	)


@frappe.whitelist(methods=["GET"])
def get_invoice_commissions(sales_invoice: str) -> list:
	"""Return all commission splits for a given Sales Invoice."""
	frappe.only_for(["Sales User", "Sales Manager", "System Manager"])

	if not sales_invoice or not frappe.db.exists("Sales Invoice", sales_invoice):
		frappe.throw(_("Sales Invoice '{0}' not found.").format(sales_invoice))

	return frappe.get_all(
		"Sales Commission Split",
		filters={"sales_invoice": sales_invoice},
		fields=[
			"name",
			"employee",
			"sale_amount",
			"commission_rate",
			"commission_amount",
			"split_percent",
			"status",
		],
	)


# ---------------------------------------------------------------------------
# Commission Calculation Hook (Sales Invoice on_submit)
# ---------------------------------------------------------------------------


def calculate_commissions(doc, method=None):
	"""
	Hook: Sales Invoice on_submit.
	Calculates commission for up to 4 salespersons based on applicable rules.
	"""
	if not doc.is_pos:
		return

	# Clean previous splits (handles amend scenarios)
	frappe.db.delete("Sales Commission Split", {"sales_invoice": doc.name})

	sales_persons = []
	for row in doc.get("custom_salesperson_splits") or []:
		if (
			hasattr(row, "employee")
			and row.employee
			and hasattr(row, "split_percent")
			and flt(row.split_percent) > 0
		):
			sales_persons.append({"employee": row.employee, "split_percent": flt(row.split_percent)})

	if not sales_persons:
		return

	net_total = flt(doc.base_net_total)
	if net_total <= 0:
		return

	# Compute discount percentage for discount-range rules
	discount_amount = flt(doc.discount_amount)
	discount_percent = (discount_amount / (net_total + discount_amount) * 100) if discount_amount else 0

	# Compute profit margin for profit-margin rules
	cogs = 0.0
	for item in doc.items:
		vr = flt(item.get("valuation_rate", 0)) if hasattr(item, "valuation_rate") else 0
		cogs += vr * flt(item.qty)
	total_profit = net_total - cogs
	profit_margin = (total_profit / net_total * 100) if net_total else 0

	for sp in sales_persons:
		rule = _get_applicable_rule(sp["employee"])
		if not rule:
			continue

		commission_rate = 0.0
		if rule.calculation_type == "Flat Rate":
			commission_rate = flt(rule.flat_rate)
		elif rule.calculation_type == "By Discount Range":
			commission_rate = _get_rate_from_tiers(rule.name, discount_percent)
		elif rule.calculation_type == "By Profit Margin":
			commission_rate = _get_rate_from_tiers(rule.name, profit_margin)
		elif rule.calculation_type == "By Sale Amount":
			commission_rate = _get_rate_from_tiers(rule.name, net_total)

		if commission_rate <= 0:
			continue

		sp_sale_amount = net_total * (sp["split_percent"] / 100)
		commission_amount = sp_sale_amount * commission_rate / 100

		split_doc = frappe.new_doc("Sales Commission Split")
		split_doc.sales_invoice = doc.name
		split_doc.employee = sp["employee"]
		split_doc.posting_date = doc.posting_date or today()
		split_doc.sale_amount = sp_sale_amount
		split_doc.split_percent = sp["split_percent"]
		split_doc.commission_rate = commission_rate
		split_doc.commission_amount = commission_amount
		split_doc.status = "Calculated"
		split_doc.insert(ignore_permissions=True)


# ---------------------------------------------------------------------------
# Helpers (single underscore — module-private, not name-mangled)
# ---------------------------------------------------------------------------


def _get_applicable_rule(employee: str):
	"""Find the commission rule for an employee, falling back to the default rule."""
	rule = frappe.get_all(
		"Commission Rule",
		filters={"employee": employee},
		fields=["name", "calculation_type", "flat_rate"],
		limit=1,
	)
	if rule:
		return rule[0]

	default = frappe.get_all(
		"Commission Rule",
		filters={"is_default": 1},
		fields=["name", "calculation_type", "flat_rate"],
		limit=1,
	)
	return default[0] if default else None


def _get_rate_from_tiers(rule_name: str, value: float) -> float:
	"""Look up a commission percentage from the tiered ranges on a rule."""
	ranges = frappe.get_all(
		"Commission Range",
		filters={"parent": rule_name},
		fields=["min_value", "max_value", "commission_percent"],
	)
	for r in ranges:
		if flt(r.min_value) <= value <= flt(r.max_value):
			return flt(r.commission_percent)
	return 0.0


@frappe.whitelist(methods=["GET"])
def get_invoice_commission_summary(sales_invoice: str) -> dict:
	"""
	Return a rich commission summary for a Sales Invoice including
	all splits, employee names, commission rules, and totals.
	"""
	frappe.only_for(["Sales User", "Sales Manager", "System Manager", "HR User"])

	if not sales_invoice or not frappe.db.exists("Sales Invoice", sales_invoice):
		frappe.throw(_("Sales Invoice '{0}' not found.").format(sales_invoice))

	# Fetch commission splits
	splits = frappe.get_all(
		"Sales Commission Split",
		filters={"sales_invoice": sales_invoice},
		fields=[
			"name",
			"employee",
			"sale_amount",
			"commission_rate",
			"commission_amount",
			"split_percent",
			"status",
		],
	)

	# Enrich with employee names
	employee_names = {}
	if splits:
		emp_ids = list({s.employee for s in splits if s.employee})
		if emp_ids:
			emps = frappe.get_all(
				"Employee",
				filters={"name": ["in", emp_ids]},
				fields=["name", "employee_name", "designation"],
			)
			employee_names = {e.name: e for e in emps}

	enriched_splits = []
	for s in splits:
		emp_info = employee_names.get(s.employee, {})
		s_dict = {
			"name": s.name,
			"employee": s.employee,
			"employee_name": emp_info.get("employee_name", s.employee),
			"designation": emp_info.get("designation", ""),
			"sale_amount": flt(s.sale_amount),
			"commission_rate": flt(s.commission_rate),
			"commission_amount": flt(s.commission_amount),
			"split_percent": flt(s.split_percent),
			"status": s.status,
		}
		enriched_splits.append(s_dict)

	# Get the salesperson configuration from the invoice
	salespersons_config = []
	si_meta = frappe.get_meta("Sales Invoice")
	if si_meta.has_field("custom_salesperson_splits"):
		config_rows = frappe.get_all(
			"Sales Invoice Salesperson Split",
			filters={"parent": sales_invoice, "parentfield": "custom_salesperson_splits"},
			fields=["employee", "split_percent"],
		)
		for row in config_rows:
			emp_info = employee_names.get(row.employee, {})
			salespersons_config.append(
				{
					"employee": row.employee,
					"employee_name": emp_info.get("employee_name", row.employee),
					"split_percent": flt(row.split_percent),
				}
			)

	return {
		"sales_invoice": sales_invoice,
		"splits": enriched_splits,
		"total_commission": sum(flt(s["commission_amount"]) for s in enriched_splits),
		"salespersons_config": salespersons_config,
	}
