"""
Expense API - Expense claim management for employee portal

Provides endpoints for listing expense claims, expense types,
creating new claims, and submitting them for approval.
"""

import frappe
from frappe import _
from frappe.utils import flt, today


@frappe.whitelist(methods=["GET"])
def get_expense_claims(employee: str | None = None, status: str | None = None) -> list:
	"""
	Get expense claims for an employee.

	Args:
		employee: Employee ID to filter claims
		status: Optional status filter (Draft, Pending, Approved, Rejected, Paid)

	Returns:
		List of expense claim dicts
	"""
	if not employee:
		user = frappe.session.user
		employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
		if not employee:
			return []

	filters = {"employee": employee, "docstatus": ["!=", 2]}
	if status:
		filters["status"] = status

	claims = frappe.get_all(
		"Expense Claim",
		filters=filters,
		fields=[
			"name",
			"employee",
			"employee_name",
			"expense_approver",
			"total_claimed_amount",
			"total_sanctioned_amount",
			"status",
			"posting_date",
			"company",
			"remark",
			"creation",
		],
		order_by="creation desc",
	)

	for claim in claims:
		claim.expenses = frappe.get_all(
			"Expense Claim Detail",
			filters={"parent": claim.name},
			fields=[
				"expense_type",
				"description",
				"amount",
				"sanctioned_amount",
				"cost_center",
			],
		)

	return claims


@frappe.whitelist(methods=["GET"])
def get_expense_types() -> list:
	"""
	Get available expense claim types.

	Returns:
		List of expense type dicts with name and description
	"""
	types = frappe.get_all(
		"Expense Claim Type",
		fields=["name", "expense_type_name as label"],
		order_by="name asc",
	)
	return types


@frappe.whitelist(methods=["POST"])
def create_expense_claim(
	employee: str | None = None,
	expenses: str | list | None = None,
	remark: str | None = None,
	company: str | None = None,
) -> dict:
	"""
	Create a new expense claim (in Draft state).

	Args:
		employee: Employee ID (auto-detected if not provided)
		expenses: JSON list of expense items with expense_type, amount, description
		remark: Optional remark
		company: Company (auto-detected if not provided)

	Returns:
		Dict with success flag and claim name
	"""
	if not employee:
		user = frappe.session.user
		employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
		if not employee:
			frappe.throw(_("No Employee record found for current user."))

	if not company:
		company = frappe.db.get_value("Employee", employee, "company")
	if not company:
		company = frappe.db.get_single_value("Global Defaults", "default_company")

	expenses_list = frappe.parse_json(expenses) if isinstance(expenses, str) else expenses
	if not expenses_list:
		frappe.throw(_("At least one expense item is required."))

	try:
		claim = frappe.new_doc("Expense Claim")
		claim.employee = employee
		claim.company = company
		claim.remark = remark or ""
		claim.posting_date = today()

		for exp in expenses_list:
			if not exp.get("expense_type"):
				frappe.throw(_("Expense type is required for each item."))
			amount = flt(exp.get("amount", 0))
			if amount <= 0:
				frappe.throw(_("Expense amount must be greater than zero."))

			claim.append(
				"expenses",
				{
					"expense_type": exp.get("expense_type"),
					"description": exp.get("description", ""),
					"amount": amount,
					"sanctioned_amount": amount,
				},
			)

		claim.insert(ignore_permissions=True)

		return {
			"success": True,
			"name": claim.name,
			"status": claim.status,
			"message": _("Expense Claim {0} created successfully.").format(claim.name),
		}
	except Exception as e:
		frappe.db.rollback()
		frappe.log_error("Expense Claim Creation Failed", frappe.get_traceback())
		frappe.throw(_("Failed to create expense claim: {0}").format(str(e)))


@frappe.whitelist(methods=["POST"])
def submit_expense_claim(name: str) -> dict:
	"""
	Submit an expense claim for approval.

	Args:
		name: Expense Claim document name

	Returns:
		Dict with success flag and updated status
	"""
	if not name or not frappe.db.exists("Expense Claim", name):
		frappe.throw(_("Expense Claim '{0}' not found.").format(name))

	doc = frappe.get_doc("Expense Claim", name)

	if doc.docstatus != 0:
		frappe.throw(_("Only draft claims can be submitted."))

	user_employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
	if doc.employee != user_employee:
		frappe.throw(_("You can only submit your own expense claims."))

	try:
		doc.submit()
		return {
			"success": True,
			"name": doc.name,
			"status": doc.status,
			"message": _("Expense Claim {0} submitted for approval.").format(doc.name),
		}
	except Exception as e:
		frappe.db.rollback()
		frappe.log_error("Expense Claim Submission Failed", frappe.get_traceback())
		frappe.throw(_("Failed to submit expense claim: {0}").format(str(e)))
