# Copyright (c) 2026, Zevar Core and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, getdate, today


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters or {})
	return columns, data


def get_columns():
	return [
		{
			"fieldname": "account",
			"label": _("Finance Account"),
			"fieldtype": "Link",
			"options": "In-House Finance Account",
			"width": 150,
		},
		{
			"fieldname": "customer",
			"label": _("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
			"width": 150,
		},
		{"fieldname": "customer_name", "label": _("Customer Name"), "fieldtype": "Data", "width": 160},
		{"fieldname": "total_balance", "label": _("Total Balance"), "fieldtype": "Currency", "width": 120},
		{"fieldname": "current", "label": _("Current"), "fieldtype": "Currency", "width": 100},
		{"fieldname": "age_1_30", "label": _("1-30 Days"), "fieldtype": "Currency", "width": 100},
		{"fieldname": "age_31_60", "label": _("31-60 Days"), "fieldtype": "Currency", "width": 100},
		{"fieldname": "age_61_90", "label": _("61-90 Days"), "fieldtype": "Currency", "width": 100},
		{"fieldname": "age_91_120", "label": _("91-120 Days"), "fieldtype": "Currency", "width": 110},
		{"fieldname": "age_121_180", "label": _("121-180 Days"), "fieldtype": "Currency", "width": 110},
		{"fieldname": "age_181_240", "label": _("181-240 Days"), "fieldtype": "Currency", "width": 110},
		{"fieldname": "age_240_plus", "label": _("240+ Days"), "fieldtype": "Currency", "width": 100},
		{"fieldname": "status", "label": _("Account Status"), "fieldtype": "Data", "width": 90},
		{"fieldname": "interest_rate", "label": _("APR %"), "fieldtype": "Percent", "width": 70},
	]


def get_data(filters):
	today_date = getdate(filters.get("as_of_date") or today())

	# Fetch active finance accounts
	conditions = "WHERE fa.docstatus < 2"
	values: dict = {}

	if filters.get("customer"):
		conditions += " AND fa.customer = %(customer)s"
		values["customer"] = filters["customer"]

	if filters.get("status"):
		conditions += " AND fa.status = %(status)s"
		values["status"] = filters["status"]

	accounts = frappe.db.sql(
		f"""
		SELECT fa.name AS account, fa.customer, fa.status, fa.interest_rate,
		       c.customer_name
		FROM `tabIn-House Finance Account` fa
		LEFT JOIN `tabCustomer` c ON fa.customer = c.name
		{conditions}
		ORDER BY fa.current_balance DESC
		""",
		values=values,
		as_dict=True,
	)

	result = []
	totals = {
		"total_balance": 0,
		"current": 0,
		"age_1_30": 0,
		"age_31_60": 0,
		"age_61_90": 0,
		"age_91_120": 0,
		"age_121_180": 0,
		"age_181_240": 0,
		"age_240_plus": 0,
	}

	for acct in accounts:
		# Get all ledger entries for this account
		entries = frappe.get_all(
			"Customer Ledger Entry",
			filters={"parent": acct.account, "parenttype": "In-House Finance Account"},
			fields=["entry_date", "entry_type", "debit", "credit"],
			order_by="entry_date asc, idx asc",
		)

		buckets = {
			"current": 0,
			"age_1_30": 0,
			"age_31_60": 0,
			"age_61_90": 0,
			"age_91_120": 0,
			"age_121_180": 0,
			"age_181_240": 0,
			"age_240_plus": 0,
		}

		running_balance = 0.0

		for entry in entries:
			debit = flt(entry.debit)
			credit = flt(entry.credit)

			if debit > 0:
				running_balance += debit
				days = (today_date - getdate(entry.entry_date)).days
				if days <= 0:
					buckets["current"] += debit
				elif days <= 30:
					buckets["age_1_30"] += debit
				elif days <= 60:
					buckets["age_31_60"] += debit
				elif days <= 90:
					buckets["age_61_90"] += debit
				elif days <= 120:
					buckets["age_91_120"] += debit
				elif days <= 180:
					buckets["age_121_180"] += debit
				elif days <= 240:
					buckets["age_181_240"] += debit
				else:
					buckets["age_240_plus"] += debit

			if credit > 0:
				running_balance -= credit
				# Credits reduce oldest buckets first (FIFO)
				remaining_credit = credit
				for bucket_key in [
					"age_240_plus",
					"age_181_240",
					"age_121_180",
					"age_91_120",
					"age_61_90",
					"age_31_60",
					"age_1_30",
					"current",
				]:
					if remaining_credit <= 0:
						break
					reduction = min(buckets[bucket_key], remaining_credit)
					buckets[bucket_key] -= reduction
					remaining_credit -= reduction

		total = sum(buckets.values())
		if total <= 0 and not filters.get("show_zero"):
			continue

		row = {
			"account": acct.account,
			"customer": acct.customer,
			"customer_name": acct.customer_name,
			"total_balance": total,
			**buckets,
			"status": acct.status,
			"interest_rate": flt(acct.interest_rate),
		}
		result.append(row)

		for key in totals:
			totals[key] += row.get(key, 0)

	# Totals row
	if len(result) > 1:
		result.append(
			{
				"account": None,
				"customer": None,
				"customer_name": _("** TOTAL **"),
				"total_balance": totals["total_balance"],
				"current": totals["current"],
				"age_1_30": totals["age_1_30"],
				"age_31_60": totals["age_31_60"],
				"age_61_90": totals["age_61_90"],
				"age_91_120": totals["age_91_120"],
				"age_121_180": totals["age_121_180"],
				"age_181_240": totals["age_181_240"],
				"age_240_plus": totals["age_240_plus"],
			}
		)

	return result
