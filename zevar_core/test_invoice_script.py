import traceback

import frappe

from zevar_core.api.pos import _create_pos_invoice_internal


def run():
	frappe.session.user = "Administrator"
	items = [{"item_code": "GOLD-CHAIN-10K", "qty": 1, "rate": 810.87}]
	payments = [{"mode_of_payment": "Cash", "amount": 810.87}]
	try:
		res = _create_pos_invoice_internal(
			items=frappe.as_json(items),
			payments=frappe.as_json(payments),
			customer="Akshay",
			warehouse="Main Store - ZC",
			tax_exempt=True,
		)
		print("SUCCESS:", res)
	except Exception as e:
		print("ERROR_CAUGHT:", str(e))
		traceback.print_exc()
