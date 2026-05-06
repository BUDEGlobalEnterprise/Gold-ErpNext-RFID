import frappe

from zevar_core.api.layaway import create_layaway


def run():
	try:
		# Use an existing customer
		customer = frappe.db.get_list("Customer", limit=1)[0].name

		# Give them a phone
		frappe.db.set_value("Customer", customer, "mobile_no", "555-1234")

		# Find an item
		item = frappe.db.get_list("Item", limit=1)[0].name

		# Create payload
		items = [{"item_code": item, "qty": 1, "rate": 100}]

		print(f"Creating layaway for {customer} with item {item}...")

		res = create_layaway(
			customer=customer,
			items=items,
			deposit_amount=20,
			duration_months=3,
			payments=[{"mode_of_payment": "Cash", "amount": 20}],
		)

		print("Success:", res)

	except Exception as e:
		print("Error:", type(e).__name__, str(e))
		print(frappe.get_traceback())
