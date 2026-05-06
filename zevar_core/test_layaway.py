import frappe

from zevar_core.api.layaway import create_layaway


def test():
	frappe.set_user("Administrator")
	try:
		create_layaway(
			customer="MARIA CASTRO",
			items='[{"item_code":"ZEV-BRA-0099","item_name":"14K Rose Gold Chain Bracelet 7\\"","qty":1,"rate":1487.03}]',
			deposit_amount=164.0,
			duration_months=6,
			warehouse="Store 3 - Chicago - ZJ",
			notes="Address: 152 N MEADOW DR, CORTLAND, IL 60112",
			terms_accepted=1,
			customer_contact=None,
			customer_email=None,
			payments='[{"mode_of_payment":"Cash","amount":164}]',
		)
	except Exception as e:
		print("EXCEPTION:", type(e), str(e))
		import traceback

		traceback.print_exc()
