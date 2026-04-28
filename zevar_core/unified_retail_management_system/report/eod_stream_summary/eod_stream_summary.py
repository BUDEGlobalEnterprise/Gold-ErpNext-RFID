import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
	columns = [
		{"fieldname": "stream", "label": _("Transaction Stream"), "fieldtype": "Data", "width": 150},
		{"fieldname": "transaction_count", "label": _("Transactions"), "fieldtype": "Int", "width": 120},
		{"fieldname": "total_amount", "label": _("Total Amount"), "fieldtype": "Currency", "width": 130},
	]

	filters = filters or {}
	from_date = filters.get("from_date") or frappe.utils.today()
	to_date = filters.get("to_date") or frappe.utils.today()

	company = filters.get("company") or frappe.defaults.get_user_default("Company")

	# Jewelry Sales
	jewelry_sales = frappe.db.sql(
		"""
		SELECT COUNT(name) as cnt, SUM(grand_total) as total
		FROM `tabSales Invoice`
		WHERE docstatus = 1 AND is_pos = 1
		AND custom_transaction_stream = 'Jewelry Sale'
		AND posting_date BETWEEN %(from_date)s AND %(to_date)s
		AND company = %(company)s
	""",
		{"from_date": from_date, "to_date": to_date, "company": company},
		as_dict=1,
	)[0]

	# Repairs
	repairs = frappe.db.sql(
		"""
		SELECT COUNT(name) as cnt, SUM(grand_total) as total
		FROM `tabSales Invoice`
		WHERE docstatus = 1 AND is_pos = 1
		AND custom_transaction_stream = 'Repair'
		AND posting_date BETWEEN %(from_date)s AND %(to_date)s
		AND company = %(company)s
	""",
		{"from_date": from_date, "to_date": to_date, "company": company},
		as_dict=1,
	)[0]

	# Layaway Deposits (Payment Entries to Liability Account)
	layaway_deposits = frappe.db.sql(
		"""
		SELECT COUNT(name) as cnt, SUM(paid_amount) as total
		FROM `tabPayment Entry`
		WHERE docstatus = 1 AND payment_type = 'Receive'
		AND paid_from LIKE 'Liability — Layaway Deposits Held%'
		AND posting_date BETWEEN %(from_date)s AND %(to_date)s
		AND company = %(company)s
	""",
		{"from_date": from_date, "to_date": to_date, "company": company},
		as_dict=1,
	)[0]

	data = [
		{
			"stream": "Jewelry Sales",
			"transaction_count": jewelry_sales.get("cnt", 0) or 0,
			"total_amount": flt(jewelry_sales.get("total", 0)),
		},
		{
			"stream": "Repairs",
			"transaction_count": repairs.get("cnt", 0) or 0,
			"total_amount": flt(repairs.get("total", 0)),
		},
		{
			"stream": "Layaway Deposits",
			"transaction_count": layaway_deposits.get("cnt", 0) or 0,
			"total_amount": flt(layaway_deposits.get("total", 0)),
		},
	]

	return columns, data
