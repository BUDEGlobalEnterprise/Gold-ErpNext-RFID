import frappe

from zevar_core.api.layaway import create_layaway


def test():
	frappe.set_user("Administrator")
	try:
		create_layaway(
			customer="MARIA CASTRO",
			items='[{"item_code":"ZEV-BRA-0099","item_name":"14K Rose Gold Chain Bracelet 7\\"","qty":1,"rate":100}]',
			deposit_amount=200.0,  # Deposit > Total will cause balance to be negative
			duration_months=6,
			warehouse="Store 3 - Chicago - ZJ",
		)
	except Exception as e:
		print("EXCEPTION:", type(e), str(e))
		if hasattr(frappe.local, "message_log"):
			print("MESSAGE LOG:", frappe.local.message_log)
