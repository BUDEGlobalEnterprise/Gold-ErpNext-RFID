import frappe
from frappe.utils import date_diff, flt, today


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{
			"fieldname": "financier",
			"label": "Financier",
			"fieldtype": "Data",
			"width": 150,
		},
		{
			"fieldname": "todays_charges",
			"label": "Today's Charges",
			"fieldtype": "Currency",
			"width": 150,
		},
		{
			"fieldname": "cumulative_ar",
			"label": "Cumulative Unsettled A/R",
			"fieldtype": "Currency",
			"width": 200,
		},
		{
			"fieldname": "days_since_oldest",
			"label": "Days Since Oldest Unsettled",
			"fieldtype": "Int",
			"width": 200,
		},
	]


def get_data(filters):
	financiers = ["Synchrony", "AFF", "CIMA", "Progressive", "Snap"]
	data = []

	for financier in financiers:
		account = f"Asset — A/R {financier} - ZJ"

		# Todays charges
		todays_debit = frappe.db.sql(
			"""
			SELECT SUM(debit)
			FROM `tabGL Entry`
			WHERE account=%s AND posting_date=%s AND is_cancelled=0
		""",
			(account, today()),
		)
		todays_charges = flt(todays_debit[0][0]) if todays_debit and todays_debit[0][0] else 0.0

		# Cumulative A/R
		bal = frappe.db.sql(
			"""
			SELECT SUM(debit) - SUM(credit)
			FROM `tabGL Entry`
			WHERE account=%s AND is_cancelled=0
		""",
			(account,),
		)
		cumulative_ar = flt(bal[0][0]) if bal and bal[0][0] else 0.0

		# Oldest unsettled
		days_since = 0
		if cumulative_ar > 0:
			oldest_entry = frappe.db.sql(
				"""
				SELECT posting_date
				FROM `tabGL Entry`
				WHERE account=%s AND debit > 0 AND is_cancelled=0
				ORDER BY posting_date ASC
				LIMIT 1
			""",
				(account,),
			)
			if oldest_entry and oldest_entry[0][0]:
				days_since = date_diff(today(), oldest_entry[0][0])

		data.append(
			{
				"financier": financier,
				"todays_charges": todays_charges,
				"cumulative_ar": cumulative_ar,
				"days_since_oldest": days_since,
			}
		)

	return data
