"""
Agent Tools - Functional capabilities for Zev AI.
Provides whitelisted functions that Zev can call to perform actions.
"""

from datetime import datetime

import frappe
from frappe import _
from frappe.utils import sanitize_html, validate_json_type

# Tool Registry - Explicit list of functions allowed to be called by the LLM
AGENT_TOOLS = ["create_task", "send_agent_email", "get_daily_summary"]


@frappe.whitelist(allow_guest=False)
def create_task(
	description: str, assigned_to: str | None = None, priority: str = "Medium", date: str | None = None
) -> dict:
	"""Create a ToDo in Frappe and assign it to a user.

	Args:
	    description: The task description.
	    assigned_to: User ID (email) to assign the task to. Defaults to current user.
	    priority: Low, Medium, or High.
	    date: Optional due date (YYYY-MM-DD).
	"""
	# Security: Ensure recipient exists
	target_user = assigned_to or frappe.session.user
	if not frappe.db.exists("User", target_user):
		return {"status": "error", "message": f"User '{target_user}' does not exist."}

	# Security: Allow Retail roles (Sales/POS) or System Managers to assign tasks
	roles = frappe.get_roles()
	if target_user != frappe.session.user:
		retail_roles = ["System Manager", "Sales User", "POS User", "Sales Manager"]
		if not any(r in roles for r in retail_roles):
			frappe.throw(
				_("You do not have permission to assign tasks to other users."), frappe.PermissionError
			)

	# Date validation
	task_date = date
	if task_date:
		try:
			datetime.strptime(task_date, "%Y-%m-%d")
		except ValueError:
			return {"status": "error", "message": f"Invalid date format: '{task_date}'. Use YYYY-MM-DD."}
	else:
		task_date = datetime.now().strftime("%Y-%m-%d")

	try:
		todo = frappe.get_doc(
			{
				"doctype": "ToDo",
				"description": sanitize_html(description),
				"allocated_to": target_user,
				"priority": priority,
				"date": task_date,
				"status": "Open",
			}
		)
		todo.insert(ignore_permissions=False)
		return {
			"status": "success",
			"message": f"Task created and assigned to {todo.allocated_to}",
			"todo_id": todo.name,
		}
	except Exception as e:
		frappe.log_error(f"Zev Tool Error (create_task): {e}")
		return {"status": "error", "message": str(e)}


@frappe.whitelist(allow_guest=False)
def send_agent_email(recipient: str, subject: str, message: str) -> dict:
	"""Send an email on behalf of the assistant.

	Args:
	    recipient: Email address of the recipient.
	    subject: Subject of the email.
	    message: The email body.
	"""
	# Security: Validate recipient
	if not recipient or "@" not in recipient:
		return {"status": "error", "message": "Invalid recipient email address."}

	# Security: Ensure user has permission to send email
	roles = frappe.get_roles()
	if not any(r in roles for r in ["System Manager", "Sales User", "POS User"]):
		frappe.throw(
			_("You do not have permission to send emails through the assistant."), frappe.PermissionError
		)

	try:
		frappe.sendmail(
			recipients=[recipient], subject=sanitize_html(subject), content=sanitize_html(message), now=True
		)
		return {"status": "success", "message": f"Email sent to {recipient}"}
	except Exception as e:
		frappe.log_error(f"Zev Tool Error (send_agent_email): {e}")
		return {"status": "error", "message": str(e)}


@frappe.whitelist(allow_guest=False)
def get_daily_summary(date: str | None = None) -> dict:
	"""Prepare a summary of today's retail operations.

	Args:
	    date: Optional date to summarize (YYYY-MM-DD). Defaults to today.
	"""
	# Security: Requires access to view sales data
	if not frappe.has_permission("POS Invoice", "read"):
		frappe.throw(_("You do not have permission to view daily sales summaries."), frappe.PermissionError)

	target_date = date
	if target_date:
		try:
			datetime.strptime(target_date, "%Y-%m-%d")
		except ValueError:
			return {"status": "error", "message": f"Invalid date format: '{target_date}'. Use YYYY-MM-DD."}
	else:
		target_date = datetime.now().strftime("%Y-%m-%d")

	try:
		# Sales Summary using Query Builder
		pos_invoice = frappe.qb.DocType("POS Invoice")
		sales_query = (
			frappe.qb.from_(pos_invoice)
			.select(
				frappe.qb.fn.Count(pos_invoice.name).as_("count"),
				frappe.qb.fn.Sum(pos_invoice.grand_total).as_("total"),
				frappe.qb.fn.Sum(pos_invoice.total_qty).as_("qty"),
			)
			.where((pos_invoice.posting_date == target_date) & (pos_invoice.docstatus == 1))
		)
		sales_result = sales_query.run(as_dict=True)
		sales = sales_result[0] if sales_result else {"count": 0, "total": 0, "qty": 0}

		# Repair Summary using Query Builder
		repair_order = frappe.qb.DocType("Repair Order")
		repair_query = (
			frappe.qb.from_(repair_order)
			.select(
				frappe.qb.fn.Count(repair_order.name).as_("count"),
				frappe.qb.fn.Sum(repair_order.grand_total).as_("total"),
			)
			.where((repair_order.posting_date == target_date) & (repair_order.docstatus == 1))
		)
		repair_result = repair_query.run(as_dict=True)
		repairs = repair_result[0] if repair_result else {"count": 0, "total": 0}

		# Payment Splits
		payment = frappe.qb.DocType("Sales Invoice Payment")
		payment_query = (
			frappe.qb.from_(payment)
			.join(pos_invoice)
			.on(payment.parent == pos_invoice.name)
			.select(payment.mode_of_payment, frappe.qb.fn.Sum(payment.amount).as_("amount"))
			.where((pos_invoice.posting_date == target_date) & (pos_invoice.docstatus == 1))
			.groupby(payment.mode_of_payment)
		)
		payments = payment_query.run(as_dict=True)

		# Build formatted summary message
		msg = f"Daily Summary for {target_date}:\n"
		msg += f"- Sales: {sales.get('count') or 0} orders (${float(sales.get('total') or 0):,.2f})\n"
		msg += f"- Repairs: {repairs.get('count') or 0} orders (${float(repairs.get('total') or 0):,.2f})\n"
		msg += "- Payments:\n"
		for p in payments:
			msg += f"  * {p.mode_of_payment}: ${float(p.amount or 0):,.2f}\n"

		return {
			"status": "success",
			"message": msg,
			"data": {"date": target_date, "sales": sales, "repairs": repairs, "payments": payments},
		}
	except Exception as e:
		frappe.log_error(f"Zev Tool Error (get_daily_summary): {e}")
		return {"status": "error", "message": str(e)}
